from flask import Blueprint, request, jsonify
from src.models.user import db, Notification, User

notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("/test", methods=["GET"])
def notifications_test():
    return jsonify({"message": "Notifications Service is running", "status": "ok"}), 200

@notifications_bp.route("/send", methods=["POST"])
def send_notification():
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")
    
    if not user_id or not message:
        return jsonify({"message": "User ID and message are required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    new_notification = Notification(user_id=user_id, message=message)
    db.session.add(new_notification)
    db.session.commit()
    return jsonify({"message": "Notification sent successfully", "notification_id": new_notification.id}), 201

@notifications_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_notifications(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    notifications = Notification.query.filter_by(user_id=user_id).all()
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            "id": notification.id,
            "message": notification.message,
            "timestamp": notification.timestamp.isoformat(),
            "is_read": notification.is_read
        })
    return jsonify(notifications_data), 200

@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
def mark_notification_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({"message": "Notification not found"}), 404
    
    notification.is_read = True
    db.session.commit()
    return jsonify({"message": "Notification marked as read"}), 200

