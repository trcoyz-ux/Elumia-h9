from datetime import datetime
import random
import string

def generate_auto_id(prefix, model_class):
    """
    Generates a unique auto-incrementing ID with a prefix.
    The ID is based on the count of existing records for the model.
    
    Args:
        prefix (str): The prefix for the ID (e.g., 'USR', 'CON', 'REC').
        model_class (db.Model): The SQLAlchemy model class.
        
    Returns:
        str: The generated unique ID.
    """
    # Get the current count of records in the table
    # This is a simple approach. In a real-world scenario, a dedicated sequence
    # or a more robust ID generation service would be used to prevent race conditions.
    # For this task, we'll use the count + 1 as the base number.
    try:
        count = model_class.query.count()
    except Exception:
        # Handle case where table might not exist yet (e.g., first run)
        count = 0
        
    next_number = count + 1
    
    # Format the number with leading zeros (e.g., 00001)
    formatted_number = str(next_number).zfill(5)
    
    # Add a short random suffix to enhance uniqueness (optional but good practice)
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    
    return f"{prefix}-{formatted_number}-{random_suffix}"

def generate_user_auto_id(User):
    return generate_auto_id('USR', User)

def generate_consultation_auto_id(Consultation):
    return generate_auto_id('CON', Consultation)

def generate_medical_record_auto_id(MedicalRecord):
    return generate_auto_id('REC', MedicalRecord)

def generate_appointment_auto_id(Appointment):
    # Use the same prefix as consultation as they are related to the same process
    return generate_auto_id('CON', Appointment)
