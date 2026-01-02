from flask import Blueprint, request, jsonify
from src.models.user import db, Appointment, User
from datetime import datetime

appointments_bp = Blueprint("appointments", __name__)

@appointments_bp.route("/book", methods=["POST"])
def book_appointment():
    data = request.get_json()
    user_id = data.get("user_id")
    doctor_id = data.get("doctor_id")
    appointment_date = data.get("appointment_date")
    appointment_type = data.get("appointment_type")
    
    # Additional patient information
    patient_name = data.get("patient_name")
    patient_phone = data.get("patient_phone")
    patient_age = data.get("patient_age")
    case_description = data.get("case_description")
    payment_method = data.get("payment_method")
    
    if not user_id or not doctor_id or not appointment_date or not appointment_type:
        return jsonify({"message": "User ID, doctor ID, appointment date, and type are required"}), 400
    
    if not patient_name or not patient_phone:
        return jsonify({"message": "Patient name and phone are required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Parse appointment date
    try:
        appointment_datetime = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({"message": "Invalid appointment date format. Use YYYY-MM-DD HH:MM"}), 400
    
    new_appointment = Appointment(
        user_id=user_id, 
        doctor_id=doctor_id, 
        appointment_date=appointment_datetime, 
        appointment_type=appointment_type,
        patient_name=patient_name,
        patient_phone=patient_phone,
        patient_age=patient_age,
        case_description=case_description,
        payment_method=payment_method
    )
    
    try:
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({
            "message": "Appointment booked successfully", 
            "appointment_id": new_appointment.id,
            "appointment": new_appointment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to book appointment", "error": str(e)}), 500

@appointments_bp.route("/<int:appointment_id>/cancel", methods=["POST"])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    appointment.status = "cancelled"
    try:
        db.session.commit()
        return jsonify({"message": "Appointment cancelled successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to cancel appointment", "error": str(e)}), 500

@appointments_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_appointments(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    appointments = Appointment.query.filter_by(user_id=user_id).all()
    appointments_data = [appointment.to_dict() for appointment in appointments]
    return jsonify(appointments_data), 200

@appointments_bp.route("/<int:appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    return jsonify(appointment.to_dict()), 200

