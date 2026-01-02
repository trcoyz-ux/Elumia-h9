from flask import Blueprint, request, jsonify
from datetime import datetime

field_teams_bp = Blueprint("field_teams", __name__)

@field_teams_bp.route("/sample_collection", methods=["POST"])
def request_sample_collection():
    """طلب إرسال فريق ميداني لأخذ العينات"""
    data = request.get_json()
    consultation_id = data.get("consultation_id")
    user_id = data.get("user_id")
    test_types = data.get("test_types")  # قائمة بأنواع الفحوصات
    address = data.get("address")
    preferred_time = data.get("preferred_time")
    urgency = data.get("urgency", "normal")  # normal, urgent
    
    if not consultation_id or not user_id or not test_types or not address:
        return jsonify({"message": "Consultation ID, user ID, test types, and address are required"}), 400
    
    # إنشاء طلب فريق ميداني
    request_id = f"FIELD-{consultation_id}-{user_id}"
    
    field_request = {
        "request_id": request_id,
        "consultation_id": consultation_id,
        "user_id": user_id,
        "request_type": "sample_collection",
        "test_types": test_types,
        "address": address,
        "preferred_time": preferred_time,
        "urgency": urgency,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "estimated_arrival": "2-4 hours" if urgency == "normal" else "30-60 minutes"
    }
    
    return jsonify({
        "message": "Field team sample collection request created successfully",
        "field_request": field_request
    }), 201

@field_teams_bp.route("/assign_team", methods=["POST"])
def assign_team():
    """تعيين فريق ميداني لطلب معين"""
    data = request.get_json()
    request_id = data.get("request_id")
    team_member_id = data.get("team_member_id")
    estimated_arrival = data.get("estimated_arrival")
    
    if not request_id or not team_member_id:
        return jsonify({"message": "Request ID and team member ID are required"}), 400
    
    assignment = {
        "request_id": request_id,
        "team_member_id": team_member_id,
        "assigned_at": datetime.utcnow().isoformat(),
        "estimated_arrival": estimated_arrival,
        "status": "assigned"
    }
    
    return jsonify({
        "message": "Team member assigned successfully",
        "assignment": assignment
    }), 200

@field_teams_bp.route("/update_status", methods=["POST"])
def update_field_request_status():
    """تحديث حالة طلب الفريق الميداني"""
    data = request.get_json()
    request_id = data.get("request_id")
    status = data.get("status")  # assigned, in_progress, samples_collected, delivered_to_lab, completed
    notes = data.get("notes", "")
    lab_location = data.get("lab_location")  # موقع المختبر
    
    if not request_id or not status:
        return jsonify({"message": "Request ID and status are required"}), 400
    
    status_update = {
        "request_id": request_id,
        "status": status,
        "notes": notes,
        "lab_location": lab_location,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    if status == "samples_collected":
        status_update["collection_time"] = datetime.utcnow().isoformat()
    elif status == "delivered_to_lab":
        status_update["lab_delivery_time"] = datetime.utcnow().isoformat()
    elif status == "completed":
        status_update["completion_time"] = datetime.utcnow().isoformat()
    
    return jsonify({
        "message": f"Field request status updated to {status}",
        "status_update": status_update
    }), 200

@field_teams_bp.route("/lab_results", methods=["POST"])
def submit_lab_results():
    """إرسال نتائج المختبر للطبيب"""
    data = request.get_json()
    request_id = data.get("request_id")
    consultation_id = data.get("consultation_id")
    lab_results = data.get("lab_results")  # نتائج الفحوصات
    lab_report_url = data.get("lab_report_url")  # رابط التقرير الكامل
    
    if not request_id or not consultation_id or not lab_results:
        return jsonify({"message": "Request ID, consultation ID, and lab results are required"}), 400
    
    results_submission = {
        "request_id": request_id,
        "consultation_id": consultation_id,
        "lab_results": lab_results,
        "lab_report_url": lab_report_url,
        "submitted_at": datetime.utcnow().isoformat(),
        "status": "results_submitted"
    }
    
    return jsonify({
        "message": "Lab results submitted to doctor successfully",
        "results_submission": results_submission
    }), 200

