import firebase_admin
from firebase_admin import credentials, firestore
import os
import time
import asyncio

# Firebase setup
def initialize_firestore():
    try:
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        if cred_path:
            cred = credentials.Certificate(cred_path)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            return firestore.client()
        else:
            return None
    except Exception as e:
        return None

def get_prompt_from_firestore(service_id):
    try:
        db = initialize_firestore()
        if db:
            doc_ref = db.collection('chatbot_settings').document(service_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                prompt = data.get('prompt')
                chat_count = data.get('chat_count')
                return {
                    'prompt': prompt,
                    'chat_count': chat_count
                }
    except Exception as e:
        print(f"Error getting prompt from Firestore: {e}")
    return None

def is_app_registered(api_key: str, appId: str) -> bool:
    try:
        db = initialize_firestore()
        if db:
            doc_ref = db.collection('app_registration').document(appId)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return data.get('api_key') == api_key
            return False
    except Exception as e:
        print(f"Error checking app registration: {e}")
    return False
