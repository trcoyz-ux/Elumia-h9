from flask import Blueprint, request, jsonify
from src.models.user import db, User, Notification
import firebase_admin
from firebase_admin import credentials, messaging
import json
import os
from datetime import datetime, timedelta
import threading
import time

push_notifications_bp = Blueprint("push_notifications", __name__)

# إعداد Firebase Admin SDK
firebase_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'firebase-service-account-corrected.json')

# تهيئة Firebase إذا لم يتم تهيئته مسبقاً
if not firebase_admin._apps:
    try:

        
        # تهيئة Firebase
        cred = credentials.Certificate(firebase_config_path)
        firebase_admin.initialize_app(cred)
        
    except Exception as e:
        print(f"تحذير: لم يتم تهيئة Firebase: {str(e)}")

class NotificationManager:
    """مدير الإشعارات المتقدم"""
    
    def __init__(self):
        self.notification_types = {
            'appointment_reminder': {
                'title': 'تذكير بالموعد',
                'priority': 'high',
                'sound': 'default'
            },
            'consultation_update': {
                'title': 'تحديث الاستشارة',
                'priority': 'high',
                'sound': 'default'
            },
            'prescription_ready': {
                'title': 'الوصفة الطبية جاهزة',
                'priority': 'normal',
                'sound': 'default'
            },
            'test_results': {
                'title': 'نتائج الفحوصات',
                'priority': 'high',
                'sound': 'default'
            },
            'payment_confirmation': {
                'title': 'تأكيد الدفع',
                'priority': 'normal',
                'sound': 'default'
            },
            'doctor_message': {
                'title': 'رسالة من الطبيب',
                'priority': 'high',
                'sound': 'default'
            },
            'system_maintenance': {
                'title': 'صيانة النظام',
                'priority': 'low',
                'sound': 'none'
            }
        }
    
    def send_push_notification(self, user_tokens, notification_type, message, data=None):
        """إرسال إشعار فوري"""
        try:
            if not user_tokens:
                return {"success": False, "error": "لا توجد رموز مستخدمين"}
            
            # إعداد الإشعار
            notification_config = self.notification_types.get(notification_type, {
                'title': 'إشعار',
                'priority': 'normal',
                'sound': 'default'
            })
            
            # إنشاء رسالة الإشعار
            notification = messaging.Notification(
                title=notification_config['title'],
                body=message
            )
            
            # إعداد Android
            android_config = messaging.AndroidConfig(
                priority=notification_config['priority'],
                notification=messaging.AndroidNotification(
                    sound=notification_config['sound'],
                    channel_id='healthcare_notifications'
                )
            )
            
            # إعداد iOS
            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound=notification_config['sound'],
                        badge=1
                    )
                )
            )
            
            # إرسال للمستخدمين المتعددين
            if isinstance(user_tokens, list):
                message_obj = messaging.MulticastMessage(
                    notification=notification,
                    data=data or {},
                    tokens=user_tokens,
                    android=android_config,
                    apns=apns_config
                )
                
                response = messaging.send_multicast(message_obj)
                
                return {
                    "success": True,
                    "success_count": response.success_count,
                    "failure_count": response.failure_count,
                    "responses": [
                        {
                            "success": resp.success,
                            "error": str(resp.exception) if resp.exception else None
                        }
                        for resp in response.responses
                    ]
                }
            else:
                # إرسال لمستخدم واحد
                message_obj = messaging.Message(
                    notification=notification,
                    data=data or {},
                    token=user_tokens,
                    android=android_config,
                    apns=apns_config
                )
                
                response = messaging.send(message_obj)
                
                return {
                    "success": True,
                    "message_id": response
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في إرسال الإشعار: {str(e)}"
            }
    
    def schedule_notification(self, user_tokens, notification_type, message, send_time, data=None):
        """جدولة إشعار للإرسال في وقت محدد"""
        def send_delayed_notification():
            current_time = datetime.now()
            delay = (send_time - current_time).total_seconds()
            
            if delay > 0:
                time.sleep(delay)
                self.send_push_notification(user_tokens, notification_type, message, data)
        
        # تشغيل في خيط منفصل
        thread = threading.Thread(target=send_delayed_notification)
        thread.daemon = True
        thread.start()
        
        return {"success": True, "scheduled_for": send_time.isoformat()}
    
    def send_bulk_notification(self, notification_type, message, user_filter=None, data=None):
        """إرسال إشعار جماعي"""
        try:
            # جلب المستخدمين حسب الفلتر
            query = User.query
            
            if user_filter:
                if user_filter.get('user_type'):
                    query = query.filter_by(user_type=user_filter['user_type'])
                if user_filter.get('is_active'):
                    query = query.filter_by(is_active=user_filter['is_active'])
            
            users = query.all()
            
            # جمع رموز FCM (يجب حفظها في قاعدة البيانات)
            # هذا مثال تجريبي - يجب إضافة جدول لحفظ رموز FCM
            user_tokens = []
            for user in users:
                # في التطبيق الحقيقي، يجب جلب الرمز من قاعدة البيانات
                # user_tokens.append(user.fcm_token)
                pass
            
            if user_tokens:
                result = self.send_push_notification(user_tokens, notification_type, message, data)
                
                # حفظ الإشعار في قاعدة البيانات
                for user in users:
                    notification = Notification(
                        user_id=user.id,
                        message=message,
                        notification_type=notification_type,
                        push_sent=result.get('success', False)
                    )
                    db.session.add(notification)
                
                db.session.commit()
                
                return result
            else:
                return {"success": False, "error": "لا توجد رموز مستخدمين صالحة"}
                
        except Exception as e:
            return {"success": False, "error": f"خطأ في الإرسال الجماعي: {str(e)}"}

