from flask import Blueprint, request, jsonify
from src.models.user import db, User
from ..utils import generate_user_auto_id
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)
    new_user.user_auto_id = generate_user_auto_id(User)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "user_auto_id": new_user.user_auto_id}), 201

@user_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({"message": "Login successful", "user_id": user.id}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@user_bp.route("/kyc/<int:user_id>", methods=["POST"])
def verify_kyc(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user.kyc_verified = True
    db.session.commit()
    return jsonify({"message": "User KYC verified successfully"}), 200

