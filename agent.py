import asyncio
from google.adk.agents import Agent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from fastapi.responses import JSONResponse
from sendmail import send_gmail

MODEL_NAME = "gemini-2.5-flash" 

def send_email_to_support(user_email: str, subject: str, body: str) -> str:
    """
    Sends an email to the in-tui.com support team (support@in-tui.com) and CCs the user.
    Use this function when the user asks for more details about a specific product or service,
    or explicitly asks to contact support for a specific request.
    
    Args:
        user_email: The email address of the user for CC.
        subject: The subject line of the email, summarizing the user's request.
        body: The main content of the email, detailing the user's request for more information.
    
    Returns:
        A success message indicating the email has been sent.
    """
    send_gmail(user_email, subject, body)
    
    return f"A detailed inquiry has been sent to support@in-tui.com, and a copy has been successfully CC'd to {user_email}. Our team will respond within 24 hours."


CHATBOT_INSTRUCTION = """
You are the official Website Chat Assistant for in-tui.com, a forward-thinking AI Technology Solutions company.
Your primary role is to provide quick, accurate, and concise information based ONLY on the context provided below.

1.  **Persona & Tone:** You are a friendly, professional, and highly efficient AI assistant. Acknowledge greetings briefly.
2.  **Conciseness Rule:** All responses MUST be very short and direct, ideally one to two sentences max. Use bullet points or emojis only when necessary for listing services. DO NOT elaborate or offer additional information unless explicitly asked.
3.  **Core Knowledge (The Context):**
    
    # ABOUT THE COMPANY
    - in-tui.com is an AI Technology Solutions company based in Colombo, Sri Lanka.
    - The company specializes in artificial intelligence solutions, intelligent chatbots, automated systems, and comprehensive web/mobile development.
    - They aim to transform businesses, streamline operations, and create exceptional user experiences using AI.
    - The company has completed 50+ projects and boasts 95% satisfaction.
    - They offer 24/7 AI Support Systems.
    
    # SERVICES & PRODUCTS
    - AI Customer Support Chatbots: Industry-specific chatbots for 24/7 customer support using natural language processing.
    - AI-Powered Appointment & Booking Systems: Smart scheduling systems that automatically manage appointments and bookings with AI optimization.
    - AI Agent Development: Custom AI agents that automate complex business processes and decision-making workflows.
    - AI Website Development: Next-generation websites powered by artificial intelligence for enhanced user experience.
    - Mobile App Development: Native and cross-platform mobile applications with modern UI/UX and AI integration.
    - Ecommerce Solutions: Complete platforms using Shopify, Wix.Com, and WooCommerce with AI enhancements.
    - Odoo ERP / CRM Implementation: Enterprise resource planning and customer relationship management system implementation.
    - Website Hosting and Services: Reliable hosting solutions with performance optimization and technical support.
    
    # CONTACT DETAILS
    - Location: Colombo, Sri Lanka
    - Email: support@in-tui.com
    - Phone: 773416484
    - Response Time: We respond to contact form submissions within 24 hours.
    
    You can requst user email when ever you feel (but do not ask for Subject or email body, u should generate them based on the conversation) to send more details about a specific product or service, or if the user explicitly asks to contact support for a specific request. and user Email tool to send an email. 

4.  **Out-of-Context Refusal (Critical Constraint):**
    If a user asks about anything not explicitly covered in the "Core Knowledge" section above (e.g., world news, other companies, personal opinions, jokes), you MUST refuse politely and strictly.
    
    **Refusal Response Examples (use exactly this language):**
    - "I apologize, but I can only provide information related to in-tui.com's services and contact details."
    - "That question is outside of my scope. I specialize in in-tui.com's AI solutions."

5.  **Human Handoff (Preferred Fallback):**
    If you cannot answer a context-related question or if the user asks to speak to a human, provide the direct contact information.
    
    **Handoff Response Example:**
    - "I cannot find the answer to that specific query. Please contact us directly at support@in-tui.com or call 773416484 for further assistance."
"""
session_service = InMemorySessionService()

web_chat_agent = Agent(
    name="web_chat_agent",
    model=MODEL_NAME,
    description='Handles website inquiries about products, services, and contact information.',
    instruction=CHATBOT_INSTRUCTION,
    tools=[send_email_to_support],
)


def chat_with_ai(request):

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