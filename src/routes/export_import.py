from flask import Blueprint, request, jsonify, send_file, current_app
from src.models.user import db, User, DoctorProfile, Consultation, DoctorReview
from src.routes.permissions_system import require_permission
import pandas as pd
import json
import csv
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import zipfile
import tempfile

export_import_bp = Blueprint('export_import', __name__)

@export_import_bp.route('/export/users', methods=['POST'])
@require_permission('export_data')
def export_users():
    """تصدير بيانات المستخدمين"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'excel')  # excel, csv, pdf, json
        filters = data.get('filters', {})
        
        # بناء الاستعلام مع الفلاتر
        query = User.query
        
        if filters.get('user_type'):
            query = query.filter(User.user_type == filters['user_type'])
        
        if filters.get('date_range'):
            start_date = datetime.strptime(filters['date_range']['start'], '%Y-%m-%d')
            end_date = datetime.strptime(filters['date_range']['end'], '%Y-%m-%d')
            query = query.filter(User.created_at.between(start_date, end_date))
        
        users = query.all()
        
        # تحضير البيانات
        users_data = []
        for user in users:
            users_data.append({
                'ID': user.id,
                'الاسم الكامل': user.full_name,
                'البريد الإلكتروني': user.email,
                'رقم الهاتف': user.phone,
                'نوع المستخدم': user.user_type,
                'العمر': user.age,
                'الجنس': user.gender,
                'تاريخ التسجيل': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                'آخر تحديث': user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else ''
            })
        
        if export_format == 'excel':
            return export_to_excel(users_data, 'المستخدمين')
        elif export_format == 'csv':
            return export_to_csv(users_data, 'المستخدمين')
        elif export_format == 'pdf':
            return export_to_pdf(users_data, 'تقرير المستخدمين')
        elif export_format == 'json':
            return export_to_json(users_data, 'المستخدمين')
        else:
            return jsonify({
                'status': 'error',
                'message': 'صيغة التصدير غير مدعومة'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في تصدير بيانات المستخدمين: {str(e)}'
        }), 500

@export_import_bp.route('/export/doctors', methods=['POST'])
@require_permission('export_data')
def export_doctors():
    """تصدير بيانات الأطباء"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'excel')
        filters = data.get('filters', {})
        
        query = Doctor.query
        
        if filters.get('specialization'):
            query = query.filter(Doctor.specialization == filters['specialization'])
        
        if filters.get('is_verified') is not None:
            query = query.filter(Doctor.is_verified == filters['is_verified'])
        
        doctors = query.all()
        
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'ID': doctor.id,
                'الاسم': doctor.name,
                'التخصص': doctor.specialization,
                'سنوات الخبرة': doctor.experience_years,
                'التقييم': doctor.rating,
                'سعر الاستشارة': doctor.consultation_price,
                'متحقق': 'نعم' if doctor.is_verified else 'لا',
                'متاح': 'نعم' if doctor.is_available else 'لا',
                'اللغات': doctor.languages,
                'المؤهلات': doctor.qualifications,
                'تاريخ التسجيل': doctor.created_at.strftime('%Y-%m-%d %H:%M:%S') if doctor.created_at else ''
            })
        
        if export_format == 'excel':
            return export_to_excel(doctors_data, 'الأطباء')
        elif export_format == 'csv':
            return export_to_csv(doctors_data, 'الأطباء')
        elif export_format == 'pdf':
            return export_to_pdf(doctors_data, 'تقرير الأطباء')
        elif export_format == 'json':
            return export_to_json(doctors_data, 'الأطباء')
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في تصدير بيانات الأطباء: {str(e)}'
        }), 500

