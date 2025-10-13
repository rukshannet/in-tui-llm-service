import firebase_admin
from firebase_admin import credentials, firestore
import os
import time
import asyncio

# Firebase setup
def initialize_firestore():
    try:
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        print(f"[DEBUG] FIREBASE_CREDENTIALS={cred_path}")
        if cred_path:
            cred = credentials.Certificate(cred_path)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
                print("[DEBUG] Firebase initialized")
            else:
                print("[DEBUG] Firebase already initialized")
            return firestore.client()
        else:
            print("[DEBUG] No credential path found")
            return None
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        return None

async def get_system_prompt_from_firestore(db, chatbot_name):
    try:
        print(f"[DEBUG] Fetching system prompt for chatbot: {chatbot_name}")
        t0 = time.time()
        doc_ref = db.collection('chatbot_settings').document(chatbot_name)
        print(f"[DEBUG] doc_ref created in {time.time() - t0:.4f} seconds")
        
        t1 = time.time()
        doc = await asyncio.to_thread(doc_ref.get)
        print(f"[DEBUG] doc_ref.get() completed in {time.time() - t1:.4f} seconds")

        if doc.exists:
            t2 = time.time()
            data = await asyncio.to_thread(doc.to_dict)
            print(f"[DEBUG] doc.to_dict() completed in {time.time() - t2:.4f} seconds")
            
            prompt = data.get("prompt", "")
            if not prompt:
                print(f"[DEBUG] 'prompt' field not found for chatbot: {chatbot_name}")
                raise ValueError(f"'prompt' field not found for chatbot: {chatbot_name}")
            
            print(f"[DEBUG] Returning prompt in {time.time() - t0:.4f} seconds")
            return prompt
        else:
            print(f"[DEBUG] System prompt document does not exist for chatbot: {chatbot_name}")
            raise ValueError("System prompt document does not exist.")
    except Exception as e:
        print(f"[DEBUG] Error fetching system prompt: {e}")
        raise e

async def get_chat_history_from_firestore(db, chatbot_name):
    try:
        history_ref = db.collection('chatbot_settings').document(chatbot_name).collection('history').order_by('timestamp').limit(50)
        docs = await asyncio.to_thread(history_ref.stream)
        history = [doc.to_dict() for doc in docs]
        return history
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        raise e

async def save_chat_history_to_firestore(db, chatbot_name, user_message, model_response):
    try:
        history_ref = db.collection('chatbot_settings').document(chatbot_name).collection('history')
        await asyncio.to_thread(
            history_ref.add,
            {
                'user_message': user_message,
                'model_response': model_response,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
        )
    except Exception as e:
        print(f"Error saving chat history: {e}")
        raise e

async def clear_chat_history_from_firestore(db, chatbot_name):
    try:
        history_ref = db.collection('chatbot_settings').document(chatbot_name).collection('history')
        docs = await asyncio.to_thread(history_ref.stream)
        
        # For deleting multiple documents, it's more efficient to use a batch operation.
        # However, to keep the change minimal and focused on async, we'll thread the loop.
        # A better implementation would use batched writes.
        delete_tasks = [asyncio.to_thread(doc.reference.delete) for doc in docs]
        await asyncio.gather(*delete_tasks)

    except Exception as e:
        print(f"Error clearing chat history: {e}")
        raise e
