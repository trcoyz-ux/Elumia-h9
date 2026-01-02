from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User, DoctorProfile, Consultation, DoctorReview
from functools import wraps
import redis
import json
import hashlib
from datetime import datetime, timedelta
import time
import threading
from collections import defaultdict

performance_cache_bp = Blueprint('performance_cache', __name__)

# إعداد Redis للتخزين المؤقت
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    # استخدام ذاكرة محلية كبديل
    local_cache = {}
    cache_timestamps = {}

# إعدادات التخزين المؤقت
CACHE_SETTINGS = {
    'doctors_list': {'ttl': 300, 'key': 'doctors:list'},  # 5 دقائق
    'doctor_profile': {'ttl': 600, 'key': 'doctor:profile:{}'},  # 10 دقائق
    'consultations_stats': {'ttl': 180, 'key': 'stats:consultations'},  # 3 دقائق
    'reviews_stats': {'ttl': 300, 'key': 'stats:reviews'},  # 5 دقائق
    'popular_doctors': {'ttl': 900, 'key': 'doctors:popular'},  # 15 دقيقة
    'search_results': {'ttl': 120, 'key': 'search:{}'},  # 2 دقيقة
}

# متغيرات مراقبة الأداء
performance_metrics = defaultdict(list)
request_times = defaultdict(list)

def cache_key_generator(prefix, *args, **kwargs):
    """إنشاء مفتاح فريد للتخزين المؤقت"""
    key_data = f"{prefix}:{':'.join(map(str, args))}"
    if kwargs:
        key_data += f":{hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
    return key_data

def get_from_cache(key):
    """الحصول على البيانات من التخزين المؤقت"""
    if REDIS_AVAILABLE:
        try:
            data = redis_client.get(key)
            return json.loads(data) if data else None
        except:
            return None
    else:
        # استخدام الذاكرة المحلية
        if key in local_cache:
            timestamp = cache_timestamps.get(key, 0)
            if time.time() - timestamp < 300:  # 5 دقائق افتراضي
                return local_cache[key]
            else:
                del local_cache[key]
                del cache_timestamps[key]
        return None

def set_to_cache(key, data, ttl=300):
    """حفظ البيانات في التخزين المؤقت"""
    if REDIS_AVAILABLE:
        try:
            redis_client.setex(key, ttl, json.dumps(data, default=str))
        except:
            pass
    else:
        # استخدام الذاكرة المحلية
        local_cache[key] = data
        cache_timestamps[key] = time.time()

def invalidate_cache(pattern):
    """إلغاء التخزين المؤقت للمفاتيح المطابقة للنمط"""
    if REDIS_AVAILABLE:
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
        except:
            pass
    else:
        # إلغاء من الذاكرة المحلية
        keys_to_delete = [k for k in local_cache.keys() if pattern.replace('*', '') in k]
        for key in keys_to_delete:
            if key in local_cache:
                del local_cache[key]
            if key in cache_timestamps:
                del cache_timestamps[key]

