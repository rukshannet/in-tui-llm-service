from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Local imports
from db_connection import (
    initialize_firestore,
    is_app_registered,
)
from agent import travel_planner_agent

load_dotenv()

# --- INITIALIZATION ---
app = FastAPI()
db = initialize_firestore()
session_service = InMemorySessionService()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
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
    service_id: str = "llm_service" # Use a default for convenience
    category: str = None # Retained for potential future use

# The corrected chat endpoint
@app.post("/chat")
def chat_with_ai(request: ChatRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    session_service = InMemorySessionService()

    # 1. Validation and Authorization
    if not request.message:
        raise HTTPException(status_code=400, detail="Missing required field: message")
    if not request.api_key:
        raise HTTPException(status_code=400, detail="Missing required field: api_key")
    if not request.service_id:
        raise HTTPException(status_code=400, detail="Missing required field: service_id")
    
    # Using the database stub for authorization
    if not is_app_registered(request.api_key, request.service_id):
        raise HTTPException(status_code=401, detail='Unauthorized: Invalid API key or service ID')
    
    # 2. Define the ADK Content object for the user's message
    user_message_content = types.Content(
        role='user',
        parts=[types.Part(text=request.message)]
    )

    session = asyncio.run(session_service.create_session(
        app_name=request.service_id,
        user_id=request.user_id,
        session_id=request.session_id
    ))

    runner = Runner(agent=travel_planner_agent, app_name=request.service_id, session_service=session_service)

    def call_agent(query):
        content = types.Content(role='user', parts=[types.Part(text=request.message)])
        events = runner.run(user_id=request.user_id, session_id=request.session_id, new_message=content)
        
        for event in events:
            print(f"Content: {event.content}")
            if event.is_final_response():
                final_response = event.content.parts[0].text
                print("Agent Response: ", final_response)
        return JSONResponse(content={'response': final_response})

    return call_agent(request.message)