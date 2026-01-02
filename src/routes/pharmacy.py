from flask import Blueprint, request, jsonify
from src.models.user import db, PharmacyOrder, Consultation

pharmacy_bp = Blueprint("pharmacy", __name__)

@pharmacy_bp.route("/order", methods=["POST"])
def create_pharmacy_order():
    data = request.get_json()
    consultation_id = data.get("consultation_id")
    medication_details = data.get("medication_details")
    
    if not consultation_id or not medication_details:
        return jsonify({"message": "Consultation ID and medication details are required"}), 400
    
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    new_order = PharmacyOrder(consultation_id=consultation_id, medication_details=medication_details)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Pharmacy order created successfully", "order_id": new_order.id}), 201

@pharmacy_bp.route("/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json()
    delivery_status = data.get("delivery_status")
    
    if not delivery_status:
        return jsonify({"message": "Delivery status is required"}), 400
    
    order = PharmacyOrder.query.get(order_id)
    if not order:
        return jsonify({"message": "Pharmacy order not found"}), 404
    
    order.delivery_status = delivery_status
    db.session.commit()
    return jsonify({"message": "Order status updated successfully"}), 200

@pharmacy_bp.route("/consultation/<int:consultation_id>", methods=["GET"])
def get_pharmacy_orders_by_consultation(consultation_id):
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({"message": "Consultation not found"}), 404
    
    orders = PharmacyOrder.query.filter_by(consultation_id=consultation_id).all()
    orders_data = []
    for order in orders:
        orders_data.append({
            "id": order.id,
            "medication_details": order.medication_details,
            "order_date": order.order_date.isoformat(),
            "delivery_status": order.delivery_status
        })
    return jsonify(orders_data), 200


from datetime import datetime

@pharmacy_bp.route("/notify_nearby", methods=["POST"])
def notify_nearby_pharmacies():
    """إشعار الصيدليات القريبة بتوفير الدواء"""
    data = request.get_json()
    consultation_id = data.get("consultation_id")
    prescription_details = data.get("prescription_details")
    user_location = data.get("user_location")  # إحداثيات المستخدم
    
    if not consultation_id or not prescription_details:
        return jsonify({"message": "Consultation ID and prescription details are required"}), 400
    
    # محاكاة العثور على الصيدليات القريبة
    nearby_pharmacies = [
        {"id": 1, "name": "صيدلية النور", "distance": "0.5 km", "phone": "+967123456789"},
        {"id": 2, "name": "صيدلية الشفاء", "distance": "1.2 km", "phone": "+967987654321"},
        {"id": 3, "name": "صيدلية الحياة", "distance": "2.0 km", "phone": "+967555666777"}
    ]
    
    # إرسال إشعارات للصيدليات
    notifications_sent = []
    for pharmacy in nearby_pharmacies:
        # محاكاة إرسال الإشعار
        notification = {
            "pharmacy_id": pharmacy["id"],
            "pharmacy_name": pharmacy["name"],
            "prescription_details": prescription_details,
            "consultation_id": consultation_id,
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat()
        }
        notifications_sent.append(notification)
    
    return jsonify({
        "message": "Notifications sent to nearby pharmacies",
        "pharmacies_notified": len(notifications_sent),
        "notifications": notifications_sent
    }), 200

@pharmacy_bp.route("/delivery_request", methods=["POST"])
def request_delivery():
    """طلب توصيل الدواء للمستخدم"""
    data = request.get_json()
    consultation_id = data.get("consultation_id")
    user_id = data.get("user_id")
    delivery_address = data.get("delivery_address")
    prescription_details = data.get("prescription_details")
    preferred_time = data.get("preferred_time")
    
    if not consultation_id or not user_id or not delivery_address:
        return jsonify({"message": "Consultation ID, user ID, and delivery address are required"}), 400
    
    # إنشاء طلب توصيل
    delivery_request = {
        "delivery_id": f"DEL-{consultation_id}-{user_id}",
        "consultation_id": consultation_id,
        "user_id": user_id,
        "delivery_address": delivery_address,
        "prescription_details": prescription_details,
        "preferred_time": preferred_time,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "estimated_delivery": "2-4 hours"
    }
    
    return jsonify({
        "message": "Delivery request created successfully",
        "delivery_request": delivery_request
    }), 201

@pharmacy_bp.route("/pharmacy_response", methods=["POST"])
def pharmacy_response():
    """استجابة الصيدلية لطلب الدواء"""
    data = request.get_json()
    pharmacy_id = data.get("pharmacy_id")
    consultation_id = data.get("consultation_id")
    availability = data.get("availability")  # True/False
    estimated_time = data.get("estimated_time")  # وقت التحضير المتوقع
    notes = data.get("notes", "")
    
    if not pharmacy_id or not consultation_id or availability is None:
        return jsonify({"message": "Pharmacy ID, consultation ID, and availability status are required"}), 400
    
    response = {
        "pharmacy_id": pharmacy_id,
        "consultation_id": consultation_id,
        "availability": availability,
        "estimated_time": estimated_time,
        "notes": notes,
        "response_time": datetime.utcnow().isoformat()
    }
    
    if availability:
        message = "Pharmacy confirmed medication availability"
    else:
        message = "Pharmacy reported medication unavailable"
    
    return jsonify({
        "message": message,
        "pharmacy_response": response
    }), 200

