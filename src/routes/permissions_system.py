from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from functools import wraps
from datetime import datetime
import jwt
import os

permissions_system_bp = Blueprint('permissions_system', __name__)

# تعريف الأدوار والصلاحيات
ROLES_PERMISSIONS = {
    'super_admin': [
        'manage_users', 'manage_doctors', 'manage_consultations', 'manage_payments',
        'manage_reviews', 'manage_notifications', 'manage_analytics', 'manage_settings',
        'manage_ai_services', 'manage_appointments', 'export_data', 'import_data',
        'view_all_data', 'delete_any_data', 'manage_permissions'
    ],
    'admin': [
        'manage_users', 'manage_doctors', 'manage_consultations', 'manage_reviews',
        'manage_notifications', 'view_analytics', 'manage_appointments', 'export_data',
        'view_all_data'
    ],
    'moderator': [
        'manage_reviews', 'manage_notifications', 'view_consultations', 'view_users',
        'view_doctors', 'view_analytics'
    ],
    'doctor': [
        'view_own_consultations', 'manage_own_profile', 'view_own_appointments',
        'manage_own_schedule', 'view_own_reviews', 'respond_to_reviews'
    ],
    'patient': [
        'view_own_consultations', 'manage_own_profile', 'book_appointments',
        'view_own_appointments', 'write_reviews', 'view_doctors'
    ],
    'support': [
        'view_consultations', 'view_users', 'view_doctors', 'manage_notifications',
        'view_reviews'
    ]
}

def require_permission(permission):
    """ديكوريتر للتحقق من الصلاحيات"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من وجود المستخدم في الجلسة
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'يجب تسجيل الدخول أولاً',
                    'code': 'UNAUTHORIZED'
                }), 401
            
            # الحصول على بيانات المستخدم
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': 'المستخدم غير موجود',
                    'code': 'USER_NOT_FOUND'
                }), 404
            
            # التحقق من الصلاحية
            if not has_permission(user, permission):
                return jsonify({
                    'status': 'error',
                    'message': 'ليس لديك صلاحية للوصول إلى هذا المورد',
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'required_permission': permission,
                    'user_role': user.role
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role):
    """ديكوريتر للتحقق من الدور"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'يجب تسجيل الدخول أولاً'
                }), 401
            
            user = User.query.get(user_id)
            if not user or user.role != role:
                return jsonify({
                    'status': 'error',
                    'message': f'يجب أن تكون {role} للوصول إلى هذا المورد'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_permission(user, permission):
    """التحقق من وجود صلاحية معينة للمستخدم"""
    if not user or not user.role:
        return False
    
    user_permissions = ROLES_PERMISSIONS.get(user.role, [])
    return permission in user_permissions

def get_user_permissions(user):
    """الحصول على جميع صلاحيات المستخدم"""
    if not user or not user.role:
        return []
    
    return ROLES_PERMISSIONS.get(user.role, [])

@permissions_system_bp.route('/roles', methods=['GET'])
@require_permission('manage_permissions')
def get_roles():
    """الحصول على قائمة الأدوار المتاحة"""
    try:
        roles = []
        for role, permissions in ROLES_PERMISSIONS.items():
            roles.append({
                'name': role,
                'display_name': get_role_display_name(role),
                'permissions_count': len(permissions),
                'permissions': permissions
            })
        
        return jsonify({
            'status': 'success',
            'data': roles
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على الأدوار: {str(e)}'
        }), 500

@permissions_system_bp.route('/permissions', methods=['GET'])
@require_permission('manage_permissions')
def get_permissions():
    """الحصول على قائمة جميع الصلاحيات"""
    try:
        all_permissions = set()
        for permissions in ROLES_PERMISSIONS.values():
            all_permissions.update(permissions)
        
        permissions_list = []
        for permission in sorted(all_permissions):
            permissions_list.append({
                'name': permission,
                'display_name': get_permission_display_name(permission),
                'category': get_permission_category(permission)
            })
        
        return jsonify({
            'status': 'success',
            'data': permissions_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على الصلاحيات: {str(e)}'
        }), 500

@permissions_system_bp.route('/user/<int:user_id>/permissions', methods=['GET'])
@require_permission('manage_permissions')
def get_user_permissions_api(user_id):
    """الحصول على صلاحيات مستخدم معين"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'المستخدم غير موجود'
            }), 404
        
        permissions = get_user_permissions(user)
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user.id,
                'user_name': user.full_name,
                'role': user.role,
                'permissions': permissions
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على صلاحيات المستخدم: {str(e)}'
        }), 500

@permissions_system_bp.route('/user/<int:user_id>/role', methods=['PUT'])
@require_permission('manage_permissions')
def update_user_role(user_id):
    """تحديث دور المستخدم"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role or new_role not in ROLES_PERMISSIONS:
            return jsonify({
                'status': 'error',
                'message': 'الدور المحدد غير صحيح'
            }), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'المستخدم غير موجود'
            }), 404
        
        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'تم تحديث دور المستخدم من {old_role} إلى {new_role}',
            'data': {
                'user_id': user.id,
                'old_role': old_role,
                'new_role': new_role,
                'new_permissions': get_user_permissions(user)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'خطأ في تحديث دور المستخدم: {str(e)}'
        }), 500