@export_import_bp.route('/export/consultations', methods=['POST'])
@require_permission('export_data')
def export_consultations():
    """تصدير بيانات الاستشارات"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'excel')
        filters = data.get('filters', {})
        
        query = Consultation.query
        
        if filters.get('status'):
            query = query.filter(Consultation.status == filters['status'])
        
        if filters.get('consultation_type'):
            query = query.filter(Consultation.consultation_type == filters['consultation_type'])
        
        if filters.get('date_range'):
            start_date = datetime.strptime(filters['date_range']['start'], '%Y-%m-%d')
            end_date = datetime.strptime(filters['date_range']['end'], '%Y-%m-%d')
            query = query.filter(Consultation.created_at.between(start_date, end_date))
        
        consultations = query.all()
        
        consultations_data = []
        for consultation in consultations:
            consultations_data.append({
                'ID': consultation.id,
                'المريض': consultation.patient.full_name if consultation.patient else 'غير محدد',
                'الطبيب': consultation.doctor.name if consultation.doctor else 'غير محدد',
                'نوع الاستشارة': consultation.consultation_type,
                'الحالة': consultation.status,
                'الأعراض': consultation.symptoms,
                'التشخيص': consultation.diagnosis,
                'المبلغ': consultation.amount,
                'تاريخ الإنشاء': consultation.created_at.strftime('%Y-%m-%d %H:%M:%S') if consultation.created_at else '',
                'تاريخ التحديث': consultation.updated_at.strftime('%Y-%m-%d %H:%M:%S') if consultation.updated_at else ''
            })
        
        if export_format == 'excel':
            return export_to_excel(consultations_data, 'الاستشارات')
        elif export_format == 'csv':
            return export_to_csv(consultations_data, 'الاستشارات')
        elif export_format == 'pdf':
            return export_to_pdf(consultations_data, 'تقرير الاستشارات')
        elif export_format == 'json':
            return export_to_json(consultations_data, 'الاستشارات')
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في تصدير بيانات الاستشارات: {str(e)}'
        }), 500

@export_import_bp.route('/export/reviews', methods=['POST'])
@require_permission('export_data')
def export_reviews():
    """تصدير بيانات المراجعات"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'excel')
        filters = data.get('filters', {})
        
        query = Review.query
        
        if filters.get('min_rating'):
            query = query.filter(Review.rating >= int(filters['min_rating']))
        
        if filters.get('is_verified') is not None:
            query = query.filter(Review.is_verified == filters['is_verified'])
        
        reviews = query.all()
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'ID': review.id,
                'المريض': review.patient.full_name if review.patient else 'غير محدد',
                'الطبيب': review.doctor.name if review.doctor else 'غير محدد',
                'التقييم': review.rating,
                'التعليق': review.comment,
                'متحقق': 'نعم' if review.is_verified else 'لا',
                'تاريخ الإنشاء': review.created_at.strftime('%Y-%m-%d %H:%M:%S') if review.created_at else ''
            })
        
        if export_format == 'excel':
            return export_to_excel(reviews_data, 'المراجعات')
        elif export_format == 'csv':
            return export_to_csv(reviews_data, 'المراجعات')
        elif export_format == 'pdf':
            return export_to_pdf(reviews_data, 'تقرير المراجعات')
        elif export_format == 'json':
            return export_to_json(reviews_data, 'المراجعات')
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في تصدير بيانات المراجعات: {str(e)}'
        }), 500

@export_import_bp.route('/export/complete-backup', methods=['POST'])
@require_permission('export_data')
def export_complete_backup():
    """تصدير نسخة احتياطية كاملة"""
    try:
        # إنشاء مجلد مؤقت
        temp_dir = tempfile.mkdtemp()
        
        # تصدير جميع البيانات
        users = User.query.all()
        doctors = Doctor.query.all()
        consultations = Consultation.query.all()
        reviews = Review.query.all()
        
        # تحويل البيانات إلى قواميس
        backup_data = {
            'users': [user.to_dict() for user in users],
            'doctors': [doctor.to_dict() for doctor in doctors],
            'consultations': [consultation.to_dict() for consultation in consultations],
            'reviews': [review.to_dict() for review in reviews],
            'export_date': datetime.now().isoformat(),
            'version': '2.0.0'
        }
        
        # حفظ البيانات في ملف JSON
        backup_file = os.path.join(temp_dir, 'complete_backup.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # إنشاء ملف ZIP
        zip_file = os.path.join(temp_dir, 'medical_platform_backup.zip')
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.write(backup_file, 'complete_backup.json')
        
        return send_file(
            zip_file,
            as_attachment=True,
            download_name=f'medical_platform_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في إنشاء النسخة الاحتياطية: {str(e)}'
        }), 500

