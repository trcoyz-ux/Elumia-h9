from flask import Blueprint, request, jsonify
from src.models.user import db, User, DoctorProfile, Appointment, Notification
from datetime import datetime, timedelta, time
import json
from sqlalchemy import and_, or_
import calendar

advanced_appointments_bp = Blueprint("advanced_appointments", __name__)

class SmartScheduler:
    """جدولة ذكية للمواعيد"""
    
    def __init__(self):
        self.default_appointment_duration = 30  # دقيقة
        self.buffer_time = 15  # وقت فاصل بين المواعيد
        self.working_hours = {
            'start': time(9, 0),  # 9:00 AM
            'end': time(17, 0),   # 5:00 PM
            'break_start': time(12, 0),  # 12:00 PM
            'break_end': time(13, 0)     # 1:00 PM
        }
    
    def get_doctor_availability(self, doctor_id, date):
        """الحصول على أوقات فراغ الطبيب في يوم محدد"""
        try:
            doctor = DoctorProfile.query.get(doctor_id)
            if not doctor:
                return []
            
            # جلب أوقات العمل المخصصة للطبيب
            working_hours = json.loads(doctor.working_hours) if doctor.working_hours else {}
            day_name = calendar.day_name[date.weekday()].lower()
            
            # أوقات العمل لهذا اليوم
            day_schedule = working_hours.get(day_name, {
                'start': '09:00',
                'end': '17:00',
                'break_start': '12:00',
                'break_end': '13:00',
                'is_working': True
            })
            
            if not day_schedule.get('is_working', True):
                return []
            
            # تحويل الأوقات
            start_time = datetime.strptime(day_schedule['start'], '%H:%M').time()
            end_time = datetime.strptime(day_schedule['end'], '%H:%M').time()
            break_start = datetime.strptime(day_schedule.get('break_start', '12:00'), '%H:%M').time()
            break_end = datetime.strptime(day_schedule.get('break_end', '13:00'), '%H:%M').time()
            
            # جلب المواعيد الموجودة
            existing_appointments = Appointment.query.filter(
                and_(
                    Appointment.doctor_id == doctor.user_id,
                    Appointment.appointment_date >= datetime.combine(date, start_time),
                    Appointment.appointment_date <= datetime.combine(date, end_time),
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
            ).all()
            
            # إنشاء قائمة الأوقات المتاحة
            available_slots = []
            current_time = datetime.combine(date, start_time)
            end_datetime = datetime.combine(date, end_time)
            
            while current_time < end_datetime:
                slot_end = current_time + timedelta(minutes=self.default_appointment_duration)
                
                # تحقق من وقت الاستراحة
                if (current_time.time() >= break_start and current_time.time() < break_end):
                    current_time += timedelta(minutes=15)
                    continue
                
                # تحقق من التعارض مع المواعيد الموجودة
                is_available = True
                for appointment in existing_appointments:
                    appointment_end = appointment.appointment_date + timedelta(minutes=self.default_appointment_duration)
                    
                    if (current_time < appointment_end and slot_end > appointment.appointment_date):
                        is_available = False
                        break
                
                if is_available and slot_end <= end_datetime:
                    available_slots.append({
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M'),
                        'datetime': current_time.isoformat()
                    })
                
                current_time += timedelta(minutes=15)  # فترات 15 دقيقة
            
            return available_slots
            
        except Exception as e:
            print(f"خطأ في جلب أوقات الفراغ: {str(e)}")
            return []
    
    def suggest_alternative_times(self, doctor_id, preferred_date, days_range=7):
        """اقتراح أوقات بديلة إذا لم تكن متاحة"""
        suggestions = []
        
        for i in range(days_range):
            check_date = preferred_date + timedelta(days=i)
            available_slots = self.get_doctor_availability(doctor_id, check_date)
            
            if available_slots:
                suggestions.append({
                    'date': check_date.isoformat(),
                    'available_slots': available_slots[:5]  # أول 5 أوقات متاحة
                })
        
        return suggestions
    
    def find_best_match(self, doctor_ids, preferred_date, preferred_time=None):
        """العثور على أفضل تطابق من عدة أطباء"""
        best_matches = []
        
        for doctor_id in doctor_ids:
            doctor = DoctorProfile.query.get(doctor_id)
            if not doctor:
                continue
            
            available_slots = self.get_doctor_availability(doctor_id, preferred_date)
            
            if available_slots:
                # إذا تم تحديد وقت مفضل، ابحث عن الأقرب إليه
                if preferred_time:
                    preferred_datetime = datetime.strptime(preferred_time, '%H:%M').time()
                    
                    closest_slot = min(available_slots, key=lambda x: abs(
                        datetime.strptime(x['start_time'], '%H:%M').time().hour * 60 +
                        datetime.strptime(x['start_time'], '%H:%M').time().minute -
                        (preferred_datetime.hour * 60 + preferred_datetime.minute)
                    ))
                    
                    best_matches.append({
                        'doctor': doctor.to_dict(),
                        'recommended_slot': closest_slot,
                        'all_slots': available_slots
                    })
                else:
                    best_matches.append({
                        'doctor': doctor.to_dict(),
                        'recommended_slot': available_slots[0],
                        'all_slots': available_slots
                    })
        
        # ترتيب حسب التقييم والسعر
        best_matches.sort(key=lambda x: (-x['doctor']['average_rating'], x['doctor']['consultation_fee']))
        
        return best_matches

# إنشاء مثيل من الجدولة الذكية
smart_scheduler = SmartScheduler()

@advanced_appointments_bp.route("/book", methods=["POST"])
def book_appointment():
    """حجز موعد جديد"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'doctor_id', 'appointment_date', 'appointment_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"الحقل {field} مطلوب"}), 400
        
        user_id = data['user_id']
        doctor_id = data['doctor_id']
        appointment_date = datetime.fromisoformat(data['appointment_date'])
        appointment_type = data['appointment_type']
        
        # التحقق من وجود المستخدم والطبيب
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "المستخدم غير موجود"}), 404
        
        doctor = DoctorProfile.query.get(doctor_id)
        if not doctor:
            return jsonify({"message": "الطبيب غير موجود"}), 404
        
        # التحقق من توفر الوقت
        date_only = appointment_date.date()
        available_slots = smart_scheduler.get_doctor_availability(doctor_id, date_only)
        
        requested_time = appointment_date.strftime('%H:%M')
        is_available = any(slot['start_time'] == requested_time for slot in available_slots)
        
        if not is_available:
            # اقتراح أوقات بديلة
            alternatives = smart_scheduler.suggest_alternative_times(doctor_id, date_only)
            
            return jsonify({
                "message": "الوقت المطلوب غير متاح",
                "available_alternatives": alternatives
            }), 409
        
        # إنشاء الموعد
        appointment = Appointment(
            user_id=user_id,
            doctor_id=doctor.user_id,
            appointment_date=appointment_date,
            appointment_type=appointment_type,
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # إرسال إشعار للطبيب والمريض
        # إشعار للطبيب
        doctor_notification = Notification(
            user_id=doctor.user_id,
            message=f"موعد جديد مع {user.username} في {appointment_date.strftime('%Y-%m-%d %H:%M')}",
            notification_type='appointment_reminder'
        )
        
        # إشعار للمريض
        patient_notification = Notification(
            user_id=user_id,
            message=f"تم تأكيد موعدك مع د. {doctor.full_name} في {appointment_date.strftime('%Y-%m-%d %H:%M')}",
            notification_type='appointment_reminder'
        )
        
        db.session.add(doctor_notification)
        db.session.add(patient_notification)
        db.session.commit()
        
        return jsonify({
            "message": "تم حجز الموعد بنجاح",
            "appointment": {
                "id": appointment.id,
                "appointment_date": appointment.appointment_date.isoformat(),
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
                "doctor": doctor.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في حجز الموعد: {str(e)}"}), 500

@advanced_appointments_bp.route("/availability/<int:doctor_id>", methods=["GET"])
def get_doctor_availability(doctor_id):
    """الحصول على أوقات فراغ الطبيب"""
    try:
        date_str = request.args.get('date')
        days_ahead = request.args.get('days_ahead', 7, type=int)
        
        if date_str:
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            available_slots = smart_scheduler.get_doctor_availability(doctor_id, check_date)
            
            return jsonify({
                "date": date_str,
                "available_slots": available_slots
            }), 200
        else:
            # جلب الأوقات المتاحة للأيام القادمة
            availability = {}
            today = datetime.now().date()
            
            for i in range(days_ahead):
                check_date = today + timedelta(days=i)
                available_slots = smart_scheduler.get_doctor_availability(doctor_id, check_date)
                
                if available_slots:
                    availability[check_date.isoformat()] = available_slots
            
            return jsonify({
                "availability": availability
            }), 200
            
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب الأوقات المتاحة: {str(e)}"}), 500

@advanced_appointments_bp.route("/search", methods=["POST"])
def search_appointments():
    """البحث الذكي عن المواعيد المتاحة"""
    try:
        data = request.get_json()
        
        specialization = data.get('specialization')
        preferred_date = datetime.strptime(data['preferred_date'], '%Y-%m-%d').date()
        preferred_time = data.get('preferred_time')
        max_fee = data.get('max_fee')
        min_rating = data.get('min_rating', 0)
        
        # البحث عن الأطباء المناسبين
        query = DoctorProfile.query.filter_by(available_for_consultation=True)
        
        if specialization:
            query = query.filter(DoctorProfile.specialization.ilike(f'%{specialization}%'))
        
        if max_fee:
            query = query.filter(DoctorProfile.consultation_fee <= max_fee)
        
        doctors = query.all()
        
        # تصفية حسب التقييم
        suitable_doctors = [
            doctor for doctor in doctors 
            if doctor.get_average_rating() >= min_rating
        ]
        
        # العثور على أفضل تطابق
        doctor_ids = [doctor.id for doctor in suitable_doctors]
        best_matches = smart_scheduler.find_best_match(doctor_ids, preferred_date, preferred_time)
        
        return jsonify({
            "matches": best_matches,
            "total_found": len(best_matches)
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في البحث: {str(e)}"}), 500

@advanced_appointments_bp.route("/<int:appointment_id>/reschedule", methods=["POST"])
def reschedule_appointment(appointment_id):
    """إعادة جدولة الموعد"""
    try:
        data = request.get_json()
        new_date = datetime.fromisoformat(data['new_appointment_date'])
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"message": "الموعد غير موجود"}), 404
        
        # التحقق من توفر الوقت الجديد
        doctor_profile = DoctorProfile.query.filter_by(user_id=appointment.doctor_id).first()
        if not doctor_profile:
            return jsonify({"message": "ملف الطبيب غير موجود"}), 404
        
        date_only = new_date.date()
        available_slots = smart_scheduler.get_doctor_availability(doctor_profile.id, date_only)
        
        requested_time = new_date.strftime('%H:%M')
        is_available = any(slot['start_time'] == requested_time for slot in available_slots)
        
        if not is_available:
            alternatives = smart_scheduler.suggest_alternative_times(doctor_profile.id, date_only)
            return jsonify({
                "message": "الوقت الجديد غير متاح",
                "available_alternatives": alternatives
            }), 409
        
        # حفظ الوقت القديم للإشعار
        old_date = appointment.appointment_date
        
        # تحديث الموعد
        appointment.appointment_date = new_date
        appointment.status = 'rescheduled'
        db.session.commit()
        
        # إرسال إشعارات
        doctor_notification = Notification(
            user_id=appointment.doctor_id,
            message=f"تم تغيير موعد من {old_date.strftime('%Y-%m-%d %H:%M')} إلى {new_date.strftime('%Y-%m-%d %H:%M')}",
            notification_type='appointment_reminder'
        )
        
        patient_notification = Notification(
            user_id=appointment.user_id,
            message=f"تم تغيير موعدك إلى {new_date.strftime('%Y-%m-%d %H:%M')}",
            notification_type='appointment_reminder'
        )
        
        db.session.add(doctor_notification)
        db.session.add(patient_notification)
        db.session.commit()
        
        return jsonify({
            "message": "تم تغيير موعد الحجز بنجاح",
            "appointment": {
                "id": appointment.id,
                "old_date": old_date.isoformat(),
                "new_date": appointment.appointment_date.isoformat(),
                "status": appointment.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في تغيير الموعد: {str(e)}"}), 500

@advanced_appointments_bp.route("/<int:appointment_id>/cancel", methods=["POST"])
def cancel_appointment(appointment_id):
    """إلغاء الموعد"""
    try:
        data = request.get_json()
        cancellation_reason = data.get('reason', 'لم يتم تحديد السبب')
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"message": "الموعد غير موجود"}), 404
        
        # التحقق من إمكانية الإلغاء (مثلاً قبل 24 ساعة)
        time_until_appointment = appointment.appointment_date - datetime.now()
        if time_until_appointment < timedelta(hours=24):
            return jsonify({
                "message": "لا يمكن إلغاء الموعد قبل أقل من 24 ساعة",
                "hours_remaining": time_until_appointment.total_seconds() / 3600
            }), 400
        
        appointment.status = 'cancelled'
        db.session.commit()
        
        # إرسال إشعارات الإلغاء
        doctor_notification = Notification(
            user_id=appointment.doctor_id,
            message=f"تم إلغاء موعد {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')} - السبب: {cancellation_reason}",
            notification_type='appointment_reminder'
        )
        
        patient_notification = Notification(
            user_id=appointment.user_id,
            message=f"تم إلغاء موعدك في {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')}",
            notification_type='appointment_reminder'
        )
        
        db.session.add(doctor_notification)
        db.session.add(patient_notification)
        db.session.commit()
        
        return jsonify({
            "message": "تم إلغاء الموعد بنجاح",
            "appointment_id": appointment_id,
            "refund_eligible": time_until_appointment > timedelta(hours=48)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في إلغاء الموعد: {str(e)}"}), 500

@advanced_appointments_bp.route("/reminders/send", methods=["POST"])
def send_appointment_reminders():
    """إرسال تذكيرات المواعيد"""
    try:
        # جلب المواعيد التي تحتاج تذكير (24 ساعة و 1 ساعة قبل الموعد)
        now = datetime.now()
        tomorrow = now + timedelta(hours=24)
        one_hour_later = now + timedelta(hours=1)
        
        # تذكيرات 24 ساعة
        appointments_24h = Appointment.query.filter(
            and_(
                Appointment.appointment_date >= tomorrow - timedelta(minutes=30),
                Appointment.appointment_date <= tomorrow + timedelta(minutes=30),
                Appointment.status == 'scheduled',
                Appointment.reminder_sent == False
            )
        ).all()
        
        # تذكيرات ساعة واحدة
        appointments_1h = Appointment.query.filter(
            and_(
                Appointment.appointment_date >= one_hour_later - timedelta(minutes=15),
                Appointment.appointment_date <= one_hour_later + timedelta(minutes=15),
                Appointment.status == 'scheduled'
            )
        ).all()
        
        reminders_sent = 0
        
        # إرسال تذكيرات 24 ساعة
        for appointment in appointments_24h:
            doctor = DoctorProfile.query.filter_by(user_id=appointment.doctor_id).first()
            
            # تذكير للمريض
            patient_notification = Notification(
                user_id=appointment.user_id,
                message=f"تذكير: لديك موعد غداً مع د. {doctor.full_name if doctor else 'الطبيب'} في {appointment.appointment_date.strftime('%H:%M')}",
                notification_type='appointment_reminder',
                priority='high'
            )
            
            # تذكير للطبيب
            doctor_notification = Notification(
                user_id=appointment.doctor_id,
                message=f"تذكير: لديك موعد غداً في {appointment.appointment_date.strftime('%H:%M')}",
                notification_type='appointment_reminder',
                priority='normal'
            )
            
            db.session.add(patient_notification)
            db.session.add(doctor_notification)
            
            appointment.reminder_sent = True
            reminders_sent += 2
        
        # إرسال تذكيرات ساعة واحدة
        for appointment in appointments_1h:
            doctor = DoctorProfile.query.filter_by(user_id=appointment.doctor_id).first()
            
            urgent_notification = Notification(
                user_id=appointment.user_id,
                message=f"تذكير عاجل: موعدك مع د. {doctor.full_name if doctor else 'الطبيب'} خلال ساعة في {appointment.appointment_date.strftime('%H:%M')}",
                notification_type='appointment_reminder',
                priority='urgent'
            )
            
            db.session.add(urgent_notification)
            reminders_sent += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"تم إرسال {reminders_sent} تذكير",
            "reminders_24h": len(appointments_24h) * 2,
            "reminders_1h": len(appointments_1h)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"خطأ في إرسال التذكيرات: {str(e)}"}), 500

@advanced_appointments_bp.route("/user/<int:user_id>/appointments", methods=["GET"])
def get_user_appointments(user_id):
    """الحصول على مواعيد المستخدم"""
    try:
        status_filter = request.args.get('status')
        upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Appointment.query.filter_by(user_id=user_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if upcoming_only:
            query = query.filter(Appointment.appointment_date >= datetime.now())
        
        appointments = query.order_by(Appointment.appointment_date.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        appointments_data = []
        for appointment in appointments.items:
            doctor = DoctorProfile.query.filter_by(user_id=appointment.doctor_id).first()
            
            appointments_data.append({
                'id': appointment.id,
                'appointment_date': appointment.appointment_date.isoformat(),
                'appointment_type': appointment.appointment_type,
                'status': appointment.status,
                'doctor': doctor.to_dict() if doctor else None,
                'can_reschedule': (appointment.appointment_date - datetime.now()) > timedelta(hours=24),
                'can_cancel': (appointment.appointment_date - datetime.now()) > timedelta(hours=24)
            })
        
        return jsonify({
            "appointments": appointments_data,
            "pagination": {
                "page": appointments.page,
                "pages": appointments.pages,
                "per_page": appointments.per_page,
                "total": appointments.total,
                "has_next": appointments.has_next,
                "has_prev": appointments.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب المواعيد: {str(e)}"}), 500

@advanced_appointments_bp.route("/doctor/<int:doctor_id>/schedule", methods=["GET"])
def get_doctor_schedule(doctor_id):
    """الحصول على جدول الطبيب"""
    try:
        date_str = request.args.get('date')
        week_view = request.args.get('week_view', 'false').lower() == 'true'
        
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()
        
        doctor = DoctorProfile.query.get(doctor_id)
        if not doctor:
            return jsonify({"message": "الطبيب غير موجود"}), 404
        
        if week_view:
            # عرض أسبوعي
            start_of_week = target_date - timedelta(days=target_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            schedule = {}
            for i in range(7):
                day = start_of_week + timedelta(days=i)
                
                # المواعيد المحجوزة
                appointments = Appointment.query.filter(
                    and_(
                        Appointment.doctor_id == doctor.user_id,
                        Appointment.appointment_date >= datetime.combine(day, time.min),
                        Appointment.appointment_date <= datetime.combine(day, time.max),
                        Appointment.status.in_(['scheduled', 'confirmed'])
                    )
                ).all()
                
                # الأوقات المتاحة
                available_slots = smart_scheduler.get_doctor_availability(doctor_id, day)
                
                schedule[day.isoformat()] = {
                    'appointments': [
                        {
                            'id': apt.id,
                            'time': apt.appointment_date.strftime('%H:%M'),
                            'type': apt.appointment_type,
                            'status': apt.status,
                            'patient_id': apt.user_id
                        }
                        for apt in appointments
                    ],
                    'available_slots': available_slots,
                    'total_appointments': len(appointments),
                    'available_slots_count': len(available_slots)
                }
            
            return jsonify({
                "doctor": doctor.to_dict(),
                "week_schedule": schedule,
                "week_start": start_of_week.isoformat(),
                "week_end": end_of_week.isoformat()
            }), 200
        else:
            # عرض يومي
            appointments = Appointment.query.filter(
                and_(
                    Appointment.doctor_id == doctor.user_id,
                    Appointment.appointment_date >= datetime.combine(target_date, time.min),
                    Appointment.appointment_date <= datetime.combine(target_date, time.max),
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
            ).order_by(Appointment.appointment_date).all()
            
            available_slots = smart_scheduler.get_doctor_availability(doctor_id, target_date)
            
            return jsonify({
                "doctor": doctor.to_dict(),
                "date": target_date.isoformat(),
                "appointments": [
                    {
                        'id': apt.id,
                        'time': apt.appointment_date.strftime('%H:%M'),
                        'type': apt.appointment_type,
                        'status': apt.status,
                        'patient_id': apt.user_id
                    }
                    for apt in appointments
                ],
                "available_slots": available_slots,
                "statistics": {
                    "total_appointments": len(appointments),
                    "available_slots": len(available_slots),
                    "utilization_rate": len(appointments) / (len(appointments) + len(available_slots)) * 100 if (len(appointments) + len(available_slots)) > 0 else 0
                }
            }), 200
            
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب الجدول: {str(e)}"}), 500

@advanced_appointments_bp.route("/statistics", methods=["GET"])
def get_appointment_statistics():
    """إحصائيات المواعيد"""
    try:
        # إحصائيات عامة
        total_appointments = Appointment.query.count()
        scheduled_appointments = Appointment.query.filter_by(status='scheduled').count()
        completed_appointments = Appointment.query.filter_by(status='completed').count()
        cancelled_appointments = Appointment.query.filter_by(status='cancelled').count()
        
        # إحصائيات هذا الشهر
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_appointments = Appointment.query.filter(
            Appointment.created_at >= start_of_month
        ).count()
        
        # معدل الإلغاء
        cancellation_rate = (cancelled_appointments / total_appointments * 100) if total_appointments > 0 else 0
        
        # أكثر الأطباء حجزاً
        popular_doctors = db.session.query(
            Appointment.doctor_id,
            db.func.count(Appointment.id).label('appointment_count')
        ).group_by(Appointment.doctor_id).order_by(
            db.func.count(Appointment.id).desc()
        ).limit(5).all()
        
        popular_doctors_data = []
        for doctor_id, count in popular_doctors:
            doctor = DoctorProfile.query.filter_by(user_id=doctor_id).first()
            if doctor:
                popular_doctors_data.append({
                    'doctor': doctor.to_dict(),
                    'appointment_count': count
                })
        
        return jsonify({
            "total_appointments": total_appointments,
            "scheduled_appointments": scheduled_appointments,
            "completed_appointments": completed_appointments,
            "cancelled_appointments": cancelled_appointments,
            "monthly_appointments": monthly_appointments,
            "cancellation_rate": round(cancellation_rate, 2),
            "completion_rate": round((completed_appointments / total_appointments * 100) if total_appointments > 0 else 0, 2),
            "popular_doctors": popular_doctors_data
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب الإحصائيات: {str(e)}"}), 500

