import unittest
import json
import sys
import os
from datetime import datetime, timedelta

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app, db
from models.user import User, Doctor, Consultation, Review

class MedicalPlatformTestCase(unittest.TestCase):
    """اختبارات المنصة الطبية"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        """تنظيف البيانات بعد الاختبار"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """إنشاء بيانات تجريبية للاختبار"""
        # إنشاء مستخدم تجريبي
        test_user = User(
            full_name='أحمد محمد',
            email='ahmed@test.com',
            phone='0501234567',
            user_type='patient',
            age=30,
            gender='male',
            password_hash='hashed_password'
        )
        db.session.add(test_user)
        
        # إنشاء طبيب تجريبي
        test_doctor = Doctor(
            name='د. سارة أحمد',
            specialization='أمراض القلب',
            experience_years=10,
            rating=4.5,
            consultation_price=150.0,
            is_verified=True,
            is_available=True,
            languages='العربية,الإنجليزية',
            qualifications='بكالوريوس طب وجراحة'
        )
        db.session.add(test_doctor)
        
        db.session.commit()
        
        # إنشاء استشارة تجريبية
        test_consultation = Consultation(
            patient_id=test_user.id,
            doctor_id=test_doctor.id,
            symptoms='صداع مستمر',
            diagnosis='صداع توتري',
            status='completed',
            consultation_type='video',
            amount=150.0
        )
        db.session.add(test_consultation)
        
        # إنشاء مراجعة تجريبية
        test_review = Review(
            patient_id=test_user.id,
            doctor_id=test_doctor.id,
            consultation_id=test_consultation.id,
            rating=5,
            comment='خدمة ممتازة',
            is_verified=True
        )
        db.session.add(test_review)
        
        db.session.commit()

class APITestCase(MedicalPlatformTestCase):
    """اختبارات API"""
    
    def test_health_check(self):
        """اختبار فحص صحة النظام"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('timestamp', data)
    
    def test_get_doctors_list(self):
        """اختبار الحصول على قائمة الأطباء"""
        response = self.client.get('/api/doctors')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
    
    def test_get_doctor_profile(self):
        """اختبار الحصول على ملف طبيب"""
        with self.app.app_context():
            doctor = Doctor.query.first()
            response = self.client.get(f'/api/doctors/{doctor.id}')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['name'], 'د. سارة أحمد')
    
    def test_create_consultation(self):
        """اختبار إنشاء استشارة جديدة"""
        consultation_data = {
            'patient_id': 1,
            'doctor_id': 1,
            'symptoms': 'ألم في الصدر',
            'consultation_type': 'video'
        }
        
        response = self.client.post('/api/consultations',
                                  data=json.dumps(consultation_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_get_consultations(self):
        """اختبار الحصول على قائمة الاستشارات"""
        response = self.client.get('/api/consultations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)

class SearchTestCase(MedicalPlatformTestCase):
    """اختبارات البحث المتقدم"""
    
    def test_search_doctors(self):
        """اختبار البحث في الأطباء"""
        search_data = {
            'query': 'سارة',
            'type': 'doctors'
        }
        
        response = self.client.post('/api/search',
                                  data=json.dumps(search_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('doctors', data['data'])
    
    def test_search_suggestions(self):
        """اختبار اقتراحات البحث"""
        response = self.client.get('/api/search/suggestions?q=سار')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)

class PermissionsTestCase(MedicalPlatformTestCase):
    """اختبارات نظام الصلاحيات"""
    
    def test_get_roles(self):
        """اختبار الحصول على الأدوار"""
        # محاكاة مستخدم مدير
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        
        # تحديث دور المستخدم
        with self.app.app_context():
            user = User.query.get(1)
            user.role = 'super_admin'
            db.session.commit()
        
        response = self.client.get('/api/permissions/roles')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
    
    def test_check_permission(self):
        """اختبار التحقق من الصلاحيات"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        
        permission_data = {
            'permission': 'view_doctors'
        }
        
        response = self.client.post('/api/permissions/check',
                                  data=json.dumps(permission_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('has_permission', data['data'])

class CacheTestCase(MedicalPlatformTestCase):
    """اختبارات التخزين المؤقت"""
    
    def test_cache_stats(self):
        """اختبار إحصائيات التخزين المؤقت"""
        response = self.client.get('/api/cache/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('cache_type', data['data'])
    
    def test_cached_doctors_endpoint(self):
        """اختبار نقطة نهاية الأطباء المخزنة مؤقتاً"""
        response = self.client.get('/api/doctors/cached')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)

class ExportImportTestCase(MedicalPlatformTestCase):
    """اختبارات التصدير والاستيراد"""
    
    def test_export_users(self):
        """اختبار تصدير المستخدمين"""
        # محاكاة مستخدم مدير
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        
        with self.app.app_context():
            user = User.query.get(1)
            user.role = 'admin'
            db.session.commit()
        
        export_data = {
            'format': 'json',
            'filters': {}
        }
        
        response = self.client.post('/api/export/users',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        # يجب أن يكون الرد ملف للتحميل أو JSON
        self.assertIn(response.status_code, [200, 201])

class AIServiceTestCase(MedicalPlatformTestCase):
    """اختبارات خدمات الذكاء الاصطناعي"""
    
    def test_ai_chat(self):
        """اختبار المحادثة مع الذكاء الاصطناعي"""
        chat_data = {
            'message': 'ما هي أعراض الصداع؟',
            'context': 'medical_consultation'
        }
        
        response = self.client.post('/api/ai/chat',
                                  data=json.dumps(chat_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('response', data['data'])
    
    def test_symptom_analysis(self):
        """اختبار تحليل الأعراض"""
        symptoms_data = {
            'symptoms': ['صداع', 'حمى', 'غثيان'],
            'patient_info': {
                'age': 30,
                'gender': 'male'
            }
        }
        
        response = self.client.post('/api/ai/analyze-symptoms',
                                  data=json.dumps(symptoms_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

class NotificationTestCase(MedicalPlatformTestCase):
    """اختبارات الإشعارات"""
    
    def test_send_notification(self):
        """اختبار إرسال إشعار"""
        notification_data = {
            'user_id': 1,
            'title': 'إشعار تجريبي',
            'message': 'هذا إشعار للاختبار',
            'type': 'info'
        }
        
        response = self.client.post('/api/notifications/send',
                                  data=json.dumps(notification_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

class IntegrationTestCase(MedicalPlatformTestCase):
    """اختبارات التكامل"""
    
    def test_complete_consultation_flow(self):
        """اختبار تدفق الاستشارة الكامل"""
        # 1. إنشاء استشارة
        consultation_data = {
            'patient_id': 1,
            'doctor_id': 1,
            'symptoms': 'ألم في البطن',
            'consultation_type': 'video'
        }
        
        response = self.client.post('/api/consultations',
                                  data=json.dumps(consultation_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        consultation_id = json.loads(response.data)['data']['id']
        
        # 2. تحديث حالة الاستشارة
        update_data = {
            'status': 'ongoing',
            'diagnosis': 'التهاب معدة'
        }
        
        response = self.client.put(f'/api/consultations/{consultation_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 3. إضافة مراجعة
        review_data = {
            'patient_id': 1,
            'doctor_id': 1,
            'consultation_id': consultation_id,
            'rating': 5,
            'comment': 'خدمة ممتازة'
        }
        
        response = self.client.post('/api/reviews',
                                  data=json.dumps(review_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)

class PerformanceTestCase(MedicalPlatformTestCase):
    """اختبارات الأداء"""
    
    def test_response_time(self):
        """اختبار وقت الاستجابة"""
        import time
        
        start_time = time.time()
        response = self.client.get('/api/doctors')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.0)  # يجب أن يكون أقل من ثانية واحدة
    
    def test_concurrent_requests(self):
        """اختبار الطلبات المتزامنة"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.client.get('/api/health')
            results.append(response.status_code)
        
        # إنشاء 10 threads للطلبات المتزامنة
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # انتظار انتهاء جميع الطلبات
        for thread in threads:
            thread.join()
        
        # التحقق من نجاح جميع الطلبات
        self.assertEqual(len(results), 10)
        for status_code in results:
            self.assertEqual(status_code, 200)

if __name__ == '__main__':
    # تشغيل الاختبارات
    unittest.main(verbosity=2)

