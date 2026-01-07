import streamlit as st
import re
import time
import pandas as pd
from data_handler import save_candidate_data, get_leaderboard
from question_generator import generate_tech_questions, generate_feedback
from prompts import SYSTEM_PROMPT

# --- Configuration & Styling ---
st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme & UI Components
st.markdown("""
<style>
    /* Dark Theme & Gradient Background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a1d2e 0%, #2d1f3d 100%);
        color: #ffffff;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #11141c;
        border-right: 1px solid #333;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #fff;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-icon {
        font-size: 3rem;
        margin-right: 10px;
    }

    /* Chat Messages */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* User Message Override */
    div[data-testid="stChatMessage"]:nth-child(odd) {
         background-color: rgba(64, 224, 208, 0.1);
         border: 1px solid rgba(64, 224, 208, 0.2);
    }

    /* Progress Tracker (Dark Mode) */
    .progress-step {
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .progress-active {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        font-weight: bold;
        border-left: 4px solid #6dd5fa;
    }
    .progress-inactive {
        background-color: rgba(255,255,255,0.05);
        color: #777;
    }
    
    /* Leaderboard Table */
    .leaderboard-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    .leaderboard-table th {
        text-align: left;
        border-bottom: 1px solid #555;
        padding: 5px;
        color: #aaa;
    }
    .leaderboard-table td {
        padding: 5px;
        border-bottom: 1px solid #333;
    }
    
    /* Deploy Button */
    .deploy-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm TalentScout, your virtual hiring assistant. I'm here to learn more about your professional background and see if you're a great fit for our team. To get started, may I have your full name?"}]
    
if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = 1 # 1: Name, ...

if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}

if "technical_questions" not in st.session_state:
    st.session_state.technical_questions = []

if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

if "technical_answers" not in st.session_state:
    st.session_state.technical_answers = {}

# --- Constants ---
STAGES = {
    1: "Name",
    2: "Email",
    3: "Phone",
    4: "Experience",
    5: "Position",
    6: "Location",
    7: "Tech Stack",
    8: "Generate Questions",
    9: "Technical Interview",
    10: "End"
}

# --- Helper Functions ---
def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_phone(phone):
    # Basic validation: digits, hyphens, plus, spaces, at least 7 chars
    pattern = r"^[\d\+\-\s]{7,20}$"
    return re.match(pattern, phone) is not None

def advance_stage():
    st.session_state.conversation_stage += 1

def process_input(user_input):
    stage = st.session_state.conversation_stage
    info = st.session_state.candidate_info
    
    # Handle Global Exit Commands
    if user_input.lower() in ["goodbye", "exit", "quit", "bye", "thanks", "no thanks"]:
        st.session_state.conversation_stage = 10
        return "Thank you for your time! We have recorded your information. A recruiter will be in touch soon. Have a great day!"

    response = ""
    
    # Logic for each stage
    if stage == 1: # expecting Name
        if len(user_input.strip()) < 2:
            return "Could you please provide your full name?"
        info['full_name'] = user_input
        advance_stage()
        response = f"Nice to meet you, {user_input.split()[0]}! What is your email address?"
        
    elif stage == 2: # expecting Email
        if not validate_email(user_input):
            return "That doesn't look like a valid email. Please try again (e.g., name@example.com)."
        info['email'] = user_input
        advance_stage()
        response = "Got it. What is your phone number?"
        
    elif stage == 3: # expecting Phone
        if not validate_phone(user_input):
            return "Please enter a valid phone number (digits, optionally + or -)."
        info['phone'] = user_input
        advance_stage()
        response = "Great! How many years of professional experience do you have?"
        
    elif stage == 4: # expecting Experience
        info['experience'] = user_input
        advance_stage()
        response = "Understood. What position(s) are you applying for?"
        
    elif stage == 5: # expecting Position
        info['position'] = user_input
        advance_stage()
        response = "Where are you currently located?"
        
    elif stage == 6: # expecting Location
        info['location'] = user_input
        advance_stage()
        response = "Thanks. Finally, briefly list your primary Tech Stack (e.g., Python, React, AWS)."
        
    elif stage == 7: # expecting Tech Stack
        info['tech_stack'] = user_input
        advance_stage() # Move to 8 (Generate)
        # We trigger generation immediately after this response in the refresh cycle or here?
        # Let's say: "Generating questions..."
        response = "Excellent. I'm now generating some tailored technical questions for you. Please wait a moment..."
        
    elif stage == 9: # Answering Technical Questions
        # Store answer for current question
        q_idx = st.session_state.current_question_index
        questions = st.session_state.technical_questions
        
        if q_idx < len(questions):
            # Save answer
            question_text = questions[q_idx]
            st.session_state.technical_answers[question_text] = user_input
            
            # Move to next
            st.session_state.current_question_index += 1
            next_idx = st.session_state.current_question_index
            
            if next_idx < len(questions):
                response = f"Question {next_idx + 1}/{len(questions)}: {questions[next_idx]}"
            else:
                # Finished questions
                advance_stage() # To 10
                # Save Data
                full_data = st.session_state.candidate_info
                full_data['technical_answers'] = st.session_state.technical_answers
                save_candidate_data(full_data)
                
                response = "Thank you! That completes the technical part. We have all your details. Our hiring team will review your profile and get back to you shortly. Have a wonderful day!"
        else:
            response = "Interview complete."

    elif stage == 10:
        response = "The interview is already complete."
        if not st.session_state.analysis_report:
             from question_generator import generate_feedback
             with st.spinner("Analyzing interview session..."):
                 report = generate_feedback(info, st.session_state.messages)
                 st.session_state.analysis_report = report
                 
    return response

# --- Sidebar ---
with st.sidebar:
    st.header("Interview Settings")
    
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi"])
    st.session_state.language = language

    difficulty = st.slider("Difficulty Level", 1, 5, 3)
    st.session_state.difficulty_level = difficulty # Update session state

    if st.button("Clear Conversation", type="primary"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm TalentScout. Let's start over. What is your full name?"}]
        st.session_state.conversation_stage = 1
        st.session_state.candidate_info = {}
        st.session_state.technical_questions = []
        st.session_state.current_question_index = 0
        st.session_state.technical_answers = {}
        st.session_state.analysis_report = None
        st.rerun()
    
    st.markdown("---")
    st.subheader("Interview Progress")
    
    # Progress Bar Widget
    total_stages = 10
    current_stage_num = min(st.session_state.conversation_stage, total_stages)
    st.progress(current_stage_num / total_stages)
    
    # Progress Indicators
    current_stage = st.session_state.conversation_stage
    
    step_1_class = "progress-active" if current_stage <= 7 else "progress-inactive"
    step_2_class = "progress-active" if 8 <= current_stage <= 9 else "progress-inactive"
    step_3_class = "progress-active" if current_stage >= 10 else "progress-inactive"
    
    st.markdown(f'<div class="{step_1_class}">1. Candidate Info</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="{step_2_class}">2. Technical Questions</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="{step_3_class}">3. End Conversation</div>', unsafe_allow_html=True)


# --- Main Layout ---
col1, col2 = st.columns([1, 8])
with col1:
    st.markdown("<div style='font-size: 3rem; text-align: center;'>💼</div>", unsafe_allow_html=True)
with col2:
    st.markdown('<div class="main-header">TalentScout Hiring Assistant</div>', unsafe_allow_html=True)

# --- Chat Area ---
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- Question Generation Trigger ---
if st.session_state.conversation_stage == 8:
    with st.spinner("Analyzing your tech stack and generating questions..."):
        info = st.session_state.candidate_info
        questions = generate_tech_questions(
            tech_stack=info.get('tech_stack', 'General'),
            difficulty=st.session_state.difficulty_level,
            experience=info.get('experience', '1'),
            language=st.session_state.get('language', 'English')
        )
        st.session_state.technical_questions = questions
        st.session_state.current_question_index = 0
        
        # Advance to Interview Stage
        st.session_state.conversation_stage = 9
        
        # Add the first question to chat
        first_q = f"Okay, I've prepared {len(questions)} questions for you. Let's start.\n\nQuestion 1: {questions[0]}"
        st.session_state.messages.append({"role": "assistant", "content": first_q})
        st.rerun()

# --- Input Area ---
if user_input := st.chat_input("Type your response here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Process response
    response = process_input(user_input)
    
    # Add bot message
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

# --- Analysis Report Display ---
if st.session_state.conversation_stage == 10 and st.session_state.analysis_report:
    st.markdown("---")
    st.markdown(st.session_state.analysis_report)


