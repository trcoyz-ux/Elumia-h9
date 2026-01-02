from flask import Blueprint, request, jsonify
from src.models.user import db, Consultation, User, MedicalRecord

consultation_bp = Blueprint("consultations", __name__)

@consultation_bp.route("/request", methods=["POST"])
def request_consultation():
    data = request.get_json()
    user_id = data.get("user_id")
    medical_record_id = data.get("medical_record_id")
    consultation_type = data.get("consultation_type")
    
    if not user_id or not consultation_type:
        return jsonify({"message": "User ID and consultation type are required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if medical_record_id:
        medical_record = MedicalRecord.query.get(medical_record_id)
        if not medical_record:
            return jsonify({"message": "Medical record not found"}), 404
    
    new_consultation = Consultation(user_id=user_id, medical_record_id=medical_record_id, consultation_type=consultation_type)
    db.session.add(new_consultation)
    db.session.commit()
    return jsonify({"message": "Consultation request submitted successfully", "consultation_id": new_consultation.id}), 201

@consultation_bp.route("/<int:consultation_id>/accept", methods=["POST"])
def accept_consultation(consultation_id):
    data = request.get_json()
    doctor_id = data.get("doctor_id")
    
    if not doctor_id:
        return jsonify({"message": "Doctor ID is required"}), 400
    
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    doctor = User.query.get(doctor_id)
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404
    
    consultation.doctor_id = doctor_id
    consultation.status = "accepted"
    db.session.commit()
    return jsonify({"message": "Consultation accepted successfully"}), 200

@consultation_bp.route("/<int:consultation_id>/complete", methods=["POST"])
def complete_consultation(consultation_id):
    data = request.get_json()
    prescription = data.get("prescription")
    doctor_notes = data.get("doctor_notes")
    
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    consultation.prescription = prescription
    consultation.doctor_notes = doctor_notes
    consultation.status = "completed"
    db.session.commit()
    return jsonify({"message": "Consultation completed successfully"}), 200

@consultation_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_consultations(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    consultations = Consultation.query.filter_by(user_id=user_id).all()
    consultations_data = []
    for consultation in consultations:
        consultations_data.append({
            "id": consultation.id,
            "doctor_id": consultation.doctor_id,
            "medical_record_id": consultation.medical_record_id,
            "status": consultation.status,
            "consultation_type": consultation.consultation_type,
            "request_date": consultation.request_date.isoformat(),
            "prescription": consultation.prescription,
            "doctor_notes": consultation.doctor_notes
        })
    return jsonify(consultations_data), 200


@consultation_bp.route("/<int:consultation_id>/doctor_decision", methods=["POST"])
def doctor_decision(consultation_id):
    """اتخاذ قرار الطبيب بعد الاستشارة"""
    data = request.get_json()
    decision_type = data.get("decision_type")  # "prescription", "additional_tests", "clinic_visit"
    doctor_id = data.get("doctor_id")
    notes = data.get("notes", "")
    
    if not decision_type or not doctor_id:
        return jsonify({"message": "Decision type and doctor ID are required"}), 400
    
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    consultation.doctor_decision = decision_type
    consultation.doctor_notes = notes
    consultation.status = "decision_made"
    db.session.commit()
    
    return jsonify({
        "message": "Doctor decision recorded successfully",
        "decision_type": decision_type,
        "consultation_id": consultation_id
    }), 200

@consultation_bp.route("/<int:consultation_id>/prescription_approval", methods=["POST"])
def prescription_approval(consultation_id):
    """الموافقة على الوصفة الطبية وإصدارها"""
    data = request.get_json()
    prescription_details = data.get("prescription_details")
    doctor_id = data.get("doctor_id")
    
    if not prescription_details or not doctor_id:
        return jsonify({"message": "Prescription details and doctor ID are required"}), 400
    
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    consultation.prescription = prescription_details
    consultation.prescription_status = "approved"
    consultation.status = "prescription_issued"
    db.session.commit()
    
    return jsonify({
        "message": "Prescription approved and issued successfully",
        "consultation_id": consultation_id,
        "prescription_id": f"RX-{consultation_id}-{consultation.user_id}"
    }), 200

@consultation_bp.route("/<int:consultation_id>/additional_tests", methods=["POST"])
def request_additional_tests(consultation_id):
    """طلب فحوصات إضافية"""
    data = request.get_json()
    test_types = data.get("test_types")  # قائمة بأنواع الفحوصات المطلوبة
    doctor_id = data.get("doctor_id")
    urgency = data.get("urgency", "normal")  # normal, urgent
    
    if not test_types or not doctor_id:
        return jsonify({"message": "Test types and doctor ID are required"}), 400
    
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    consultation.additional_tests = ",".join(test_types)
    consultation.test_urgency = urgency
    consultation.status = "tests_requested"
    db.session.commit()
    
    return jsonify({
        "message": "Additional tests requested successfully",
        "consultation_id": consultation_id,
        "test_request_id": f"TEST-{consultation_id}-{consultation.user_id}",
        "tests": test_types
    }), 200

@consultation_bp.route("/<int:consultation_id>/clinic_visit", methods=["POST"])
def schedule_clinic_visit(consultation_id):
    """جدولة زيارة العيادة"""
    data = request.get_json()
    visit_type = data.get("visit_type")  # "in_person", "remote"
    doctor_id = data.get("doctor_id")
    preferred_date = data.get("preferred_date")
    
    if not visit_type or not doctor_id:
        return jsonify({"message": "Visit type and doctor ID are required"}), 400
    
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    consultation.visit_type = visit_type
    consultation.preferred_visit_date = preferred_date
    consultation.status = "visit_scheduled"
    db.session.commit()
    
    return jsonify({
        "message": "Clinic visit scheduled successfully",
        "consultation_id": consultation_id,
        "visit_type": visit_type,
        "appointment_id": f"APPT-{consultation_id}-{consultation.user_id}"
    }), 200

