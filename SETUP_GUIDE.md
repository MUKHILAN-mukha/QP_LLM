# ExamGen AI: Setup & Run Guide

**Note**: This project is designed to run locally. Ensure you have the necessary prerequisites installed.

---

## 1. Prerequisites

Before you begin, ensure you have the following installed on your machine:
*   **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
*   **Node.js (v18+)**: [Download Here](https://nodejs.org/en/download/)
*   **Ollama (for AI Models)**: [Download Here](https://ollama.com/)
*   **Git**: [Download Here](https://git-scm.com/downloads)

---

## 2. Installation Steps

### Step 1: Clone the Repository
Open your terminal/command prompt and run:
```bash
git clone https://github.com/MUKHILAN-mukha/QP_LLM.git
cd QP_LLM
```

### Step 2: Backend Setup
Open a terminal in the `backend` folder:
```bash
cd backend
python -m venv venv
```
Activate the virtual environment:
*   **Windows**: `.\venv\Scripts\activate`
*   **Mac/Linux**: `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```
*Note: This may take a few minutes as it downloads PyTorch and other ML libraries.*

### Step 3: Frontend Setup
Open a **new** terminal in the `frontend` folder:
```bash
cd frontend
npm install
```

### Step 4: AI Model Setup
Ensure Ollama is installed. Then pull the required model (Mistral or Gemma):
```bash
ollama pull mistral
```
*Note: You can change the model in `backend/app/config.py` if you prefer another one (e.g., `llama3` or `gemma`).*

---

## 3. Running the Application

You will need **three** terminal windows open to run the full stack:

### Terminal 1: AI Engine
Start the Ollama server (usually runs in background, but good to check):
```bash
ollama serve
```

### Terminal 2: Backend Server
Navigate to `backend` and run:
```bash
# Make sure venv is activated!
uvicorn app.main:app --reload
```
You should see: `INFO: Uvicorn running on http://127.0.0.1:8000`

### Terminal 3: Frontend Client
Navigate to `frontend` and run:
```bash
npm run dev
```
You should see: `Local: http://localhost:5173/`

---

## 4. How to Use
1.  Open your browser and go to `http://localhost:5173`.
2.  **Create a Subject**: Click the "+" icon in the sidebar (e.g., "History 101").
3.  **Upload PDFs**: Drag and drop your lecture notes or textbooks into the upload area. Wait for "Indexing" to complete.
4.  **Chat**: Switch to "Assistant" view (top right toggle).
5.  **Ask Questions**:
    *   *"Give me 5 hard questions from Unit 2"*
    *   *"Summarize Chapter 3"*
    *   *"Create a quiz based on Part A notes"*

---

## 5. Troubleshooting

*   **"Connection Refused" (Backend)**: Ensure `uvicorn` is running and port 8000 is free.
*   **"Ollama Connection Error"**: Ensure `ollama serve` is running and you have pulled the model (`ollama pull mistral`).
*   **"Module Not Found"**: Make sure you activated the virtual environment (`venv`) before running `uvicorn`.

---
*Happy Studying! 🎓*