def cache_response(cache_type, ttl=None):
    """ديكوريتر للتخزين المؤقت للاستجابات"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # إنشاء مفتاح التخزين المؤقت
            cache_config = CACHE_SETTINGS.get(cache_type, {})
            cache_ttl = ttl or cache_config.get('ttl', 300)
            
            # تضمين معاملات الطلب في المفتاح
            request_args = dict(request.args)
            request_json = request.get_json() if request.is_json else {}
            
            cache_key = cache_key_generator(
                cache_config.get('key', cache_type),
                *args,
                **kwargs,
                **request_args,
                **request_json
            )
            
            # محاولة الحصول على البيانات من التخزين المؤقت
            cached_data = get_from_cache(cache_key)
            if cached_data:
                return jsonify({
                    'status': 'success',
                    'data': cached_data,
                    'cached': True,
                    'cache_key': cache_key
                })
            
            # تنفيذ الدالة الأصلية
            result = f(*args, **kwargs)
            
            # حفظ النتيجة في التخزين المؤقت
            if hasattr(result, 'get_json') and result.status_code == 200:
                response_data = result.get_json()
                if response_data.get('status') == 'success':
                    set_to_cache(cache_key, response_data.get('data'), cache_ttl)
            
            return result
        return decorated_function
    return decorator

def measure_performance(f):
    """ديكوريتر لقياس أداء الدوال"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # تسجيل الأداء
            function_name = f.__name__
            performance_metrics[function_name].append({
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            
            # الاحتفاظ بآخر 100 قياس فقط
            if len(performance_metrics[function_name]) > 100:
                performance_metrics[function_name] = performance_metrics[function_name][-100:]
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            performance_metrics[f.__name__].append({
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
            raise
            
    return decorated_function

@performance_cache_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """إحصائيات التخزين المؤقت"""
    try:
        stats = {
            'redis_available': REDIS_AVAILABLE,
            'cache_type': 'Redis' if REDIS_AVAILABLE else 'Local Memory',
            'total_keys': 0,
            'memory_usage': 0
        }
        
        if REDIS_AVAILABLE:
            try:
                info = redis_client.info()
                stats.update({
                    'total_keys': redis_client.dbsize(),
                    'memory_usage': info.get('used_memory_human', '0B'),
                    'connected_clients': info.get('connected_clients', 0),
                    'uptime': info.get('uptime_in_seconds', 0)
                })
            except:
                pass
        else:
            stats.update({
                'total_keys': len(local_cache),
                'memory_usage': f"{len(str(local_cache))} bytes"
            })
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على إحصائيات التخزين المؤقت: {str(e)}'
        }), 500

@performance_cache_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """مسح التخزين المؤقت"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '*')
        
        if REDIS_AVAILABLE:
            if pattern == '*':
                redis_client.flushdb()
            else:
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
        else:
            if pattern == '*':
                local_cache.clear()
                cache_timestamps.clear()
            else:
                keys_to_delete = [k for k in local_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    if key in local_cache:
                        del local_cache[key]
                    if key in cache_timestamps:
                        del cache_timestamps[key]
        
        return jsonify({
            'status': 'success',
            'message': 'تم مسح التخزين المؤقت بنجاح'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في مسح التخزين المؤقت: {str(e)}'
        }), 500

@performance_cache_bp.route('/performance/stats', methods=['GET'])
def get_performance_stats():
    """إحصائيات الأداء"""
    try:
        stats = {}
        
        for function_name, metrics in performance_metrics.items():
            if metrics:
                execution_times = [m['execution_time'] for m in metrics if m['success']]
                if execution_times:
                    stats[function_name] = {
                        'total_calls': len(metrics),
                        'successful_calls': len(execution_times),
                        'failed_calls': len(metrics) - len(execution_times),
                        'avg_execution_time': sum(execution_times) / len(execution_times),
                        'min_execution_time': min(execution_times),
                        'max_execution_time': max(execution_times),
                        'last_call': metrics[-1]['timestamp']
                    }
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على إحصائيات الأداء: {str(e)}'
        }), 500

@performance_cache_bp.route('/performance/slow-queries', methods=['GET'])
def get_slow_queries():
    """الاستعلامات البطيئة"""
    try:
        slow_threshold = float(request.args.get('threshold', 1.0))  # ثانية واحدة افتراضياً
        
        slow_queries = []
        for function_name, metrics in performance_metrics.items():
            for metric in metrics:
                if metric['success'] and metric['execution_time'] > slow_threshold:
                    slow_queries.append({
                        'function': function_name,
                        'execution_time': metric['execution_time'],
                        'timestamp': metric['timestamp']
                    })
        
        # ترتيب حسب وقت التنفيذ
        slow_queries.sort(key=lambda x: x['execution_time'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'slow_queries': slow_queries[:50],  # أبطأ 50 استعلام
                'threshold': slow_threshold,
                'total_slow_queries': len(slow_queries)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على الاستعلامات البطيئة: {str(e)}'
        }), 500

# تطبيق التخزين المؤقت على الدوال الحالية
@performance_cache_bp.route('/doctors/cached', methods=['GET'])
@cache_response('doctors_list')
@measure_performance
def get_cached_doctors():
    """الحصول على قائمة الأطباء مع التخزين المؤقت"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        specialization = request.args.get('specialization')
        
        query = Doctor.query.filter(Doctor.is_verified == True)
        
        if specialization:
            query = query.filter(Doctor.specialization == specialization)
        
        doctors = query.paginate(page=page, per_page=per_page, error_out=False)
        
        doctors_data = []
        for doctor in doctors.items:
            doctors_data.append({
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization,
                'rating': doctor.rating,
                'experience_years': doctor.experience_years,
                'consultation_price': doctor.consultation_price,
                'is_available': doctor.is_available,
                'profile_image': doctor.profile_image
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'doctors': doctors_data,
                'pagination': {
                    'page': doctors.page,
                    'pages': doctors.pages,
                    'per_page': doctors.per_page,
                    'total': doctors.total
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على قائمة الأطباء: {str(e)}'
        }), 500

@performance_cache_bp.route('/stats/cached', methods=['GET'])
@cache_response('consultations_stats')
@measure_performance
def get_cached_stats():
    """إحصائيات مخزنة مؤقتاً"""
    try:
        # إحصائيات الاستشارات
        total_consultations = Consultation.query.count()
        completed_consultations = Consultation.query.filter(Consultation.status == 'completed').count()
        ongoing_consultations = Consultation.query.filter(Consultation.status == 'ongoing').count()
        
        # إحصائيات الأطباء
        total_doctors = Doctor.query.count()
        verified_doctors = Doctor.query.filter(Doctor.is_verified == True).count()
        available_doctors = Doctor.query.filter(Doctor.is_available == True).count()
        
        # إحصائيات المستخدمين
        total_users = User.query.count()
        patients = User.query.filter(User.user_type == 'patient').count()
        
        stats = {
            'consultations': {
                'total': total_consultations,
                'completed': completed_consultations,
                'ongoing': ongoing_consultations,
                'completion_rate': (completed_consultations / total_consultations * 100) if total_consultations > 0 else 0
            },
            'doctors': {
                'total': total_doctors,
                'verified': verified_doctors,
                'available': available_doctors,
                'verification_rate': (verified_doctors / total_doctors * 100) if total_doctors > 0 else 0
            },
            'users': {
                'total': total_users,
                'patients': patients
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على الإحصائيات: {str(e)}'
        }), 500

# دالة لتنظيف التخزين المؤقت المنتهي الصلاحية
def cleanup_expired_cache():
    """تنظيف التخزين المؤقت المنتهي الصلاحية"""
    if not REDIS_AVAILABLE:
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in cache_timestamps.items():
            if current_time - timestamp > 300:  # 5 دقائق
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in local_cache:
                del local_cache[key]
            if key in cache_timestamps:
                del cache_timestamps[key]

# تشغيل تنظيف التخزين المؤقت كل 5 دقائق
def start_cache_cleanup():
    """بدء عملية تنظيف التخزين المؤقت"""
    def cleanup_worker():
        while True:
            time.sleep(300)  # 5 دقائق
            cleanup_expired_cache()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

# بدء تنظيف التخزين المؤقت عند تحميل الوحدة
start_cache_cleanup()

