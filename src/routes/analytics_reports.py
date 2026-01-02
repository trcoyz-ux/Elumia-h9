from flask import Blueprint, request, jsonify, send_file
from src.models.user import db, User, DoctorProfile, Consultation, Appointment, Payment, DoctorReview, ServiceReview, Notification
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')  # استخدام backend غير تفاعلي

analytics_reports_bp = Blueprint("analytics_reports", __name__)

# إعداد الخطوط العربية
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
sns.set_style("whitegrid")

class AnalyticsEngine:
    """محرك التحليلات المتقدم"""
    
    def __init__(self):
        self.colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    def get_consultation_analytics(self, start_date=None, end_date=None):
        """تحليلات الاستشارات"""
        try:
            query = Consultation.query
            
            if start_date:
                query = query.filter(Consultation.request_date >= start_date)
            if end_date:
                query = query.filter(Consultation.request_date <= end_date)
            
            consultations = query.all()
            
            # الإحصائيات الأساسية
            total_consultations = len(consultations)
            completed_consultations = len([c for c in consultations if c.status == 'completed'])
            pending_consultations = len([c for c in consultations if c.status == 'pending'])
            cancelled_consultations = len([c for c in consultations if c.status == 'cancelled'])
            
            # معدل الإكمال
            completion_rate = (completed_consultations / total_consultations * 100) if total_consultations > 0 else 0
            
            # التوزيع حسب النوع
            consultation_types = {}
            for consultation in consultations:
                type_name = consultation.consultation_type or 'غير محدد'
                consultation_types[type_name] = consultation_types.get(type_name, 0) + 1
            
            # التوزيع الزمني (يومي)
            daily_distribution = {}
            for consultation in consultations:
                date_key = consultation.request_date.strftime('%Y-%m-%d')
                daily_distribution[date_key] = daily_distribution.get(date_key, 0) + 1
            
            # متوسط وقت الاستجابة
            response_times = []
            for consultation in consultations:
                if consultation.completed_at and consultation.request_date:
                    response_time = (consultation.completed_at - consultation.request_date).total_seconds() / 3600
                    response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # الإيرادات
            total_revenue = sum([c.consultation_fee or 0 for c in consultations])
            avg_consultation_fee = total_revenue / total_consultations if total_consultations > 0 else 0
            
            return {
                'total_consultations': total_consultations,
                'completed_consultations': completed_consultations,
                'pending_consultations': pending_consultations,
                'cancelled_consultations': cancelled_consultations,
                'completion_rate': round(completion_rate, 2),
                'consultation_types': consultation_types,
                'daily_distribution': daily_distribution,
                'avg_response_time_hours': round(avg_response_time, 2),
                'total_revenue': total_revenue,
                'avg_consultation_fee': round(avg_consultation_fee, 2)
            }
            
        except Exception as e:
            return {'error': f'خطأ في تحليل الاستشارات: {str(e)}'}
    
    def get_doctor_performance_analytics(self, doctor_id=None, start_date=None, end_date=None):
        """تحليلات أداء الأطباء"""
        try:
            query = DoctorProfile.query
            
            if doctor_id:
                query = query.filter_by(id=doctor_id)
            
            doctors = query.all()
            doctor_analytics = []
            
            for doctor in doctors:
                # الاستشارات
                consultation_query = Consultation.query.filter_by(doctor_id=doctor.user_id)
                
                if start_date:
                    consultation_query = consultation_query.filter(Consultation.request_date >= start_date)
                if end_date:
                    consultation_query = consultation_query.filter(Consultation.request_date <= end_date)
                
                consultations = consultation_query.all()
                
                # المواعيد
                appointment_query = Appointment.query.filter_by(doctor_id=doctor.user_id)
                
                if start_date:
                    appointment_query = appointment_query.filter(Appointment.appointment_date >= start_date)
                if end_date:
                    appointment_query = appointment_query.filter(Appointment.appointment_date <= end_date)
                
                appointments = appointment_query.all()
                
                # التقييمات
                reviews = DoctorReview.query.filter_by(doctor_id=doctor.id, is_approved=True).all()
                
                # حساب المؤشرات
                total_consultations = len(consultations)
                completed_consultations = len([c for c in consultations if c.status == 'completed'])
                total_appointments = len(appointments)
                completed_appointments = len([a for a in appointments if a.status == 'completed'])
                
                avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
                total_reviews = len(reviews)
                
                # الإيرادات
                revenue = sum([c.consultation_fee or 0 for c in consultations])
                
                # معدل الاستجابة
                response_times = []
                for consultation in consultations:
                    if consultation.completed_at and consultation.request_date:
                        response_time = (consultation.completed_at - consultation.request_date).total_seconds() / 3600
                        response_times.append(response_time)
                
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                
                doctor_analytics.append({
                    'doctor': doctor.to_dict(),
                    'total_consultations': total_consultations,
                    'completed_consultations': completed_consultations,
                    'completion_rate': (completed_consultations / total_consultations * 100) if total_consultations > 0 else 0,
                    'total_appointments': total_appointments,
                    'completed_appointments': completed_appointments,
                    'avg_rating': round(avg_rating, 2),
                    'total_reviews': total_reviews,
                    'revenue': revenue,
                    'avg_response_time_hours': round(avg_response_time, 2)
                })
            
            return doctor_analytics
            
        except Exception as e:
            return {'error': f'خطأ في تحليل أداء الأطباء: {str(e)}'}
    
    def get_financial_analytics(self, start_date=None, end_date=None):
        """التحليلات المالية"""
        try:
            query = Payment.query.filter_by(status='completed')
            
            if start_date:
                query = query.filter(Payment.completed_at >= start_date)
            if end_date:
                query = query.filter(Payment.completed_at <= end_date)
            
            payments = query.all()
            
            # الإحصائيات الأساسية
            total_revenue = sum([p.amount for p in payments])
            total_transactions = len(payments)
            avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
            
            # التوزيع حسب نوع الدفع
            payment_types = {}
            for payment in payments:
                payment_types[payment.payment_type] = payment_types.get(payment.payment_type, 0) + payment.amount
            
            # التوزيع حسب طريقة الدفع
            payment_methods = {}
            for payment in payments:
                method = payment.payment_method or 'غير محدد'
                payment_methods[method] = payment_methods.get(method, 0) + payment.amount
            
            # التوزيع الزمني (شهري)
            monthly_revenue = {}
            for payment in payments:
                if payment.completed_at:
                    month_key = payment.completed_at.strftime('%Y-%m')
                    monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + payment.amount
            
            # أعلى الأطباء إيراداً
            doctor_revenues = {}
            for payment in payments:
                if payment.consultation_id:
                    consultation = Consultation.query.get(payment.consultation_id)
                    if consultation and consultation.doctor_id:
                        doctor_revenues[consultation.doctor_id] = doctor_revenues.get(consultation.doctor_id, 0) + payment.amount
            
            top_earning_doctors = []
            for doctor_id, revenue in sorted(doctor_revenues.items(), key=lambda x: x[1], reverse=True)[:5]:
                doctor_profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
                if doctor_profile:
                    top_earning_doctors.append({
                        'doctor': doctor_profile.to_dict(),
                        'revenue': revenue
                    })
            
            return {
                'total_revenue': total_revenue,
                'total_transactions': total_transactions,
                'avg_transaction_value': round(avg_transaction_value, 2),
                'payment_types': payment_types,
                'payment_methods': payment_methods,
                'monthly_revenue': monthly_revenue,
                'top_earning_doctors': top_earning_doctors
            }
            
        except Exception as e:
            return {'error': f'خطأ في التحليلات المالية: {str(e)}'}
    
    def get_user_analytics(self, start_date=None, end_date=None):
        """تحليلات المستخدمين"""
        try:
            query = User.query
            
            if start_date:
                query = query.filter(User.created_at >= start_date)
            if end_date:
                query = query.filter(User.created_at <= end_date)
            
            users = query.all()
            
            # الإحصائيات الأساسية
            total_users = len(users)
            active_users = len([u for u in users if u.is_active])
            verified_users = len([u for u in users if u.kyc_verified])
            
            # التوزيع حسب نوع المستخدم
            user_types = {}
            for user in users:
                user_types[user.user_type] = user_types.get(user.user_type, 0) + 1
            
            # معدل النمو الشهري
            monthly_registrations = {}
            for user in users:
                month_key = user.created_at.strftime('%Y-%m')
                monthly_registrations[month_key] = monthly_registrations.get(month_key, 0) + 1
            
            # نشاط المستخدمين (آخر 30 يوم)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_consultations = Consultation.query.filter(Consultation.request_date >= thirty_days_ago).all()
            active_patients = len(set([c.user_id for c in recent_consultations]))
            active_doctors = len(set([c.doctor_id for c in recent_consultations if c.doctor_id]))
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0,
                'user_types': user_types,
                'monthly_registrations': monthly_registrations,
                'active_patients_30d': active_patients,
                'active_doctors_30d': active_doctors
            }
            
        except Exception as e:
            return {'error': f'خطأ في تحليلات المستخدمين: {str(e)}'}
    
    def generate_chart(self, chart_type, data, title, filename):
        """إنشاء الرسوم البيانية"""
        try:
            plt.figure(figsize=(12, 8))
            
            if chart_type == 'bar':
                keys = list(data.keys())
                values = list(data.values())
                bars = plt.bar(keys, values, color=self.colors[:len(keys)])
                plt.xticks(rotation=45, ha='right')
                
                # إضافة القيم على الأعمدة
                for bar, value in zip(bars, values):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                            f'{value}', ha='center', va='bottom')
            
            elif chart_type == 'pie':
                keys = list(data.keys())
                values = list(data.values())
                plt.pie(values, labels=keys, autopct='%1.1f%%', colors=self.colors[:len(keys)])
            
            elif chart_type == 'line':
                keys = list(data.keys())
                values = list(data.values())
                plt.plot(keys, values, marker='o', linewidth=2, markersize=6)
                plt.xticks(rotation=45, ha='right')
                plt.grid(True, alpha=0.3)
            
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            
            # حفظ الرسم البياني
            chart_path = f'/tmp/{filename}.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f'خطأ في إنشاء الرسم البياني: {str(e)}')
            return None

