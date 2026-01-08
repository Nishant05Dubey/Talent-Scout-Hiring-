import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import QUESTION_GENERATION_PROMPT_TEMPLATE

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

FALLBACK_QUESTIONS = [
    "Describe a challenging technical problem you solved recently.",
    "How do you stay updated with the latest technology trends?",
    "Explain the concept of RESTful APIs.",
    "What is your preferred version control workflow?",
    "How do you handle error handling in your code?"
]

def generate_tech_questions(tech_stack: str, difficulty: int, experience: str, language: str = "English") -> list:
    """
    Generates technical questions using Google Gemini Pro.
    Returns a list of questions (strings).
    """
    # Force reload env to pick up key changes without restart
    load_dotenv(override=True)
    api_key_local = os.getenv("GOOGLE_API_KEY")
    
    if not api_key_local:
        # Try finding key in case .env was just created
        import glob
        if os.path.exists(".env"):
             # load_dotenv is already imported globally
             pass

    if not api_key_local:
        print("Warning: GOOGLE_API_KEY not found. Using fallback questions.")
        return FALLBACK_QUESTIONS[:3]
        
    genai.configure(api_key=api_key_local)

    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = QUESTION_GENERATION_PROMPT_TEMPLATE.format(
            num_questions=5, 
            tech_stack=tech_stack,
            experience=experience,
            difficulty=difficulty,
            language=language
        )
        
        response = model.generate_content(prompt)
        text_response = response.text
        
        # improved parsing for JSON in markdown
        cleaned_text = text_response.replace("```json", "").replace("```", "").strip()
        
        try:
            questions = json.loads(cleaned_text)
            if isinstance(questions, list):
                return questions[:5] # Ensure strictly 5
            else:
                return FALLBACK_QUESTIONS
        except json.JSONDecodeError:
            # Simple fallback if JSON parsing fails but text is there
            # split by newlines if it looks like a list
            lines = [l.strip('- ').strip() for l in cleaned_text.split('\n') if l.strip()]
            if lines:
                return lines[:5]
            return FALLBACK_QUESTIONS
            
    except Exception as e:
        print(f"Error generating questions: {e}")
        return FALLBACK_QUESTIONS

def generate_feedback(candidate_info: dict, transcript: list) -> str:
    """
    Generates a final feedback report using Gemini.
    """
    # Force reload env
    # Force reload env
    load_dotenv(override=True)
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    # 1. Helper to format transcript
    formatted_transcript = ""
    for msg in transcript:
        role = msg['role'].upper()
        content = msg['content']
        if role in ['USER', 'ASSISTANT']:
            formatted_transcript += f"{role}: {content}\n"
            
    from prompts import ANALYSIS_PROMPT_TEMPLATE
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        experience=candidate_info.get('experience', 'N/A'),
        position=candidate_info.get('position', 'N/A'),
        tech_stack=candidate_info.get('tech_stack', 'N/A'),
        transcript=formatted_transcript
    )

    # 2. Try Groq First (if key exists)
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful hiring assistant."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}. Falling back to Gemini.")
            # Fall through to Gemini

    # 3. Fallback to Gemini
    if not google_key:
        return "API Key missing. Please ensure .env file exists with GOOGLE_API_KEY or GROQ_API_KEY."

    genai.configure(api_key=google_key)
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing session: {str(e)}"
