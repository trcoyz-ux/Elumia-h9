from flask import Blueprint, request, jsonify
from src.models.user import db, User, DoctorProfile, Consultation, DoctorReview
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import re

advanced_search_bp = Blueprint('advanced_search', __name__)

@advanced_search_bp.route('/search', methods=['POST'])
def advanced_search():
    """البحث المتقدم عبر جميع الأقسام"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'all')  # all, doctors, patients, consultations, reviews
        filters = data.get('filters', {})
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'يرجى إدخال كلمة البحث'
            }), 400
        
        results = {}
        
        # البحث في الأطباء
        if search_type in ['all', 'doctors']:
            doctors_query = Doctor.query.filter(
                or_(
                    Doctor.name.contains(query),
                    Doctor.specialization.contains(query),
                    Doctor.bio.contains(query),
                    Doctor.qualifications.contains(query)
                )
            )
            
            # تطبيق الفلاتر
            if filters.get('specialization'):
                doctors_query = doctors_query.filter(Doctor.specialization == filters['specialization'])
            
            if filters.get('min_rating'):
                doctors_query = doctors_query.filter(Doctor.rating >= float(filters['min_rating']))
            
            if filters.get('min_experience'):
                doctors_query = doctors_query.filter(Doctor.experience_years >= int(filters['min_experience']))
            
            if filters.get('verified_only'):
                doctors_query = doctors_query.filter(Doctor.is_verified == True)
            
            doctors = doctors_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            results['doctors'] = {
                'items': [{
                    'id': doctor.id,
                    'name': doctor.name,
                    'specialization': doctor.specialization,
                    'rating': doctor.rating,
                    'experience_years': doctor.experience_years,
                    'consultation_price': doctor.consultation_price,
                    'is_verified': doctor.is_verified,
                    'is_available': doctor.is_available,
                    'profile_image': doctor.profile_image,
                    'languages': doctor.languages.split(',') if doctor.languages else []
                } for doctor in doctors.items],
                'total': doctors.total,
                'pages': doctors.pages,
                'current_page': doctors.page
            }
        
        # البحث في المرضى
        if search_type in ['all', 'patients']:
            patients_query = User.query.filter(
                and_(
                    User.user_type == 'patient',
                    or_(
                        User.full_name.contains(query),
                        User.email.contains(query),
                        User.phone.contains(query)
                    )
                )
            )
            
            # تطبيق الفلاتر
            if filters.get('age_range'):
                age_min, age_max = map(int, filters['age_range'].split('-'))
                patients_query = patients_query.filter(
                    and_(User.age >= age_min, User.age <= age_max)
                )
            
            if filters.get('gender'):
                patients_query = patients_query.filter(User.gender == filters['gender'])
            
            patients = patients_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            results['patients'] = {
                'items': [{
                    'id': patient.id,
                    'name': patient.full_name,
                    'email': patient.email,
                    'phone': patient.phone,
                    'age': patient.age,
                    'gender': patient.gender,
                    'created_at': patient.created_at.isoformat() if patient.created_at else None
                } for patient in patients.items],
                'total': patients.total,
                'pages': patients.pages,
                'current_page': patients.page
            }
        
        # البحث في الاستشارات
        if search_type in ['all', 'consultations']:
            consultations_query = Consultation.query.filter(
                or_(
                    Consultation.symptoms.contains(query),
                    Consultation.diagnosis.contains(query),
                    Consultation.notes.contains(query)
                )
            )
            
            # تطبيق الفلاتر
            if filters.get('status'):
                consultations_query = consultations_query.filter(Consultation.status == filters['status'])
            
            if filters.get('consultation_type'):
                consultations_query = consultations_query.filter(Consultation.consultation_type == filters['consultation_type'])
            
            if filters.get('date_range'):
                start_date = datetime.strptime(filters['date_range']['start'], '%Y-%m-%d')
                end_date = datetime.strptime(filters['date_range']['end'], '%Y-%m-%d')
                consultations_query = consultations_query.filter(
                    and_(
                        Consultation.created_at >= start_date,
                        Consultation.created_at <= end_date
                    )
                )
            
            consultations = consultations_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            results['consultations'] = {
                'items': [{
                    'id': consultation.id,
                    'patient_name': consultation.patient.full_name if consultation.patient else 'غير محدد',
                    'doctor_name': consultation.doctor.name if consultation.doctor else 'غير محدد',
                    'symptoms': consultation.symptoms,
                    'diagnosis': consultation.diagnosis,
                    'status': consultation.status,
                    'consultation_type': consultation.consultation_type,
                    'created_at': consultation.created_at.isoformat() if consultation.created_at else None,
                    'amount': consultation.amount
                } for consultation in consultations.items],
                'total': consultations.total,
                'pages': consultations.pages,
                'current_page': consultations.page
            }
        
        # البحث في المراجعات
        if search_type in ['all', 'reviews']:
            reviews_query = Review.query.filter(
                or_(
                    Review.comment.contains(query),
                    Review.doctor.has(Doctor.name.contains(query)),
                    Review.patient.has(User.full_name.contains(query))
                )
            )
            
            # تطبيق الفلاتر
            if filters.get('min_rating'):
                reviews_query = reviews_query.filter(Review.rating >= int(filters['min_rating']))
            
            if filters.get('verified_only'):
                reviews_query = reviews_query.filter(Review.is_verified == True)
            
            reviews = reviews_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            results['reviews'] = {
                'items': [{
                    'id': review.id,
                    'patient_name': review.patient.full_name if review.patient else 'غير محدد',
                    'doctor_name': review.doctor.name if review.doctor else 'غير محدد',
                    'rating': review.rating,
                    'comment': review.comment,
                    'is_verified': review.is_verified,
                    'created_at': review.created_at.isoformat() if review.created_at else None
                } for review in reviews.items],
                'total': reviews.total,
                'pages': reviews.pages,
                'current_page': reviews.page
            }
        
        return jsonify({
            'status': 'success',
            'data': results,
            'query': query,
            'search_type': search_type,
            'total_results': sum([r.get('total', 0) for r in results.values()])
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في البحث: {str(e)}'
        }), 500

@advanced_search_bp.route('/suggestions', methods=['GET'])
def search_suggestions():
    """اقتراحات البحث التلقائية"""
    try:
        query = request.args.get('q', '').strip()
        
        if len(query) < 2:
            return jsonify({
                'status': 'success',
                'data': []
            })
        
        suggestions = []
        
        # اقتراحات من أسماء الأطباء
        doctors = Doctor.query.filter(
            Doctor.name.contains(query)
        ).limit(5).all()
        
        for doctor in doctors:
            suggestions.append({
                'type': 'doctor',
                'text': doctor.name,
                'subtitle': doctor.specialization,
                'id': doctor.id
            })
        
        # اقتراحات من التخصصات
        specializations = db.session.query(Doctor.specialization).filter(
            Doctor.specialization.contains(query)
        ).distinct().limit(5).all()
        
        for spec in specializations:
            suggestions.append({
                'type': 'specialization',
                'text': spec[0],
                'subtitle': 'تخصص طبي',
                'id': None
            })
        
        # اقتراحات من الأعراض الشائعة
        common_symptoms = [
            'صداع', 'حمى', 'سعال', 'ألم في الصدر', 'ضيق تنفس',
            'ألم في البطن', 'غثيان', 'دوخة', 'ألم في الظهر', 'أرق'
        ]
        
        matching_symptoms = [s for s in common_symptoms if query.lower() in s.lower()]
        for symptom in matching_symptoms[:3]:
            suggestions.append({
                'type': 'symptom',
                'text': symptom,
                'subtitle': 'عرض طبي',
                'id': None
            })
        
        return jsonify({
            'status': 'success',
            'data': suggestions[:10]  # أقصى 10 اقتراحات
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على الاقتراحات: {str(e)}'
        }), 500

@advanced_search_bp.route('/filters', methods=['GET'])
def get_search_filters():
    """الحصول على قائمة الفلاتر المتاحة"""
    try:
        # التخصصات المتاحة
        specializations = db.session.query(Doctor.specialization).distinct().all()
        specializations = [s[0] for s in specializations if s[0]]
        
        # حالات الاستشارات
        consultation_statuses = ['pending', 'ongoing', 'completed', 'cancelled']
        
        # أنواع الاستشارات
        consultation_types = ['video', 'audio', 'text']
        
        # نطاقات الأعمار
        age_ranges = [
            {'label': '18-25', 'value': '18-25'},
            {'label': '26-35', 'value': '26-35'},
            {'label': '36-45', 'value': '36-45'},
            {'label': '46-55', 'value': '46-55'},
            {'label': '56-65', 'value': '56-65'},
            {'label': '65+', 'value': '65-100'}
        ]
        
        # نطاقات التقييم
        rating_ranges = [
            {'label': '5 نجوم', 'value': '5'},
            {'label': '4 نجوم فأكثر', 'value': '4'},
            {'label': '3 نجوم فأكثر', 'value': '3'},
            {'label': '2 نجوم فأكثر', 'value': '2'},
            {'label': 'نجمة واحدة فأكثر', 'value': '1'}
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'specializations': specializations,
                'consultation_statuses': consultation_statuses,
                'consultation_types': consultation_types,
                'age_ranges': age_ranges,
                'rating_ranges': rating_ranges,
                'genders': ['male', 'female']
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على الفلاتر: {str(e)}'
        }), 500

@advanced_search_bp.route('/recent', methods=['GET'])
def get_recent_searches():
    """الحصول على عمليات البحث الأخيرة"""
    try:
        # في التطبيق الحقيقي، يمكن حفظ عمليات البحث في قاعدة البيانات
        # هنا سنعيد قائمة افتراضية
        recent_searches = [
            {'query': 'أطباء القلب', 'timestamp': '2024-01-15T10:30:00'},
            {'query': 'صداع مزمن', 'timestamp': '2024-01-14T15:20:00'},
            {'query': 'د. أحمد محمد', 'timestamp': '2024-01-13T09:45:00'},
            {'query': 'استشارة نفسية', 'timestamp': '2024-01-12T14:10:00'}
        ]
        
        return jsonify({
            'status': 'success',
            'data': recent_searches
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على عمليات البحث الأخيرة: {str(e)}'
        }), 500

@advanced_search_bp.route('/popular', methods=['GET'])
def get_popular_searches():
    """الحصول على عمليات البحث الشائعة"""
    try:
        # قائمة بعمليات البحث الشائعة
        popular_searches = [
            {'query': 'أطباء القلب', 'count': 1250},
            {'query': 'استشارة نفسية', 'count': 980},
            {'query': 'أطباء الأطفال', 'count': 875},
            {'query': 'أمراض جلدية', 'count': 720},
            {'query': 'صداع', 'count': 650},
            {'query': 'ألم في الظهر', 'count': 580},
            {'query': 'استشارة عامة', 'count': 520},
            {'query': 'أطباء العظام', 'count': 480}
        ]
        
        return jsonify({
            'status': 'success',
            'data': popular_searches
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على عمليات البحث الشائعة: {str(e)}'
        }), 500