# إنشاء مثيل من محرك التحليلات
analytics_engine = AnalyticsEngine()

@analytics_reports_bp.route("/dashboard", methods=["GET"])
def get_dashboard_analytics():
    """لوحة التحكم الرئيسية للتحليلات"""
    try:
        # تحديد الفترة الزمنية
        days_back = request.args.get('days_back', 30, type=int)
        start_date = datetime.now() - timedelta(days=days_back)
        
        # جمع التحليلات
        consultation_analytics = analytics_engine.get_consultation_analytics(start_date)
        financial_analytics = analytics_engine.get_financial_analytics(start_date)
        user_analytics = analytics_engine.get_user_analytics(start_date)
        
        # إحصائيات سريعة
        total_users = User.query.count()
        total_doctors = DoctorProfile.query.count()
        total_consultations = Consultation.query.count()
        total_revenue = Payment.query.filter_by(status='completed').with_entities(func.sum(Payment.amount)).scalar() or 0
        
        # معدلات النمو
        previous_period_start = start_date - timedelta(days=days_back)
        previous_consultations = Consultation.query.filter(
            and_(Consultation.request_date >= previous_period_start, Consultation.request_date < start_date)
        ).count()
        
        current_consultations = consultation_analytics.get('total_consultations', 0)
        growth_rate = ((current_consultations - previous_consultations) / previous_consultations * 100) if previous_consultations > 0 else 0
        
        return jsonify({
            "summary": {
                "total_users": total_users,
                "total_doctors": total_doctors,
                "total_consultations": total_consultations,
                "total_revenue": total_revenue,
                "growth_rate": round(growth_rate, 2)
            },
            "consultation_analytics": consultation_analytics,
            "financial_analytics": financial_analytics,
            "user_analytics": user_analytics,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "days": days_back
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب تحليلات لوحة التحكم: {str(e)}"}), 500

@analytics_reports_bp.route("/consultations", methods=["GET"])
def get_consultation_analytics():
    """تحليلات مفصلة للاستشارات"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        analytics = analytics_engine.get_consultation_analytics(start_date, end_date)
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في تحليلات الاستشارات: {str(e)}"}), 500

@analytics_reports_bp.route("/doctors/performance", methods=["GET"])
def get_doctor_performance():
    """تحليلات أداء الأطباء"""
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        analytics = analytics_engine.get_doctor_performance_analytics(doctor_id, start_date, end_date)
        
        return jsonify({"doctor_performance": analytics}), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في تحليلات أداء الأطباء: {str(e)}"}), 500

@analytics_reports_bp.route("/financial", methods=["GET"])
def get_financial_analytics():
    """التحليلات المالية"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        analytics = analytics_engine.get_financial_analytics(start_date, end_date)
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في التحليلات المالية: {str(e)}"}), 500

@analytics_reports_bp.route("/users", methods=["GET"])
def get_user_analytics():
    """تحليلات المستخدمين"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        analytics = analytics_engine.get_user_analytics(start_date, end_date)
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في تحليلات المستخدمين: {str(e)}"}), 500

@analytics_reports_bp.route("/charts/generate", methods=["POST"])
def generate_chart():
    """إنشاء رسم بياني"""
    try:
        data = request.get_json()
        
        chart_type = data.get('chart_type', 'bar')
        chart_data = data.get('data', {})
        title = data.get('title', 'رسم بياني')
        filename = data.get('filename', 'chart')
        
        chart_path = analytics_engine.generate_chart(chart_type, chart_data, title, filename)
        
        if chart_path and os.path.exists(chart_path):
            # تحويل الصورة إلى base64
            with open(chart_path, 'rb') as f:
                chart_data_b64 = base64.b64encode(f.read()).decode()
            
            # حذف الملف المؤقت
            os.remove(chart_path)
            
            return jsonify({
                "message": "تم إنشاء الرسم البياني بنجاح",
                "chart_data": f"data:image/png;base64,{chart_data_b64}"
            }), 200
        else:
            return jsonify({"message": "فشل في إنشاء الرسم البياني"}), 500
            
    except Exception as e:
        return jsonify({"message": f"خطأ في إنشاء الرسم البياني: {str(e)}"}), 500

@analytics_reports_bp.route("/reports/generate", methods=["POST"])
def generate_report():
    """إنشاء تقرير شامل"""
    try:
        data = request.get_json()
        
        report_type = data.get('report_type', 'comprehensive')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        format_type = data.get('format', 'pdf')  # pdf, excel, json
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now()
        
        # جمع البيانات
        consultation_analytics = analytics_engine.get_consultation_analytics(start_date, end_date)
        financial_analytics = analytics_engine.get_financial_analytics(start_date, end_date)
        user_analytics = analytics_engine.get_user_analytics(start_date, end_date)
        doctor_performance = analytics_engine.get_doctor_performance_analytics(None, start_date, end_date)
        
        report_data = {
            'report_info': {
                'type': report_type,
                'generated_at': datetime.now().isoformat(),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            },
            'consultation_analytics': consultation_analytics,
            'financial_analytics': financial_analytics,
            'user_analytics': user_analytics,
            'doctor_performance': doctor_performance
        }
        
        if format_type == 'json':
            return jsonify(report_data), 200
        
        elif format_type == 'excel':
            # إنشاء ملف Excel
            filename = f'healthcare_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            filepath = f'/tmp/{filename}'
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # ورقة الملخص
                summary_data = {
                    'المؤشر': ['إجمالي الاستشارات', 'الاستشارات المكتملة', 'إجمالي الإيرادات', 'إجمالي المستخدمين'],
                    'القيمة': [
                        consultation_analytics.get('total_consultations', 0),
                        consultation_analytics.get('completed_consultations', 0),
                        financial_analytics.get('total_revenue', 0),
                        user_analytics.get('total_users', 0)
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='الملخص', index=False)
                
                # ورقة أداء الأطباء
                if doctor_performance and not isinstance(doctor_performance, dict):
                    doctors_data = []
                    for doc in doctor_performance:
                        doctors_data.append({
                            'اسم الطبيب': doc['doctor']['full_name'],
                            'التخصص': doc['doctor']['specialization'],
                            'عدد الاستشارات': doc['total_consultations'],
                            'معدل الإكمال': doc['completion_rate'],
                            'التقييم': doc['avg_rating'],
                            'الإيرادات': doc['revenue']
                        })
                    
                    if doctors_data:
                        pd.DataFrame(doctors_data).to_excel(writer, sheet_name='أداء الأطباء', index=False)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif format_type == 'pdf':
            # إنشاء تقرير PDF
            filename = f'healthcare_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            filepath = f'/tmp/{filename}'
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # العنوان
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # وسط
            )
            
            story.append(Paragraph("تقرير التحليلات الطبية الشامل", title_style))
            story.append(Spacer(1, 12))
            
            # معلومات التقرير
            info_data = [
                ['نوع التقرير', report_type],
                ['تاريخ الإنشاء', datetime.now().strftime('%Y-%m-%d %H:%M')],
                ['فترة التقرير', f"{start_date.strftime('%Y-%m-%d')} إلى {end_date.strftime('%Y-%m-%d')}"]
            ]
            
            info_table = Table(info_data)
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # ملخص الإحصائيات
            story.append(Paragraph("ملخص الإحصائيات", styles['Heading2']))
            
            summary_data = [
                ['المؤشر', 'القيمة'],
                ['إجمالي الاستشارات', str(consultation_analytics.get('total_consultations', 0))],
                ['الاستشارات المكتملة', str(consultation_analytics.get('completed_consultations', 0))],
                ['معدل الإكمال', f"{consultation_analytics.get('completion_rate', 0)}%"],
                ['إجمالي الإيرادات', f"{financial_analytics.get('total_revenue', 0)} ريال"],
                ['إجمالي المستخدمين', str(user_analytics.get('total_users', 0))]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            
            doc.build(story)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        else:
            return jsonify({"message": "نوع التقرير غير مدعوم"}), 400
            
    except Exception as e:
        return jsonify({"message": f"خطأ في إنشاء التقرير: {str(e)}"}), 500

@analytics_reports_bp.route("/kpi", methods=["GET"])
def get_key_performance_indicators():
    """مؤشرات الأداء الرئيسية"""
    try:
        # فترة المقارنة
        current_period_days = request.args.get('current_period', 30, type=int)
        
        current_start = datetime.now() - timedelta(days=current_period_days)
        previous_start = current_start - timedelta(days=current_period_days)
        
        # الفترة الحالية
        current_consultations = Consultation.query.filter(Consultation.request_date >= current_start).count()
        current_revenue = Payment.query.filter(
            and_(Payment.completed_at >= current_start, Payment.status == 'completed')
        ).with_entities(func.sum(Payment.amount)).scalar() or 0
        
        current_users = User.query.filter(User.created_at >= current_start).count()
        
        # الفترة السابقة
        previous_consultations = Consultation.query.filter(
            and_(Consultation.request_date >= previous_start, Consultation.request_date < current_start)
        ).count()
        
        previous_revenue = Payment.query.filter(
            and_(
                Payment.completed_at >= previous_start,
                Payment.completed_at < current_start,
                Payment.status == 'completed'
            )
        ).with_entities(func.sum(Payment.amount)).scalar() or 0
        
        previous_users = User.query.filter(
            and_(User.created_at >= previous_start, User.created_at < current_start)
        ).count()
        
        # حساب معدلات النمو
        def calculate_growth(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return ((current - previous) / previous) * 100
        
        consultation_growth = calculate_growth(current_consultations, previous_consultations)
        revenue_growth = calculate_growth(current_revenue, previous_revenue)
        user_growth = calculate_growth(current_users, previous_users)
        
        # مؤشرات إضافية
        avg_consultation_value = current_revenue / current_consultations if current_consultations > 0 else 0
        
        # معدل رضا العملاء
        recent_reviews = DoctorReview.query.filter(
            and_(DoctorReview.created_at >= current_start, DoctorReview.is_approved == True)
        ).all()
        
        customer_satisfaction = sum([r.rating for r in recent_reviews]) / len(recent_reviews) if recent_reviews else 0
        
        # معدل الاحتفاظ بالعملاء (العملاء الذين لديهم أكثر من استشارة واحدة)
        repeat_customers = db.session.query(Consultation.user_id).filter(
            Consultation.request_date >= current_start
        ).group_by(Consultation.user_id).having(func.count(Consultation.id) > 1).count()
        
        total_customers = db.session.query(Consultation.user_id).filter(
            Consultation.request_date >= current_start
        ).distinct().count()
        
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        kpis = {
            'consultations': {
                'current': current_consultations,
                'previous': previous_consultations,
                'growth_rate': round(consultation_growth, 2)
            },
            'revenue': {
                'current': current_revenue,
                'previous': previous_revenue,
                'growth_rate': round(revenue_growth, 2)
            },
            'new_users': {
                'current': current_users,
                'previous': previous_users,
                'growth_rate': round(user_growth, 2)
            },
            'avg_consultation_value': round(avg_consultation_value, 2),
            'customer_satisfaction': round(customer_satisfaction, 2),
            'retention_rate': round(retention_rate, 2),
            'period_days': current_period_days
        }
        
        return jsonify(kpis), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في جلب مؤشرات الأداء: {str(e)}"}), 500

@analytics_reports_bp.route("/trends", methods=["GET"])
def get_trends_analysis():
    """تحليل الاتجاهات"""
    try:
        months_back = request.args.get('months_back', 6, type=int)
        
        # حساب التواريخ
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # الاتجاهات الشهرية للاستشارات
        monthly_consultations = db.session.query(
            extract('year', Consultation.request_date).label('year'),
            extract('month', Consultation.request_date).label('month'),
            func.count(Consultation.id).label('count')
        ).filter(Consultation.request_date >= start_date).group_by(
            extract('year', Consultation.request_date),
            extract('month', Consultation.request_date)
        ).order_by('year', 'month').all()
        
        # الاتجاهات الشهرية للإيرادات
        monthly_revenue = db.session.query(
            extract('year', Payment.completed_at).label('year'),
            extract('month', Payment.completed_at).label('month'),
            func.sum(Payment.amount).label('revenue')
        ).filter(
            and_(Payment.completed_at >= start_date, Payment.status == 'completed')
        ).group_by(
            extract('year', Payment.completed_at),
            extract('month', Payment.completed_at)
        ).order_by('year', 'month').all()
        
        # الاتجاهات الشهرية للمستخدمين الجدد
        monthly_users = db.session.query(
            extract('year', User.created_at).label('year'),
            extract('month', User.created_at).label('month'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= start_date).group_by(
            extract('year', User.created_at),
            extract('month', User.created_at)
        ).order_by('year', 'month').all()
        
        # تنسيق البيانات
        consultation_trend = [
            {
                'period': f"{int(row.year)}-{int(row.month):02d}",
                'value': row.count
            }
            for row in monthly_consultations
        ]
        
        revenue_trend = [
            {
                'period': f"{int(row.year)}-{int(row.month):02d}",
                'value': float(row.revenue) if row.revenue else 0
            }
            for row in monthly_revenue
        ]
        
        user_trend = [
            {
                'period': f"{int(row.year)}-{int(row.month):02d}",
                'value': row.count
            }
            for row in monthly_users
        ]
        
        return jsonify({
            'consultation_trend': consultation_trend,
            'revenue_trend': revenue_trend,
            'user_trend': user_trend,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'months': months_back
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"خطأ في تحليل الاتجاهات: {str(e)}"}), 500

