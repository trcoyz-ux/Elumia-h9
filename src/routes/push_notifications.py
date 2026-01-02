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

# تهيئة Firebase إذا لم يتم تهيئته مسبقاً
if not firebase_admin._apps:
    try:
        # محاولة القراءة من متغير البيئة أولاً (للنشر على Render)
        firebase_creds_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
        
        if firebase_creds_json:
            try:
                creds_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
                print("تمت تهيئة Firebase بنجاح باستخدام متغيرات البيئة.")
            except Exception as json_err:
                print(f"خطأ في تحليل JSON لمتغير البيئة FIREBASE_SERVICE_ACCOUNT: {str(json_err)}")
        else:
            # المحاولة من الملف المحلي (للتطوير المحلي)
            firebase_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'firebase-service-account-corrected.json')
            if os.path.exists(firebase_config_path):
                cred = credentials.Certificate(firebase_config_path)
                firebase_admin.initialize_app(cred)
                print("تمت تهيئة Firebase بنجاح باستخدام الملف المحلي.")
            else:
                print("تحذير: لم يتم العثور على متغير البيئة FIREBASE_SERVICE_ACCOUNT أو الملف المحلي.")
        
    except Exception as e:
        print(f"تحذير: فشل تهيئة Firebase: {str(e)}")

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
        return jsonify({"message": f"خطأ في إرسال الإشعار: {str(e)}"}), 500
