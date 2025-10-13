import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from llm_gemini import configure_gemini, generate_gemini_response
from db_connection import (
    initialize_firestore,
    get_system_prompt_from_firestore,
)
from dotenv import load_dotenv

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

@app.get("/chat")
async def chat():
    chatbot_name = "in-tui-web-chat-bot"
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        prompt = get_system_prompt_from_firestore(db, chatbot_name)
        return JSONResponse(content={"chatbot_name": chatbot_name, "prompt": prompt})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

