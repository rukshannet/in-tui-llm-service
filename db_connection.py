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

def get_prompt_from_firestore():
    try:
        db = initialize_firestore()
        if db:
            doc_ref = db.collection('chatbot_settings').document('in-tui-web-chat-bot')
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get('prompt')
    except Exception as e:
        print(f"Error getting prompt from Firestore: {e}")
    return None