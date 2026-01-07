# TalentScout Hiring Assistant - Project Documentation

## 1. Project Overview
The **TalentScout Hiring Assistant** is an intelligent, AI-powered conversational agent designed to streamline the technical interview screening process. Built with Streamlit and powered by Google's Gemini Pro LLM, it automates the initial candidate interaction, parsing professional details and administering a tailored technical assessment.

**Key Capabilities:**
*   **Conversational Data Collection**: Natural language gathering of candidate details (Name, Email, Experience, Tech Stack).
*   **Dynamic Assessment**: Generates strictly five deep, technical questions tailored specifically to the candidate's reported technology stack and experience level.
*   **Multi-Language Support**: Capable of conducting interviews and generating questions in multiple languages (English, Spanish, French, German, Hindi).
*   **Sentiment & Technical Analysis**: Provides an automated post-interview report analyzing the candidate's confidence (sentiment) and technical depth.
*   **Robust Architecture**: Stateless API integration with session management for a smooth user experience.

## 2. Installation Instructions
Follow these steps to set up the application locally.

### Prerequisites
*   Python 3.8 or higher.
*   A Google Cloud API Key for Gemini (AI Studio).

### Steps
1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Nishant05Dubey/Talent-Scout-Hiring-.git
    cd talentscout-hiring-assistant
    ```

2.  **Create a Virtual Environment** (Recommended)
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    *   Rename `.env.example` to `.env`.
    *   Open `.env` and paste your API Key: `GOOGLE_API_KEY=your_key_here`.

5.  **Run the Application**
    ```bash
    streamlit run app.py
    ```
    The application will launch in your default browser at `http://localhost:8501`.

## 3. Usage Guide
The application interface is designed for simplicity.

1.  **Sidebar Settings**:
    *   **Language**: Select your preferred language for the interview.
    *   **Difficulty**: Adjust the slider (1-5) to set the complexity of the questions.
    *   **Clear Conversation**: Use this button to reset the session at any time.

2.  **The Interview Flow**:
    *   **Introduction**: The bot greets you and asks for basic details (Name, Email, Phone).
    *   **Profile Building**: You provide your Experience, Position, Location, and Tech Stack.
    *   **Question Generation**: The system uses your Tech Stack (e.g., "Python, AWS") to generate 5 unique questions.
    *   **Testing**: Answer each question one by one.
    *   **Conclusion**: The bot wraps up and displays a **Final Analysis Report** with your score and sentiment feedback.

## 4. Technical Details

### Technology Stack
*   **Frontend**: Streamlit (Python-based web framework) for rapid UI development.
*   **LLM Integration**: Google Generative AI (`google-generativeai` SDK) accessing the `gemini-pro` model.
*   **State Management**: Native Streamlit `session_state` to persist conversation history and candidate data across re-runs.
*   **Data Storage**: Local JSON file storage (`candidate_data.json`) for persistence.

### Architectural Decisions
*   **Stateless Functions**: The `generate_tech_questions` and `generate_feedback` functions are decoupled from the UI, making them testable and reusable.
*   **Hot-Reloading Configuration**: The application includes logic to force-reload environment variables (`dotenv`), allowing users to update API keys without restarting the server—a critical usability feature.

## 5. Prompt Design
The core intelligence relies on structured prompt engineering.

### Information Gathering
We utilize a **System Prompt** that defines the persona ("Professional Recruiter") and enforces a step-by-step data collection protocol. This prevents the bot from asking all 7 questions at once, ensuring a natural conversation flow.

### Question Generation
We use a **Few-Shot Prompting** strategy with strict output constraints:
*   **Context**: "As a Senior Technical Recruiter..."
*   **Variables**: Injects user-specific data (`{tech_stack}`, `{experience}`, `{difficulty}`).
*   **Constraint**: "Output MUST be a valid JSON array of strings."
*   **Impact**: This guarantees the code can programmatically parse exactly 5 questions to display them individually, rather than receiving a blob of text.

### Sentiment Analysis
The final report uses a **Chain-of-Thought** style prompt:
1.  Ingest the full conversation transcript.
2.  Analyze tone (Sentiment).
3.  Evaluate answer correctness (Technical Rating).
4.  Synthesize into a Markdown report.

## 6. Challenges & Solutions

| Challenge | Solution |
| :--- | :--- |
| **Handling API Key Errors** | Users often forgot to rename `.env` or added keys late. We implemented dynamic environment reloading logic in the Python code to catch this without crashing. |
| **JSON Parsing Reliability** | LLMs sometimes add Markdown backticks (```json) to outputs. We added a robust cleaning layer that strips these artifacts before parsing the list. |
| **State Persistence** | Streamlit re-runs the entire script on every interaction. We used complex `session_state` logic to track the exact "Conversation Stage" (0-10) to maintain flow. |
| **UnboundLocalError** | During refactoring, a variable scope issue occurred. We resolved this by cleaning up global vs. local import statements in the generator module. |
