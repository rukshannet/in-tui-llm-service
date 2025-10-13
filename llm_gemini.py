import google.generativeai as genai

# Configure generative AI
def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

def generate_gemini_response(gemini_model, system_prompt, message):
    messages_gemini = [
        {
            "role": "user",
            "parts": [{"text": system_prompt + "\n\n" + message}]
        }
    ]
    response = gemini_model.generate_content(messages_gemini)
    return response.text  # Ensure only the text is returned, not the model object