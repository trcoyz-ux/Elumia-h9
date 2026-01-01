import firebase_admin
from firebase_admin import credentials

try:
    cred = credentials.Certificate('/home/ubuntu/Elumia_Enhanced_Medical_Platform/H9W2AET_for_zip/src/config/firebase-service-account.json')
    firebase_admin.initialize_app(cred)
    print('Firebase has been initialized successfully!')
except Exception as e:
    print(f'An error occurred: {e}')


