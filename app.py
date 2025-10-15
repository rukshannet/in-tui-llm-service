from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from db_connection import (
    initialize_firestore,
    is_app_registered,
    get_prompt_from_firestore
)
from agent import chat_with_ai

# --- INITIALIZATION ---
app = FastAPI()
load_dotenv()
db = initialize_firestore()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello():
    return JSONResponse(content={'message': 'Welcome to LLM Service API'})

@app.get("/health")
def health():
    return JSONResponse(content={'status': '200 OK'})

class ChatRequest(BaseModel):
    user_id: str
    message: str
    api_key: str
    session_id: str
    service_id: str = "llm_service"
    category: str = None 

@app.post("/chat")
def chat_agent(request: ChatRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    if not request.message:
        raise HTTPException(status_code=400, detail="Missing required field: message")
    if not request.api_key:
        raise HTTPException(status_code=400, detail="Missing required field: api_key")
    if not request.service_id:
        raise HTTPException(status_code=400, detail="Missing required field: service_id")

    if not is_app_registered(request.api_key, request.service_id):
        raise HTTPException(status_code=401, detail='Unauthorized: Invalid API key or service ID')

    prompt = get_prompt_from_firestore(request.service_id)
    response = chat_with_ai(request)

    return response