@permissions_system_bp.route('/check', methods=['POST'])
def check_permission():
    """التحقق من صلاحية معينة للمستخدم الحالي"""
    try:
        data = request.get_json()
        permission = data.get('permission')
        
        if not permission:
            return jsonify({
                'status': 'error',
                'message': 'يجب تحديد الصلاحية المطلوب التحقق منها'
            }), 400
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'status': 'success',
                'data': {
                    'has_permission': False,
                    'reason': 'المستخدم غير مسجل الدخول'
                }
            })
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'success',
                'data': {
                    'has_permission': False,
                    'reason': 'المستخدم غير موجود'
                }
            })
        
        has_perm = has_permission(user, permission)
        
        return jsonify({
            'status': 'success',
            'data': {
                'has_permission': has_perm,
                'user_role': user.role,
                'permission': permission,
                'reason': 'الصلاحية متاحة' if has_perm else 'الصلاحية غير متاحة'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في التحقق من الصلاحية: {str(e)}'
        }), 500

@permissions_system_bp.route('/my-permissions', methods=['GET'])
def get_my_permissions():
    """الحصول على صلاحيات المستخدم الحالي"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'يجب تسجيل الدخول أولاً'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'المستخدم غير موجود'
            }), 404
        
        permissions = get_user_permissions(user)
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user.id,
                'user_name': user.full_name,
                'role': user.role,
                'role_display_name': get_role_display_name(user.role),
                'permissions': permissions,
                'permissions_count': len(permissions)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في الحصول على الصلاحيات: {str(e)}'
        }), 500

def get_role_display_name(role):
    """الحصول على الاسم المعروض للدور"""
    role_names = {
        'super_admin': 'مدير عام',
        'admin': 'مدير',
        'moderator': 'مشرف',
        'doctor': 'طبيب',
        'patient': 'مريض',
        'support': 'دعم فني'
    }
    return role_names.get(role, role)

def get_permission_display_name(permission):
    """الحصول على الاسم المعروض للصلاحية"""
    permission_names = {
        'manage_users': 'إدارة المستخدمين',
        'manage_doctors': 'إدارة الأطباء',
        'manage_consultations': 'إدارة الاستشارات',
        'manage_payments': 'إدارة المدفوعات',
        'manage_reviews': 'إدارة المراجعات',
        'manage_notifications': 'إدارة الإشعارات',
        'manage_analytics': 'إدارة التحليلات',
        'manage_settings': 'إدارة الإعدادات',
        'manage_ai_services': 'إدارة خدمات الذكاء الاصطناعي',
        'manage_appointments': 'إدارة المواعيد',
        'export_data': 'تصدير البيانات',
        'import_data': 'استيراد البيانات',
        'view_all_data': 'عرض جميع البيانات',
        'delete_any_data': 'حذف أي بيانات',
        'manage_permissions': 'إدارة الصلاحيات',
        'view_own_consultations': 'عرض الاستشارات الخاصة',
        'manage_own_profile': 'إدارة الملف الشخصي',
        'view_own_appointments': 'عرض المواعيد الخاصة',
        'manage_own_schedule': 'إدارة الجدول الشخصي',
        'view_own_reviews': 'عرض التقييمات الخاصة',
        'respond_to_reviews': 'الرد على التقييمات',
        'book_appointments': 'حجز المواعيد',
        'write_reviews': 'كتابة التقييمات',
        'view_doctors': 'عرض الأطباء',
        'view_consultations': 'عرض الاستشارات',
        'view_users': 'عرض المستخدمين',
        'view_analytics': 'عرض التحليلات',
        'view_reviews': 'عرض التقييمات'
    }
    return permission_names.get(permission, permission)

def get_permission_category(permission):
    """الحصول على فئة الصلاحية"""
    categories = {
        'manage_users': 'إدارة المستخدمين',
        'manage_doctors': 'إدارة الأطباء',
        'manage_consultations': 'إدارة الاستشارات',
        'manage_payments': 'إدارة المدفوعات',
        'manage_reviews': 'إدارة المراجعات',
        'manage_notifications': 'إدارة الإشعارات',
        'manage_analytics': 'التحليلات والتقارير',
        'manage_settings': 'إعدادات النظام',
        'manage_ai_services': 'خدمات الذكاء الاصطناعي',
        'manage_appointments': 'إدارة المواعيد',
        'export_data': 'تصدير واستيراد البيانات',
        'import_data': 'تصدير واستيراد البيانات',
        'view_all_data': 'عرض البيانات',
        'delete_any_data': 'حذف البيانات',
        'manage_permissions': 'إدارة الصلاحيات',
        'view_own_consultations': 'الاستشارات الشخصية',
        'manage_own_profile': 'الملف الشخصي',
        'view_own_appointments': 'المواعيد الشخصية',
        'manage_own_schedule': 'الجدول الشخصي',
        'view_own_reviews': 'التقييمات الشخصية',
        'respond_to_reviews': 'التقييمات الشخصية',
        'book_appointments': 'حجز المواعيد',
        'write_reviews': 'كتابة التقييمات',
        'view_doctors': 'عرض البيانات',
        'view_consultations': 'عرض البيانات',
        'view_users': 'عرض البيانات',
        'view_analytics': 'التحليلات والتقارير',
        'view_reviews': 'عرض البيانات'
    }
    return categories.get(permission, 'عام')

