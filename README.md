# Exam Gen AI

A subject-scoped RAG-based AI Question Paper Generator.
Builds on FastAPI, React, Hugging Face Inference, and FAISS.

## Features
- **Subject Management**: Create separate workspaces for different subjects.
- **RAG-based Generation**: Upload notes and question banks to generate context-aware questions.
- **Strict Scoping**: Questions are generated ONLY from uploaded content for the specific subject.
- **Premium UI**: Modern, dark-mode interface built with React.

## Prerequisites
- Python 3.8+
- Node.js 16+
- Hugging Face API Token

## Setup

### 1. Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create virtual environment (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Environment:
   - Rename `.env.example` to `.env`
   - Add your `HUGGINGFACE_API_KEY` in `.env`

5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   Server will run at `http://localhost:8000`.

### 2. Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   App will run at `http://localhost:5173`.

## Usage
1. Open the frontend app.
2. Click "+" in the sidebar to create a subject (e.g., "Physics").
3. Select the subject.
4. Go to "Uploads" tab.
5. Upload your PDF notes or question banks.
6. Switch to "Chat" tab.
7. Ask questions like "Generate 5 two-mark questions from Unit 1".

## Tech Stack
- **Backend**: FastAPI, SQLModel, PyMuPDF, SentenceTransformers, FAISS
- **Frontend**: React, Vite, Axios, Lucide React, React Markdown
- **AI**: Hugging Face Inference API (Zephyr-7b-beta)
 
