import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from llm_gemini import configure_gemini, generate_gemini_response
from db_connection import (
    initialize_firestore,
    get_system_prompt_from_firestore,
    save_chat_history_to_firestore,
)
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLMs
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gemini_config = configure_gemini(GOOGLE_API_KEY)

# Initialize Firestore
db = initialize_firestore()

@app.get("/")
async def hello():
    return JSONResponse(content={'message': 'Welcome to LLM Service API'})

@app.get("/health")
async def health():
    return JSONResponse(content={'status': '200 OK'})

class ChatRequest(BaseModel):
    message: str
    pre_message: str = None
    api_key: str
    service_id: str = None
    category: str = None

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:

        if not request.message:
            return JSONResponse({'error': 'Missing required field: message'}), 400
        if not request.api_key:
            return JSONResponse({'error': 'Missing required field: api_key'}), 400
        if not request.service_id:
            return JSONResponse({'error': 'Missing required field: service_id'}), 400

        ai_response = generate_gemini_response(gemini_config, "you are a helpful chatbot", request.message)

        return JSONResponse(content={
            "pre_message": request.message,
            "response": ai_response
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
