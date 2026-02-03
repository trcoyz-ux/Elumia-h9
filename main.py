import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user_management import user_bp
from src.routes.medical_records import medical_records_bp
from src.routes.ai_service import ai_bp
from src.routes.consultations import consultation_bp
from src.routes.field_teams import field_teams_bp
from src.routes.pharmacy import pharmacy_bp
from src.routes.appointments import appointments_bp
from src.routes.payment import payment_bp
from src.routes.notifications import notifications_bp
from src.routes.doctor_management import doctor_management_bp
from src.routes.review_system import review_system_bp
from src.routes.push_notifications import push_notifications_bp
from src.routes.advanced_appointments import advanced_appointments_bp
from src.routes.analytics_reports import analytics_reports_bp
from src.routes.advanced_search import advanced_search_bp
from src.routes.permissions_system import permissions_system_bp
from src.routes.export_import import export_import_bp
from src.routes.performance_cache import performance_cache_bp
from datetime import datetime

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev-only')

# Enable CORS for all routes
CORS(app)

# Register Blueprints in the main application
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(medical_records_bp, url_prefix="/medical_records")
app.register_blueprint(ai_bp, url_prefix="/ai")
app.register_blueprint(consultation_bp, url_prefix="/consultations")
app.register_blueprint(field_teams_bp, url_prefix="/field_teams")
app.register_blueprint(pharmacy_bp, url_prefix="/pharmacy")
app.register_blueprint(appointments_bp, url_prefix="/appointments")
app.register_blueprint(payment_bp, url_prefix="/payment")
app.register_blueprint(notifications_bp, url_prefix="/notifications")
app.register_blueprint(doctor_management_bp, url_prefix="/api/doctors")
app.register_blueprint(review_system_bp, url_prefix="/api/reviews")
app.register_blueprint(push_notifications_bp, url_prefix="/api/push_notifications")
app.register_blueprint(advanced_appointments_bp, url_prefix="/api/advanced_appointments")
app.register_blueprint(analytics_reports_bp, url_prefix="/api/analytics")
app.register_blueprint(advanced_search_bp, url_prefix="/api/search")
app.register_blueprint(permissions_system_bp, url_prefix="/api/permissions")
app.register_blueprint(export_import_bp, url_prefix="/api/export-import")
app.register_blueprint(performance_cache_bp, url_prefix="/api/cache")

# Configure SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()  # Create database tables if they don't exist

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        # Check if the path is likely an API call that should have been handled by a Blueprint
        api_prefixes = ('users', 'medical_records', 'ai', 'consultations', 'field_teams', 'pharmacy', 'appointments', 'payment', 'notifications', 'api/')
        if path.startswith(api_prefixes):
            return jsonify({"error": "API endpoint not found or not implemented"}), 404
        
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Welcome to the healthcare application!"

@app.route("/dashboard")
def dashboard():
    return send_from_directory(os.path.join(app.static_folder, "dashboard"), 'index.html')

@app.route('/doctors')
def doctors():
    """صفحة اختيار الأطباء"""
    return send_from_directory(app.static_folder, 'doctor-selection.html')

@app.route('/admin')
def admin_dashboard():
    """لوحة التحكم الإدارية الجديدة"""
    return send_from_directory(os.path.join(app.static_folder, "dashboard"), 'admin-dashboard.html')

@app.route('/admin/visual')
def visual_admin_dashboard():
    """لوحة التحكم الإدارية المرئية المخصصة"""
    return send_from_directory(os.path.join(app.static_folder, "dashboard"), 'visual-admin-dashboard.html')

@app.route('/api/health')
def health_check():
    """فحص حالة النظام"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": [
            "AI Medical Image Analysis",
            "Doctor License Management", 
            "Review System",
            "Push Notifications",
            "Advanced Appointments",
            "Analytics & Reports"
        ]
    })

# Main entry point for running the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run the app in debug mode



