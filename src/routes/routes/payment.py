from flask import Blueprint, request, jsonify
from src.models.user import db, Payment, User, Consultation
from datetime import datetime
import uuid

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/create", methods=["POST"])
def create_payment():
    """إنشاء طلب دفع جديد"""
    data = request.get_json()
    user_id = data.get("user_id")
    consultation_id = data.get("consultation_id")
    amount = data.get("amount")
    payment_type = data.get("payment_type")  # "consultation", "prescription", "tests", "visit"
    
    if not user_id or not amount or not payment_type:
        return jsonify({"message": "User ID, amount, and payment type are required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # إنشاء معرف فريد للدفع
    payment_id = str(uuid.uuid4())
    
    new_payment = Payment(
        payment_id=payment_id,
        user_id=user_id,
        consultation_id=consultation_id,
        amount=amount,
        payment_type=payment_type,
        status="pending"
    )
    
    db.session.add(new_payment)
    db.session.commit()
    
    return jsonify({
        "message": "Payment request created successfully",
        "payment_id": payment_id,
        "amount": amount,
        "payment_type": payment_type,
        "status": "pending"
    }), 201

@payment_bp.route("/<payment_id>/process", methods=["POST"])
def process_payment(payment_id):
    """معالجة الدفع"""
    data = request.get_json()
    payment_method = data.get("payment_method")  # "credit_card", "bank_transfer", "mobile_wallet"
    payment_details = data.get("payment_details", {})
    
    if not payment_method:
        return jsonify({"message": "Payment method is required"}), 400
    
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment:
        return jsonify({"message": "Payment not found"}), 404
    
    # محاكاة معالجة الدفع
    payment.payment_method = payment_method
    payment.payment_details = str(payment_details)
    payment.status = "processing"
    payment.processed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "message": "Payment is being processed",
        "payment_id": payment_id,
        "status": "processing"
    }), 200

@payment_bp.route("/<payment_id>/confirm", methods=["POST"])
def confirm_payment(payment_id):
    """تأكيد الدفع"""
    data = request.get_json()
    transaction_id = data.get("transaction_id")
    
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment:
        return jsonify({"message": "Payment not found"}), 404
    
    payment.transaction_id = transaction_id
    payment.status = "completed"
    payment.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "message": "Payment confirmed successfully",
        "payment_id": payment_id,
        "transaction_id": transaction_id,
        "status": "completed"
    }), 200

@payment_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_payments(user_id):
    """الحصول على تاريخ المدفوعات للمستخدم"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    payments = Payment.query.filter_by(user_id=user_id).all()
    payments_data = []
    
    for payment in payments:
        payments_data.append({
            "payment_id": payment.payment_id,
            "amount": payment.amount,
            "payment_type": payment.payment_type,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "created_at": payment.created_at.isoformat(),
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
            "transaction_id": payment.transaction_id
        })
    
    return jsonify(payments_data), 200

@payment_bp.route("/<payment_id>/status", methods=["GET"])
def get_payment_status(payment_id):
    """الحصول على حالة الدفع"""
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment:
        return jsonify({"message": "Payment not found"}), 404
    
    return jsonify({
        "payment_id": payment.payment_id,
        "status": payment.status,
        "amount": payment.amount,
        "payment_type": payment.payment_type,
        "created_at": payment.created_at.isoformat(),
        "completed_at": payment.completed_at.isoformat() if payment.completed_at else None
    }), 200

