import asyncio
from google.adk.agents import Agent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from fastapi.responses import JSONResponse

session_service = InMemorySessionService()

web_chat_agent = Agent(
    name="web_chat_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a chat agent and a assistant for in-tui, an AI Technology Solutions company. "
        "Your goal is to help users with their queries regarding the company. "
        "YOUR INSTRUCTION HERE BASED ON in-tui.com CONTENT"
        "You can use the available tools to get real-time information."
    ),
)

def chat_with_ai(request):

    user_message_content = types.Content(
        role='user',
        parts=[types.Part(text=request.message)]
    )

    session = asyncio.run(session_service.create_session(
        app_name=request.service_id,
        user_id=request.user_id,
        session_id=request.session_id
    ))

    runner = Runner(agent=web_chat_agent, app_name=request.service_id, session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text=request.message)])
    events = runner.run(user_id=request.user_id, session_id=request.session_id, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text

    return JSONResponse(content={'response': final_response})