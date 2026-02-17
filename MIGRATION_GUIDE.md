
# ExamGen AI: Migration Guide & Deployment

This guide explains how to move your **ExamGen AI** project from your current computer to a new machine.

---

## 🏗️ Phase 1: Preparation on New Machine

### 1. Install Prerequisites
On the **new computer**, install these tools first:
1.  **Git**: [Download Git](https://git-scm.com/downloads) - To clone the code.
2.  **Python 3.10+**: [Download Python](https://www.python.org/downloads/) - For the backend.
3.  **Node.js (LTS)**: [Download Node.js](https://nodejs.org/en/download/) - For the frontend.
4.  **Ollama**: [Download Ollama](https://ollama.com/) - The local AI engine.

### 2. Prepare the AI Model
Once Ollama is installed on the new machine, open a terminal and run:
```bash
ollama pull mistral
```
*(If you used a different model like `llama3` or `gemma` on your old machine, pull that one instead).*

---

## 🚀 Phase 2: Get the Code

### 1. Clone the Repository
Open a terminal in the folder where you want the project:
```bash
git clone https://github.com/MUKHILAN-mukha/QP_LLM.git
cd QP_LLM
```

---

## 📦 Phase 3: Install Dependencies

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Activate Venv:
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Libraries
pip install -r requirements.txt
```

### 2. Frontend Setup
Open a **new terminal** (leave the backend one open):
```bash
cd frontend
npm install
```

---

## 💾 Phase 4: Data Migration (Optional)
**Important**: Your uploaded documents, vector database, and chat history are **NOT** stored in GitHub (for privacy/size reasons).

**If you want to keep your old data:**
1.  Go to your **OLD computer**.
2.  Copy these files/folders from the `QP_LLM/backend` directory:
    *   `database.db` (The SQL database)
    *   `faiss_index/` (The Vector Store folder)
    *   `uploads/` (The raw PDF files)
3.  Paste them into the exact same location in `QP_LLM/backend` on your **NEW computer**.

*If you don't do this, you will start with a fresh, empty system.*

---

## ▶️ Phase 5: Launch

1.  **Start Ollama**: Run `ollama serve` (or just ensure the app is running).
2.  **Start Backend**: `uvicorn app.main:app --reload` (inside `backend` folder, with `venv` active).
3.  **Start Frontend**: `npm run dev` (inside `frontend` folder).

---

## ❓ Troubleshooting
- **"Ollama Connection Refused"**: Make sure Ollama is running in the background.
- **"Missing Modules"**: Ensure you activated `venv` before running the backend.
- **"Empty Chat History"**: You probably didn't copy the `database.db` file from the old machine.
