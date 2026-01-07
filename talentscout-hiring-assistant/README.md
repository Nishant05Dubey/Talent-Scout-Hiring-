# TalentScout Hiring Assistant

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange.svg)

## Project Overview

TalentScout is a production-ready, AI-powered hiring assistant chatbot built with Streamlit and Google's Gemini Pro model. It automates the initial screening process for technical candidates by collecting personal details, analyzing their tech stack, and dynamically generating tailored technical interview questions. The application features a professional dark-themed UI, real-time leaderboard, and robust data handling.

## Features List

-   **Intelligent Conversation Flow**: Seamlessly guides candidates through data collection (Name, Email, Phone, etc.).
-   **Dynamic Question Generation**: Uses Google Gemini to create unique technical questions based on the candidate's specific tech stack and experience level.
-   **Conversation Context**: Maintains state throughout the interview session.
-   **Real-time Leaderboard**: Tracks and ranks candidates based on profile completeness and response quality (simulated scoring).
-   **Robust Validation**: Regex-based validation for emails and phone numbers.
-   **Dark Mode UI**: Professional, aesthetically pleasing dark gradient interface.
-   **Production Ready**: Includes error handling, modular code structure, and local data persistence.

## Installation Instructions

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd talentscout-hiring-assistant
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## API Key Setup

This project uses Google's Generative AI (Gemini). You need an API key from Google AI Studio.

1.  Get your key from [Google AI Studio](https://aistudio.google.com/).
2.  Rename `.env.example` to `.env`.
3.  Add your key:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

## Usage Guide

1.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

2.  **Interact with the Bot**
    - The bot will greet you. Enter your details as requested.
    - Select your difficulty level in the sidebar (optional).
    - Provide your Tech Stack (e.g., "Python, Django, React").
    - Answer the generated technical questions.

3.  **View Leaderboard**
    - The sidebar updates in real-time with top candidates.

## Technical Architecture

The application follows a modular structure:
-   **`app.py`**: Main entry point. Handles Streamlit UI rendering, session state management, and the central conversation loop.
-   **`question_generator.py`**: Abstraction layer for Google Gemini API. Handles prompt construction and JSON parsing.
-   **`data_handler.py`**: Manages local JSON storage (`candidate_data.json`) and calculates leaderboard scores.
-   **`prompts.py`**: Stores system prompts and templates to separate logic from content.

## Prompt Design Explanation

-   **System Prompt**: Defines the persona ("Professional Recruiter") and sets strict boundaries (one question at a time, polite refusal of off-topic chat).
-   **Question Generation Prompt**: Uses Few-Shot prompting principles to instruct the LLM to output valid JSON arrays, ensuring the code can programmatically parse specific questions without regex messiness.

## Tech Stack Used

-   **Frontend**: Streamlit (Python)
-   **LLM**: Google Gemini Pro (`google-generativeai`)
-   **Data Storage**: JSON (Local Flat File)
-   **Environment**: `python-dotenv`

## Challenges & Solutions

-   **Challenge**: Getting valid JSON from the LLM.
    -   **Solution**: Used a strict prompt template asking for a JSON array and added a cleaning function to strip markdown code blocks before parsing.
-   **Challenge**: State Management in Streamlit.
    -   **Solution**: Utilized `st.session_state` extensively to track the conversation stage (0-10) and store cumulative user data.

## Future Enhancements

-   **Resume Parsing**: Allow users to upload PDF resumes.
-   **Voice Interface**: Add speech-to-text for audio responses.
-   **Database Integration**: Migrate from JSON to PostgreSQL/SQLite for scalability.
-   **Automated Grading**: Use the LLM to grade the technical answers and update the leaderboard score dynamically.

## Data Privacy Compliance

-   Candidate data is stored locally in `candidate_data.json`.
-   No data is sent to third parties other than the prompt content (Tech Stack) sent to Google Gemini for question generation. PII is kept local.
-   Timestamps are recorded for audit purposes.

## License

MIT License. See LICENSE file for details.
