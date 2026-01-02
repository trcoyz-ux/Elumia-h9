from flask import Blueprint, request, jsonify
from src.models.user import db, MedicalRecord, User
from ..utils import generate_medical_record_auto_id
# import boto3

medical_records_bp = Blueprint("medical_records", __name__)

# Initialize S3 client (example) - commented out for local testing
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id="REMOVED_SENSITIVE_DATA",  # Should be replaced with your access key
#     aws_secret_access_key="REMOVED_SENSITIVE_DATA",  # Should be replaced with your secret access key
#     region_name="YOUR_AWS_REGION"  # Example: "us-east-1"
# )

@medical_records_bp.route("/upload", methods=["POST"])
def upload_medical_record():
    user_id = request.form.get("user_id")
    record_type = request.form.get("record_type")
    file = request.files.get("file")
    
    if not user_id or not record_type or not file:
        return jsonify({"message": "User ID, record type, and file are required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # For local testing, we'll simulate file upload
    file_url = f"local://uploads/{user_id}/{record_type}/{file.filename}"
    
    # bucket_name = "your-medical-records-bucket"
    # file_name = f"{user_id}/{record_type}/{file.filename}"
    
    # try:
    #     s3_client.upload_fileobj(file, bucket_name, file_name)
    #     file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
    # except Exception as e:
    #     return jsonify({"message": f"Failed to upload file to S3: {str(e)}"}), 500
    
    new_record = MedicalRecord(user_id=user_id, record_type=record_type, file_url=file_url)
    new_record.record_auto_id = generate_medical_record_auto_id(MedicalRecord)
    db.session.add(new_record)
    db.session.commit()
    return jsonify({"message": "Medical record uploaded successfully", "record_id": new_record.id, "record_auto_id": new_record.record_auto_id}), 201

@medical_records_bp.route("/<int:record_id>", methods=["GET"])
def get_medical_record(record_id):
    record = MedicalRecord.query.get(record_id)
    if not record:
        return jsonify({"message": "Medical record not found"}), 404
    
    return jsonify({
        "id": record.id,
        "record_auto_id": record.record_auto_id,
        "user_id": record.user_id,
        "record_type": record.record_type,
        "file_url": record.file_url,
        "upload_date": record.upload_date.isoformat(),
        "ai_analysis_report": record.ai_analysis_report
    })

