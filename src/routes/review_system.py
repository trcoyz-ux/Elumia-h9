from flask import Blueprint, request, jsonify
from src.models.user import db, DoctorReview, ServiceReview, DoctorProfile, User, Consultation
from datetime import datetime
import json

review_system_bp = Blueprint("review_system", __name__)

@review_system_bp.route("/doctor/add", methods=["POST"])
def add_doctor_review():
    """إضافة تقييم للطبيب"""
    try:
        data = request.get_json()
        
        required_fields = ['doctor_id', 'patient_id', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        # التحقق من صحة التقييم (1-5)
        if not 1 <= data['rating'] <= 5:
            return jsonify({"message": "التقييم يجب أن يكون بين 1 و 5"}), 400
        
        # التحقق من وجود الطبيب والمريض
        doctor = DoctorProfile.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({"message": "الطبيب غير موجود"}), 404
        
        patient = User.query.get(data['patient_id'])
        if not patient:
            return jsonify({"message": "المريض غير موجود"}), 404
        
        # التحقق من وجود استشارة مكتملة (اختياري)
        consultation_id = data.get('consultation_id')
        if consultation_id:
            consultation = Consultation.query.filter_by(
                id=consultation_id,
                user_id=data['patient_id'],
                doctor_id=doctor.user_id,
                status='completed'
            ).first()
            
            if not consultation:
                return jsonify({"message": "الاستشارة غير موجودة أو غير مكتملة"}), 404
            
            # التحقق من عدم وجود تقييم مسبق لنفس الاستشارة
            existing_review = DoctorReview.query.filter_by(
                consultation_id=consultation_id
            ).first()
            
            if existing_review:
                return jsonify({"message": "تم تقييم هذه الاستشارة مسبقاً"}), 400
        
        # إنشاء التقييم
        review = DoctorReview(
            doctor_id=data['doctor_id'],
            patient_id=data['patient_id'],
            consultation_id=consultation_id,
            rating=data['rating'],
            review_text=data.get('review_text'),
            review_categories=json.dumps(data.get('review_categories', {})),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            "message": "تم إضافة التقييم بنجاح",
            "review": review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في إضافة التقييم: {str(e)}"}), 500

@review_system_bp.route("/doctor/<int:doctor_id>/reviews", methods=["GET"])
def get_doctor_reviews(doctor_id):
    """الحصول على تقييمات الطبيب"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        min_rating = request.args.get('min_rating', type=int)
        
        # التحقق من وجود الطبيب
        doctor = DoctorProfile.query.get(doctor_id)
        if not doctor:
            return jsonify({"message": "الطبيب غير موجود"}), 404
        
        # بناء الاستعلام
        query = DoctorReview.query.filter_by(doctor_id=doctor_id)
        
        if approved_only:
            query = query.filter_by(is_approved=True)
        
        if min_rating:
            query = query.filter(DoctorReview.rating >= min_rating)
        
        # ترتيب حسب التاريخ
        query = query.order_by(DoctorReview.created_at.desc())
        
        # تطبيق التصفح
        reviews = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # حساب الإحصائيات
        all_reviews = DoctorReview.query.filter_by(
            doctor_id=doctor_id,
            is_approved=True
        ).all()
        
        total_reviews = len(all_reviews)
        average_rating = sum(r.rating for r in all_reviews) / total_reviews if total_reviews > 0 else 0
        
        # توزيع التقييمات
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[str(i)] = len([r for r in all_reviews if r.rating == i])
        
        return jsonify({
            "reviews": [review.to_dict() for review in reviews.items],
            "statistics": {
                "total_reviews": total_reviews,
                "average_rating": round(average_rating, 2),
                "rating_distribution": rating_distribution
            },
            "pagination": {
                "page": reviews.page,
                "pages": reviews.pages,
                "per_page": reviews.per_page,
                "total": reviews.total,
                "has_next": reviews.has_next,
                "has_prev": reviews.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب التقييمات: {str(e)}"}), 500

@review_system_bp.route("/doctor/review/<int:review_id>/approve", methods=["POST"])
def approve_doctor_review(review_id):
    """الموافقة على تقييم الطبيب"""
    try:
        data = request.get_json()
        approved_by = data.get('approved_by')
        
        if not approved_by:
            return jsonify({"message": "معرف المراجع مطلوب"}), 400
        
        review = DoctorReview.query.get(review_id)
        if not review:
            return jsonify({"message": "التقييم غير موجود"}), 404
        
        review.is_approved = True
        review.approved_by = approved_by
        review.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "تم الموافقة على التقييم",
            "review": review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في الموافقة على التقييم: {str(e)}"}), 500

@review_system_bp.route("/service/add", methods=["POST"])
def add_service_review():
    """إضافة تقييم للخدمة"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'service_type', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        # التحقق من صحة التقييم
        if not 1 <= data['rating'] <= 5:
            return jsonify({"message": "التقييم يجب أن يكون بين 1 و 5"}), 400
        
        # التحقق من نوع الخدمة
        valid_service_types = ['consultation', 'ai_analysis', 'pharmacy', 'field_team']
        if data['service_type'] not in valid_service_types:
            return jsonify({"message": "نوع الخدمة غير صحيح"}), 400
        
        # التحقق من وجود المستخدم
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"message": "المستخدم غير موجود"}), 404
        
        # إنشاء تقييم الخدمة
        review = ServiceReview(
            user_id=data['user_id'],
            service_type=data['service_type'],
            service_id=data.get('service_id'),
            rating=data['rating'],
            review_text=data.get('review_text'),
            aspects_rating=json.dumps(data.get('aspects_rating', {})),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            "message": "تم إضافة تقييم الخدمة بنجاح",
            "review": review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في إضافة تقييم الخدمة: {str(e)}"}), 500

@review_system_bp.route("/service/<service_type>/reviews", methods=["GET"])
def get_service_reviews(service_type):
    """الحصول على تقييمات الخدمة"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        min_rating = request.args.get('min_rating', type=int)
        
        # بناء الاستعلام
        query = ServiceReview.query.filter_by(service_type=service_type)
        
        if min_rating:
            query = query.filter(ServiceReview.rating >= min_rating)
        
        # ترتيب حسب التاريخ
        query = query.order_by(ServiceReview.created_at.desc())
        
        # تطبيق التصفح
        reviews = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # حساب الإحصائيات
        all_reviews = ServiceReview.query.filter_by(service_type=service_type).all()
        total_reviews = len(all_reviews)
        average_rating = sum(r.rating for r in all_reviews) / total_reviews if total_reviews > 0 else 0
        
        # توزيع التقييمات
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[str(i)] = len([r for r in all_reviews if r.rating == i])
        
        return jsonify({
            "reviews": [review.to_dict() for review in reviews.items],
            "statistics": {
                "total_reviews": total_reviews,
                "average_rating": round(average_rating, 2),
                "rating_distribution": rating_distribution
            },
            "pagination": {
                "page": reviews.page,
                "pages": reviews.pages,
                "per_page": reviews.per_page,
                "total": reviews.total,
                "has_next": reviews.has_next,
                "has_prev": reviews.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب تقييمات الخدمة: {str(e)}"}), 500

@review_system_bp.route("/review/<int:review_id>", methods=["PUT"])
def update_review(review_id):
    """تحديث التقييم"""
    try:
        data = request.get_json()
        review_type = data.get('review_type', 'doctor')  # doctor or service
        
        if review_type == 'doctor':
            review = DoctorReview.query.get(review_id)
        else:
            review = ServiceReview.query.get(review_id)
        
        if not review:
            return jsonify({"message": "التقييم غير موجود"}), 404
        
        # التحقق من صاحب التقييم
        user_id = data.get('user_id')
        if review_type == 'doctor':
            if review.patient_id != user_id:
                return jsonify({"message": "غير مسموح بتعديل هذا التقييم"}), 403
        else:
            if review.user_id != user_id:
                return jsonify({"message": "غير مسموح بتعديل هذا التقييم"}), 403
        
        # تحديث البيانات
        if 'rating' in data and 1 <= data['rating'] <= 5:
            review.rating = data['rating']
        
        if 'review_text' in data:
            review.review_text = data['review_text']
        
        if review_type == 'doctor' and 'review_categories' in data:
            review.review_categories = json.dumps(data['review_categories'])
        elif review_type == 'service' and 'aspects_rating' in data:
            review.aspects_rating = json.dumps(data['aspects_rating'])
        
        review.updated_at = datetime.utcnow()
        
        # إعادة تعيين الموافقة للمراجعة
        if review_type == 'doctor':
            review.is_approved = False
            review.approved_by = None
            review.approved_at = None
        
        db.session.commit()
        
        return jsonify({
            "message": "تم تحديث التقييم بنجاح",
            "review": review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في تحديث التقييم: {str(e)}"}), 500

@review_system_bp.route("/review/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    """حذف التقييم"""
    try:
        data = request.get_json()
        review_type = data.get('review_type', 'doctor')
        user_id = data.get('user_id')
        
        if review_type == 'doctor':
            review = DoctorReview.query.get(review_id)
            if review and review.patient_id != user_id:
                return jsonify({"message": "غير مسموح بحذف هذا التقييم"}), 403
        else:
            review = ServiceReview.query.get(review_id)
            if review and review.user_id != user_id:
                return jsonify({"message": "غير مسموح بحذف هذا التقييم"}), 403
        
        if not review:
            return jsonify({"message": "التقييم غير موجود"}), 404
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({"message": "تم حذف التقييم بنجاح"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في حذف التقييم: {str(e)}"}), 500

@review_system_bp.route("/statistics", methods=["GET"])
def get_review_statistics():
    """إحصائيات التقييمات العامة"""
    try:
        # إحصائيات تقييمات الأطباء
        doctor_reviews = DoctorReview.query.filter_by(is_approved=True).all()
        total_doctor_reviews = len(doctor_reviews)
        avg_doctor_rating = sum(r.rating for r in doctor_reviews) / total_doctor_reviews if total_doctor_reviews > 0 else 0
        
        # إحصائيات تقييمات الخدمات
        service_reviews = ServiceReview.query.all()
        total_service_reviews = len(service_reviews)
        avg_service_rating = sum(r.rating for r in service_reviews) / total_service_reviews if total_service_reviews > 0 else 0
        
        # إحصائيات حسب نوع الخدمة
        service_stats = {}
        service_types = ['consultation', 'ai_analysis', 'pharmacy', 'field_team']
        
        for service_type in service_types:
            type_reviews = [r for r in service_reviews if r.service_type == service_type]
            service_stats[service_type] = {
                'total_reviews': len(type_reviews),
                'average_rating': sum(r.rating for r in type_reviews) / len(type_reviews) if type_reviews else 0
            }
        
        # التقييمات المعلقة للموافقة
        pending_reviews = DoctorReview.query.filter_by(is_approved=False).count()
        
        return jsonify({
            "doctor_reviews": {
                "total": total_doctor_reviews,
                "average_rating": round(avg_doctor_rating, 2)
            },
            "service_reviews": {
                "total": total_service_reviews,
                "average_rating": round(avg_service_rating, 2),
                "by_service_type": service_stats
            },
            "pending_approvals": pending_reviews,
            "overall_satisfaction": round((avg_doctor_rating + avg_service_rating) / 2, 2) if (avg_doctor_rating > 0 or avg_service_rating > 0) else 0
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب الإحصائيات: {str(e)}"}), 500

@review_system_bp.route("/pending", methods=["GET"])
def get_pending_reviews():
    """الحصول على التقييمات المعلقة للموافقة"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pending_reviews = DoctorReview.query.filter_by(is_approved=False).order_by(
            DoctorReview.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        reviews_data = []
        for review in pending_reviews.items:
            review_data = review.to_dict()
            # إضافة معلومات الطبيب
            doctor = DoctorProfile.query.get(review.doctor_id)
            if doctor:
                review_data['doctor_name'] = doctor.full_name
                review_data['doctor_specialization'] = doctor.specialization
            
            reviews_data.append(review_data)
        
        return jsonify({
            "pending_reviews": reviews_data,
            "pagination": {
                "page": pending_reviews.page,
                "pages": pending_reviews.pages,
                "per_page": pending_reviews.per_page,
                "total": pending_reviews.total,
                "has_next": pending_reviews.has_next,
                "has_prev": pending_reviews.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب التقييمات المعلقة: {str(e)}"}), 500

