
# 🚀 ExamGen AI: Deployment Guide (New Computer)

Follow this guide to move and run this project on a completely new computer.

## 1. Prerequisites (Install these first)
Before copying the code, install these tools on the new machine:

1.  **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
    *   *Check "Add Python to PATH" during installation.*
2.  **Node.js (v18+)**: [Download Here](https://nodejs.org/en/download/)
3.  **Git**: [Download Here](https://git-scm.com/downloads)
4.  **Ollama (AI Engine)**: [Download Here](https://ollama.com/)

---

## 2. Setup AI Engine (Ollama)
1.  Install Ollama and run it.
2.  Open a terminal (Command Prompt or PowerShell) and run:
    ```bash
    ollama pull mistral
    ```
    *(This downloads the brain of the AI. It is about 4GB).*

---

## 3. Clone & Install Project

### Step A: get the Code
Open Terminal/Command Prompt in the folder where you want the project:
```bash
git clone https://github.com/MUKHILAN-mukha/QP_LLM.git
cd QP_LLM
```

### Step B: Setup Backend (Python)
Navigate to the backend folder:
```bash
cd backend
```

Create a virtual environment (keeps dependencies isolated):
```bash
python -m venv venv
```

Activate it:
*   **Windows**: `.\venv\Scripts\activate`
*   **Mac/Linux**: `source venv/bin/activate`

Install libraries:
```bash
pip install -r requirements.txt
```
*(Wait for it to finish. It installs FastAPI, PyTorch, etc.)*

### Step C: Setup Frontend (React)
Open a **NEW** terminal window, navigate to the project folder, then to frontend:
```bash
cd QP_LLM/frontend
npm install
```

---

## 4. Running the App (Daily Use)

You need **two** terminal windows running at the same time.

**Terminal 1: Backend**
```bash
cd QP_LLM/backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2: Frontend**
```bash
cd QP_LLM/frontend
npm run dev
```

Then open your browser to: **`http://localhost:5173`**

---

## 5. Deployment FAQ

**Q: Can I run this offline?**
A: Yes! Once `ollama pull mistral` is done and `pip install` / `npm install` are finished, you don't need internet.

**Q: How do I update the code?**
A: Run `git pull origin main` inside the `QP_LLM` folder.

**Q: My PDF download is stuck?**
A: Ensure the Backend terminal is running and shows no errors.
