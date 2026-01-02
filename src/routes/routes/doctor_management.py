from flask import Blueprint, request, jsonify
from src.models.user import db, User, DoctorProfile, DoctorLicense, DoctorReview
from datetime import datetime, date
import json
import os
from werkzeug.utils import secure_filename

doctor_management_bp = Blueprint("doctor_management", __name__)

# إعدادات رفع الملفات
UPLOAD_FOLDER = 'uploads/licenses'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@doctor_management_bp.route("/register", methods=["POST"])
def register_doctor():
    """تسجيل طبيب جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['user_id', 'full_name', 'specialization', 'consultation_fee']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        # التحقق من وجود المستخدم
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"message": "المستخدم غير موجود"}), 404
        
        # التحقق من عدم وجود ملف طبيب مسبقاً
        existing_profile = DoctorProfile.query.filter_by(user_id=data['user_id']).first()
        if existing_profile:
            return jsonify({"message": "ملف الطبيب موجود مسبقاً"}), 400
        
        # إنشاء ملف الطبيب
        doctor_profile = DoctorProfile(
            user_id=data['user_id'],
            full_name=data['full_name'],
            specialization=data['specialization'],
            sub_specialization=data.get('sub_specialization'),
            years_of_experience=data.get('years_of_experience', 0),
            medical_school=data.get('medical_school'),
            graduation_year=data.get('graduation_year'),
            bio=data.get('bio'),
            consultation_fee=data['consultation_fee'],
            languages=json.dumps(data.get('languages', ['العربية'])),
            working_hours=json.dumps(data.get('working_hours', {}))
        )
        
        db.session.add(doctor_profile)
        
        # تحديث نوع المستخدم
        user.user_type = 'doctor'
        
        db.session.commit()
        
        return jsonify({
            "message": "تم تسجيل الطبيب بنجاح",
            "doctor_profile": doctor_profile.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في تسجيل الطبيب: {str(e)}"}), 500

@doctor_management_bp.route("/profile/<int:doctor_id>", methods=["GET"])
def get_doctor_profile(doctor_id):
    """الحصول على ملف الطبيب"""
    try:
        doctor = DoctorProfile.query.get(doctor_id)
        if not doctor:
            return jsonify({"message": "ملف الطبيب غير موجود"}), 404
        
        profile_data = doctor.to_dict()
        
        # إضافة معلومات التراخيص
        licenses = [license.to_dict() for license in doctor.licenses.all()]
        profile_data['licenses'] = licenses
        
        # إضافة آخر المراجعات
        recent_reviews = doctor.reviews.filter_by(is_approved=True).order_by(DoctorReview.created_at.desc()).limit(5).all()
        profile_data['recent_reviews'] = [review.to_dict() for review in recent_reviews]
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب ملف الطبيب: {str(e)}"}), 500

@doctor_management_bp.route("/profile/<int:doctor_id>", methods=["PUT"])
def update_doctor_profile(doctor_id):
    """تحديث ملف الطبيب"""
    try:
        doctor = DoctorProfile.query.get(doctor_id)
        if not doctor:
            return jsonify({"message": "ملف الطبيب غير موجود"}), 404
        
        data = request.get_json()
        
        # تحديث البيانات
        updatable_fields = [
            'full_name', 'specialization', 'sub_specialization', 
            'years_of_experience', 'medical_school', 'graduation_year',
            'bio', 'consultation_fee', 'available_for_consultation'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(doctor, field, data[field])
        
        if 'languages' in data:
            doctor.languages = json.dumps(data['languages'])
        
        if 'working_hours' in data:
            doctor.working_hours = json.dumps(data['working_hours'])
        
        doctor.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "تم تحديث ملف الطبيب بنجاح",
            "doctor_profile": doctor.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في تحديث ملف الطبيب: {str(e)}"}), 500

@doctor_management_bp.route("/license/add", methods=["POST"])
def add_doctor_license():
    """إضافة ترخيص للطبيب"""
    try:
        data = request.get_json()
        
        required_fields = ['doctor_id', 'license_type', 'license_number', 'issuing_authority', 'issue_date']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        # التحقق من وجود الطبيب
        doctor = DoctorProfile.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({"message": "ملف الطبيب غير موجود"}), 404
        
        # التحقق من عدم تكرار رقم الترخيص
        existing_license = DoctorLicense.query.filter_by(
            license_number=data['license_number'],
            license_type=data['license_type']
        ).first()
        
        if existing_license:
            return jsonify({"message": "رقم الترخيص موجود مسبقاً"}), 400
        
        # إنشاء الترخيص
        license = DoctorLicense(
            doctor_id=data['doctor_id'],
            license_type=data['license_type'],
            license_number=data['license_number'],
            issuing_authority=data['issuing_authority'],
            issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date(),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            notes=data.get('notes')
        )
        
        db.session.add(license)
        db.session.commit()
        
        return jsonify({
            "message": "تم إضافة الترخيص بنجاح",
            "license": license.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في إضافة الترخيص: {str(e)}"}), 500

@doctor_management_bp.route("/license/upload", methods=["POST"])
def upload_license_document():
    """رفع وثيقة الترخيص"""
    try:
        if 'file' not in request.files:
            return jsonify({"message": "لم يتم رفع ملف"}), 400
        
        file = request.files['file']
        license_id = request.form.get('license_id')
        
        if not license_id:
            return jsonify({"message": "معرف الترخيص مطلوب"}), 400
        
        if file.filename == '':
            return jsonify({"message": "لم يتم اختيار ملف"}), 400
        
        if file and allowed_file(file.filename):
            # إنشاء مجلد الرفع إذا لم يكن موجوداً
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{license_id}_{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            file.save(file_path)
            
            # تحديث الترخيص
            license = DoctorLicense.query.get(license_id)
            if license:
                license.license_document = file_path
                db.session.commit()
                
                return jsonify({
                    "message": "تم رفع الوثيقة بنجاح",
                    "file_path": file_path
                }), 200
            else:
                return jsonify({"message": "الترخيص غير موجود"}), 404
        
        return jsonify({"message": "نوع الملف غير مدعوم"}), 400
        
    except Exception as e:
        return jsonify({"message": f"خطأ في رفع الوثيقة: {str(e)}"}), 500

@doctor_management_bp.route("/license/verify/<int:license_id>", methods=["POST"])
def verify_license(license_id):
    """التحقق من صحة الترخيص"""
    try:
        data = request.get_json()
        verified_by = data.get('verified_by')
        verification_status = data.get('verification_status', 'verified')
        notes = data.get('notes')
        
        if not verified_by:
            return jsonify({"message": "معرف المحقق مطلوب"}), 400
        
        license = DoctorLicense.query.get(license_id)
        if not license:
            return jsonify({"message": "الترخيص غير موجود"}), 404
        
        license.verification_status = verification_status
        license.verified_by = verified_by
        license.verified_at = datetime.utcnow()
        license.notes = notes
        
        db.session.commit()
        
        return jsonify({
            "message": f"تم {verification_status} الترخيص بنجاح",
            "license": license.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في التحقق من الترخيص: {str(e)}"}), 500

@doctor_management_bp.route("/search", methods=["GET"])
def search_doctors():
    """البحث عن الأطباء"""
    try:
        # معاملات البحث
        specialization = request.args.get('specialization')
        min_rating = request.args.get('min_rating', type=float)
        max_fee = request.args.get('max_fee', type=float)
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        search_term = request.args.get('search_term')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # بناء الاستعلام
        query = DoctorProfile.query
        
        if specialization:
            query = query.filter(DoctorProfile.specialization.ilike(f'%{specialization}%'))
        
        if max_fee:
            query = query.filter(DoctorProfile.consultation_fee <= max_fee)
        
        if available_only:
            query = query.filter(DoctorProfile.available_for_consultation == True)
        
        if search_term:
            query = query.filter(
                db.or_(
                    DoctorProfile.full_name.ilike(f'%{search_term}%'),
                    DoctorProfile.specialization.ilike(f'%{search_term}%'),
                    DoctorProfile.bio.ilike(f'%{search_term}%')
                )
            )
        
        # تطبيق التصفح
        doctors = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # تحضير النتائج
        results = []
        for doctor in doctors.items:
            doctor_data = doctor.to_dict()
            
            # تصفية النتائج حسب التقييم إذا تم تحديده
            if min_rating and doctor_data['average_rating'] < min_rating:
                continue
                
            results.append(doctor_data)
        
        return jsonify({
            "doctors": results,
            "pagination": {
                "page": doctors.page,
                "pages": doctors.pages,
                "per_page": doctors.per_page,
                "total": doctors.total,
                "has_next": doctors.has_next,
                "has_prev": doctors.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في البحث: {str(e)}"}), 500

@doctor_management_bp.route("/specializations", methods=["GET"])
def get_specializations():
    """الحصول على قائمة التخصصات المتاحة"""
    try:
        specializations = db.session.query(DoctorProfile.specialization).distinct().all()
        specialization_list = [spec[0] for spec in specializations if spec[0]]
        
        return jsonify({
            "specializations": specialization_list,
            "total": len(specialization_list)
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب التخصصات: {str(e)}"}), 500

@doctor_management_bp.route("/statistics", methods=["GET"])
def get_doctor_statistics():
    """إحصائيات الأطباء"""
    try:
        total_doctors = DoctorProfile.query.count()
        verified_doctors = DoctorProfile.query.join(DoctorLicense).filter(
            DoctorLicense.verification_status == 'verified',
            DoctorLicense.is_active == True
        ).distinct().count()
        
        available_doctors = DoctorProfile.query.filter_by(available_for_consultation=True).count()
        
        # إحصائيات التخصصات
        specialization_stats = db.session.query(
            DoctorProfile.specialization,
            db.func.count(DoctorProfile.id).label('count')
        ).group_by(DoctorProfile.specialization).all()
        
        specialization_data = [
            {"specialization": spec, "count": count} 
            for spec, count in specialization_stats
        ]
        
        return jsonify({
            "total_doctors": total_doctors,
            "verified_doctors": verified_doctors,
            "available_doctors": available_doctors,
            "verification_rate": (verified_doctors / total_doctors * 100) if total_doctors > 0 else 0,
            "specialization_distribution": specialization_data
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب الإحصائيات: {str(e)}"}), 500