# إنشاء مثيل من مدير الإشعارات
notification_manager = NotificationManager()

@push_notifications_bp.route("/register_token", methods=["POST"])
def register_fcm_token():
    """تسجيل رمز FCM للمستخدم"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        fcm_token = data.get('fcm_token')
        device_type = data.get('device_type', 'android')  # android, ios
        
        if not user_id or not fcm_token:
            return jsonify({"message": "معرف المستخدم ورمز FCM مطلوبان"}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "المستخدم غير موجود"}), 404
        
        # في التطبيق الحقيقي، يجب إنشاء جدول منفصل لحفظ رموز FCM
        # لأن المستخدم قد يكون لديه عدة أجهزة
        
        return jsonify({
            "message": "تم تسجيل رمز FCM بنجاح",
            "user_id": user_id,
            "device_type": device_type
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في تسجيل الرمز: {str(e)}"}), 500

@push_notifications_bp.route("/send", methods=["POST"])
def send_notification():
    """إرسال إشعار فوري"""
    try:
        data = request.get_json()
        
        required_fields = ['user_ids', 'notification_type', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        user_ids = data['user_ids']
        notification_type = data['notification_type']
        message = data['message']
        notification_data = data.get('data', {})
        
        # التحقق من صحة نوع الإشعار
        if notification_type not in notification_manager.notification_types:
            return jsonify({"message": "نوع الإشعار غير صحيح"}), 400
        
        # جلب رموز FCM للمستخدمين (تجريبي)
        user_tokens = []  # يجب جلبها من قاعدة البيانات
        
        # إرسال الإشعار
        result = notification_manager.send_push_notification(
            user_tokens, notification_type, message, notification_data
        )
        
        # حفظ الإشعار في قاعدة البيانات
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                message=message,
                notification_type=notification_type,
                push_sent=result.get('success', False)
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            "message": "تم إرسال الإشعار",
            "result": result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في إرسال الإشعار: {str(e)}"}), 500

@push_notifications_bp.route("/schedule", methods=["POST"])
def schedule_notification():
    """جدولة إشعار للإرسال لاحقاً"""
    try:
        data = request.get_json()
        
        required_fields = ['user_ids', 'notification_type', 'message', 'send_time']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        user_ids = data['user_ids']
        notification_type = data['notification_type']
        message = data['message']
        send_time = datetime.fromisoformat(data['send_time'])
        notification_data = data.get('data', {})
        
        # التحقق من أن الوقت في المستقبل
        if send_time <= datetime.now():
            return jsonify({"message": "وقت الإرسال يجب أن يكون في المستقبل"}), 400
        
        # جلب رموز FCM (تجريبي)
        user_tokens = []
        
        # جدولة الإشعار
        result = notification_manager.schedule_notification(
            user_tokens, notification_type, message, send_time, notification_data
        )
        
        # حفظ الإشعار المجدول في قاعدة البيانات
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                message=message,
                notification_type=notification_type,
                timestamp=send_time,
                push_sent=False
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            "message": "تم جدولة الإشعار",
            "result": result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في جدولة الإشعار: {str(e)}"}), 500

@push_notifications_bp.route("/bulk", methods=["POST"])
def send_bulk_notification():
    """إرسال إشعار جماعي"""
    try:
        data = request.get_json()
        
        required_fields = ['notification_type', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        notification_type = data['notification_type']
        message = data['message']
        user_filter = data.get('user_filter', {})
        notification_data = data.get('data', {})
        
        # إرسال الإشعار الجماعي
        result = notification_manager.send_bulk_notification(
            notification_type, message, user_filter, notification_data
        )
        
        return jsonify({
            "message": "تم إرسال الإشعار الجماعي",
            "result": result
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في الإرسال الجماعي: {str(e)}"}), 500

@push_notifications_bp.route("/user/<int:user_id>/notifications", methods=["GET"])
def get_user_notifications(user_id):
    """الحصول على إشعارات المستخدم"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.timestamp.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        notifications_data = []
        for notification in notifications.items:
            notifications_data.append({
                'id': notification.id,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'timestamp': notification.timestamp.isoformat(),
                'is_read': notification.is_read,
                'push_sent': notification.push_sent
            })
        
        return jsonify({
            "notifications": notifications_data,
            "pagination": {
                "page": notifications.page,
                "pages": notifications.pages,
                "per_page": notifications.per_page,
                "total": notifications.total,
                "has_next": notifications.has_next,
                "has_prev": notifications.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب الإشعارات: {str(e)}"}), 500

@push_notifications_bp.route("/notification/<int:notification_id>/read", methods=["POST"])
def mark_notification_read(notification_id):
    """تعليم الإشعار كمقروء"""
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({"message": "الإشعار غير موجود"}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({"message": "تم تعليم الإشعار كمقروء"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في تحديث الإشعار: {str(e)}"}), 500

@push_notifications_bp.route("/user/<int:user_id>/mark_all_read", methods=["POST"])
def mark_all_notifications_read(user_id):
    """تعليم جميع إشعارات المستخدم كمقروءة"""
    try:
        notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
        
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        
        return jsonify({
            "message": f"تم تعليم {len(notifications)} إشعار كمقروء"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في تحديث الإشعارات: {str(e)}"}), 500

@push_notifications_bp.route("/types", methods=["GET"])
def get_notification_types():
    """الحصول على أنواع الإشعارات المتاحة"""
    return jsonify({
        "notification_types": notification_manager.notification_types
    }), 200

@push_notifications_bp.route("/statistics", methods=["GET"])
def get_notification_statistics():
    """إحصائيات الإشعارات"""
    try:
        total_notifications = Notification.query.count()
        unread_notifications = Notification.query.filter_by(is_read=False).count()
        push_sent_count = Notification.query.filter_by(push_sent=True).count()
        
        # إحصائيات حسب النوع
        type_stats = db.session.query(
            Notification.notification_type,
            db.func.count(Notification.id).label('count')
        ).group_by(Notification.notification_type).all()
        
        type_distribution = [
            {"type": type_name, "count": count}
            for type_name, count in type_stats
        ]
        
        return jsonify({
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "push_success_rate": (push_sent_count / total_notifications * 100) if total_notifications > 0 else 0,
            "type_distribution": type_distribution
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب الإحصائيات: {str(e)}"}), 500