@export_import_bp.route('/import/users', methods=['POST'])
@require_permission('import_data')
def import_users():
    """استيراد بيانات المستخدمين"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'لم يتم رفع أي ملف'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'لم يتم اختيار ملف'
            }), 400
        
        # قراءة الملف حسب النوع
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        elif file.filename.endswith('.json'):
            data = json.load(file)
            df = pd.DataFrame(data)
        else:
            return jsonify({
                'status': 'error',
                'message': 'نوع الملف غير مدعوم'
            }), 400
        
        # معالجة البيانات واستيرادها
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # التحقق من وجود المستخدم
                existing_user = User.query.filter_by(email=row['البريد الإلكتروني']).first()
                if existing_user:
                    errors.append(f'السطر {index + 1}: المستخدم موجود بالفعل - {row["البريد الإلكتروني"]}')
                    continue
                
                # إنشاء مستخدم جديد
                user = User(
                    full_name=row['الاسم الكامل'],
                    email=row['البريد الإلكتروني'],
                    phone=row.get('رقم الهاتف', ''),
                    user_type=row.get('نوع المستخدم', 'patient'),
                    age=int(row.get('العمر', 0)) if pd.notna(row.get('العمر')) else None,
                    gender=row.get('الجنس', ''),
                    password_hash='imported_user_needs_password_reset'
                )
                
                db.session.add(user)
                imported_count += 1
                
            except Exception as e:
                errors.append(f'السطر {index + 1}: خطأ في الاستيراد - {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'تم استيراد {imported_count} مستخدم بنجاح',
            'data': {
                'imported_count': imported_count,
                'errors_count': len(errors),
                'errors': errors[:10]  # أول 10 أخطاء فقط
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'خطأ في استيراد البيانات: {str(e)}'
        }), 500

def export_to_excel(data, sheet_name):
    """تصدير البيانات إلى Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'{sheet_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def export_to_csv(data, filename):
    """تصدير البيانات إلى CSV"""
    output = io.StringIO()
    
    if data:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    response_output = io.BytesIO()
    response_output.write(output.getvalue().encode('utf-8-sig'))
    response_output.seek(0)
    
    return send_file(
        response_output,
        as_attachment=True,
        download_name=f'{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mimetype='text/csv'
    )

def export_to_pdf(data, title):
    """تصدير البيانات إلى PDF"""
    output = io.BytesIO()
    
    # إنشاء مستند PDF
    doc = SimpleDocTemplate(output, pagesize=A4)
    elements = []
    
    # الأنماط
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # وسط
    )
    
    # العنوان
    title_para = Paragraph(title, title_style)
    elements.append(title_para)
    elements.append(Spacer(1, 12))
    
    if data:
        # إنشاء الجدول
        table_data = []
        
        # رؤوس الأعمدة
        headers = list(data[0].keys())
        table_data.append(headers)
        
        # البيانات
        for row in data:
            table_data.append([str(row[key]) for key in headers])
        
        # إنشاء الجدول
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
    
    # بناء المستند
    doc.build(elements)
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'{title}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )

def export_to_json(data, filename):
    """تصدير البيانات إلى JSON"""
    output = io.BytesIO()
    
    json_data = {
        'data': data,
        'export_date': datetime.now().isoformat(),
        'total_records': len(data)
    }
    
    json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
    output.write(json_str.encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
        mimetype='application/json'
    )

@export_import_bp.route('/templates/download/<template_type>', methods=['GET'])
@require_permission('import_data')
def download_import_template(template_type):
    """تحميل قوالب الاستيراد"""
    try:
        templates = {
            'users': {
                'الاسم الكامل': 'أحمد محمد',
                'البريد الإلكتروني': 'ahmed@example.com',
                'رقم الهاتف': '0501234567',
                'نوع المستخدم': 'patient',
                'العمر': 30,
                'الجنس': 'male'
            },
            'doctors': {
                'الاسم': 'د. سارة أحمد',
                'التخصص': 'أمراض القلب',
                'سنوات الخبرة': 10,
                'سعر الاستشارة': 150,
                'اللغات': 'العربية,الإنجليزية',
                'المؤهلات': 'بكالوريوس طب وجراحة'
            }
        }
        
        if template_type not in templates:
            return jsonify({
                'status': 'error',
                'message': 'نوع القالب غير مدعوم'
            }), 400
        
        template_data = [templates[template_type]]
        return export_to_excel(template_data, f'قالب_{template_type}')
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في تحميل القالب: {str(e)}'
        }), 500

