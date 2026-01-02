from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_auto_id = db.Column(db.String(20), unique=True, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    kyc_verified = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(20), default='patient')  # patient, doctor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_auto_id': self.user_auto_id,
            'username': self.username,
            'email': self.email,
            'user_type': self.user_type,
            'kyc_verified': self.kyc_verified,
            'is_active': self.is_active
        }

class DoctorProfile(db.Model):
    """ملف تعريف الطبيب مع معلومات التراخيص والتخصصات"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    sub_specialization = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    medical_school = db.Column(db.String(200))
    graduation_year = db.Column(db.Integer)
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    consultation_fee = db.Column(db.Float, nullable=False, default=0.0)
    available_for_consultation = db.Column(db.Boolean, default=True)
    languages = db.Column(db.Text)  # JSON array of languages
    working_hours = db.Column(db.Text)  # JSON object with working hours
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='doctor_profile')
    licenses = db.relationship('DoctorLicense', backref='doctor', lazy='dynamic')
    reviews = db.relationship('DoctorReview', backref='doctor', lazy='dynamic')
    
    def __repr__(self):
        return f'<DoctorProfile {self.full_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'specialization': self.specialization,
            'sub_specialization': self.sub_specialization,
            'years_of_experience': self.years_of_experience,
            'medical_school': self.medical_school,
            'graduation_year': self.graduation_year,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'consultation_fee': self.consultation_fee,
            'available_for_consultation': self.available_for_consultation,
            'languages': json.loads(self.languages) if self.languages else [],
            'working_hours': json.loads(self.working_hours) if self.working_hours else {},
            'average_rating': self.get_average_rating(),
            'total_reviews': self.reviews.count(),
            'license_status': self.get_license_status()
        }
    
    def get_average_rating(self):
        """حساب متوسط التقييم"""
        reviews = self.reviews.filter_by(is_approved=True).all()
        if not reviews:
            return 0.0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def get_license_status(self):
        """التحقق من حالة التراخيص"""
        active_licenses = self.licenses.filter_by(is_active=True).count()
        return 'verified' if active_licenses > 0 else 'pending'

class DoctorLicense(db.Model):
    """تراخيص الأطباء وشهاداتهم"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profile.id'), nullable=False)
    license_type = db.Column(db.String(50), nullable=False)  # medical_license, board_certification, fellowship
    license_number = db.Column(db.String(100), nullable=False)
    issuing_authority = db.Column(db.String(200), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    license_document = db.Column(db.String(255))  # رابط الوثيقة
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DoctorLicense {self.license_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_type': self.license_type,
            'license_number': self.license_number,
            'issuing_authority': self.issuing_authority,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'verification_status': self.verification_status,
            'is_active': self.is_active,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }

class DoctorReview(db.Model):
    """تقييمات ومراجعات الأطباء"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profile.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    review_categories = db.Column(db.Text)  # JSON object with category ratings
    is_anonymous = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    patient = db.relationship('User', foreign_keys=[patient_id], backref='reviews_given')
    
    def __repr__(self):
        return f'<DoctorReview {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_categories': json.loads(self.review_categories) if self.review_categories else {},
            'is_anonymous': self.is_anonymous,
            'patient_name': 'مجهول' if self.is_anonymous else self.patient.username,
            'created_at': self.created_at.isoformat(),
            'is_approved': self.is_approved
        }

class ServiceReview(db.Model):
    """تقييمات الخدمات الطبية العامة"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)  # consultation, ai_analysis, pharmacy, field_team
    service_id = db.Column(db.Integer)  # معرف الخدمة المحددة
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    aspects_rating = db.Column(db.Text)  # JSON object with different aspects
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='service_reviews')
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_type': self.service_type,
            'rating': self.rating,
            'review_text': self.review_text,
            'aspects_rating': json.loads(self.aspects_rating) if self.aspects_rating else {},
            'user_name': 'مجهول' if self.is_anonymous else self.user.username,
            'created_at': self.created_at.isoformat()
        }

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_auto_id = db.Column(db.String(20), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    ai_analysis_report = db.Column(db.Text)
    
    def __repr__(self):
        return f"<MedicalRecord {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'record_auto_id': self.record_auto_id,
            'user_id': self.user_id,
            'record_type': self.record_type,
            'file_url': self.file_url,
            'upload_date': self.upload_date.isoformat(),
            'ai_analysis_report': self.ai_analysis_report
        }

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consultation_auto_id = db.Column(db.String(20), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_record.id'))
    status = db.Column(db.String(50), default='pending')
    consultation_type = db.Column(db.String(50))
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    prescription = db.Column(db.Text)
    doctor_notes = db.Column(db.Text)
    doctor_decision = db.Column(db.String(50))  # prescription, additional_tests, clinic_visit
    prescription_status = db.Column(db.String(50))  # pending, approved, dispensed
    additional_tests = db.Column(db.Text)  # قائمة الفحوصات المطلوبة
    test_urgency = db.Column(db.String(20))  # normal, urgent
    visit_type = db.Column(db.String(20))  # in_person, remote
    preferred_visit_date = db.Column(db.DateTime)
    consultation_fee = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime)
    
    # العلاقات
    patient = db.relationship('User', foreign_keys=[user_id], backref='consultations_as_patient')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='consultations_as_doctor')
    reviews = db.relationship('DoctorReview', backref='consultation')
    
    def __repr__(self):
        return f"<Consultation {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'consultation_auto_id': self.consultation_auto_id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'status': self.status,
            'consultation_type': self.consultation_type,
            'request_date': self.request_date.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class PharmacyOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'), nullable=False)
    medication_details = db.Column(db.Text, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_status = db.Column(db.String(50), default='pending')
    
    def __repr__(self):
        return f"<PharmacyOrder {self.id}>"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_auto_id = db.Column(db.String(20), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default='scheduled')
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional patient information
    patient_name = db.Column(db.String(100))
    patient_phone = db.Column(db.String(20))
    patient_age = db.Column(db.Integer)
    case_description = db.Column(db.Text)
    payment_method = db.Column(db.String(50))
    
    def __repr__(self):
        return f"<Appointment {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_auto_id': self.appointment_auto_id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'patient_name': self.patient_name,
            'patient_phone': self.patient_phone,
            'patient_age': self.patient_age,
            'case_description': self.case_description,
            'payment_method': self.payment_method
        }
