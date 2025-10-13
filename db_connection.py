import os
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase setup
def initialize_firestore():
    try:
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        if cred_path:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        else:
            return None
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        return None

def get_system_prompt_from_firestore(db, chatbot_name):
    try:
        doc_ref = db.collection('chatbot_settings').document(chatbot_name)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            prompt = data.get("prompt", "")
            if not prompt:
                raise ValueError(f"'prompt' field not found for chatbot: {chatbot_name}")
            return prompt
        else:
            raise ValueError("System prompt document does not exist.")
    except Exception as e:
        print(f"Error fetching system prompt: {e}")
        raise e
