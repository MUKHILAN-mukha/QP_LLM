# ExamGen AI: Comprehensive Project Report

## 1. Executive Summary
**ExamGen AI** is an advanced, privacy-focused educational tool designed to function as an intelligent study assistant. By leveraging **Retrieval-Augmented Generation (RAG)**, it allows students to interact with their own academic materials (PDFs) to generate study questions, summaries, and answers. The system is engineered to run entirely on local hardware, ensuring **zero data leakage**, **no API costs**, and **offline availability**.

---

## 2. System Workflow & Architecture

### 2.1 The "RAG" Workflow
The core of ExamGen AI follows a strict RAG pipeline to ensure accuracy:
1.  **Ingestion**: User uploads a PDF (e.g., "Data Science Unit 1").
2.  **Extraction**: The backend extracts text using `PyPDF2` and cleans it (removing headers/footers).
3.  **Chunking**: The text is split into smaller, overlapping segments (chunks) using `RecursiveCharacterTextSplitter`. This ensures context isn't lost at cut-off points.
4.  **Embedding**: Each chunk is converted into a numerical vector (embedding) using a local `SentenceTransformer` model (`all-MiniLM-L6-v2`).
5.  **Storage**: These vectors are stored in **ChromaDB**, segmented by `Subject ID` for isolation.
6.  **Retrieval**: When a user asks a question, the system converts the query into a vector and finds the top 25 most similar chunks from the database.
7.  **Generation**: The retrieved chunks + the user's question are sent to a local LLM (**Ollama**), which generates a natural language response strictly based on the provided chunks.

### 2.2 Tech Stack
*   **Backend**: Python (FastAPI) - Chosen for speed and async capabilities.
*   **Frontend**: React (Vite) + Glassmorphism UI - For a modern, responsive user experience.
*   **Database**: SQLite (Metadata) + ChromaDB (Vector Store).
*   **AI Engine**: Ollama (Running Mistral/Gemma) + Sentence Transformers (Embeddings).

---

## 3. The Pivot from Cloud AI (HuggingFace) to Local AI

### 3.1 Initial Approach: HuggingFace API
Initially, the project utilized the **HuggingFace Inference API** for both embeddings and text generation. While convenient, several critical issues emerged:
*   **Rate Limiting**: The free tier APIs have strict rate limits (e.g., 10 requests/hour), causing the app to crash or hang during testing.
*   **Cold Starts**: Serverless models often had "cold start" latency, taking 10-20 seconds to respond to the first query.
*   **Data Privacy**: Sending exam papers and private notes to a third-party cloud API raised potential privacy concerns.
*   **Reliability**: The API helper library (`huggingface_hub`) occasionally threw connection timeouts or `ModelOverloaded` errors unpredictable during demos.

### 3.2 The Solution: Local-First Strategy
To resolve these bottlenecks, we migrated to a **Local-First Architecture**:
*   **Embeddings**: Switched to `sentence-transformers` running locally on the CPU. It is fast, free, and has no rate limits.
*   **LLM**: Integrated **Ollama** to run models like Mistral 7B directly on the user's machine.
*   **Result**: 
    *   **Zero Latency**: No network round-trips.
    *   **Unlimited Usage**: Students can generate thousands of questions without hitting a paywall.
    *   **Full Privacy**: Data never leaves the laptop.

---

## 4. Advanced Features Developed

### 4.1 "Strict Grounding" Protocol
A common issue with LLMs is "hallucination" (making things up). We implemented a strict **System Prompt** that forces the AI to answer *only* using the uploaded context. If the answer isn't in the notes, it politely refuses, ensuring academic accuracy.

### 4.2 Creative Mode
Recognizing the need for flexibility, we added a **Creative Intent Detection** layer. If a user asks to "create", "invent", or "generate" new questions, the system unlocks its creative capabilities, allowing it to synthesize novel questions based on the patterns found in the notes.

### 4.3 Deterministic vs. Random Shuffle
To handle different user needs:
*   **Study Mode**: Queries for "best" or "toughest" questions use **Deterministic Retrieval**, preserving the original ranking of the most relevant results.
*   **Quiz Mode**: General requests (e.g., "give me 5 questions") use **Randomized Shuffling** to ensure a fresh set of questions every time.

---

## 5. Future Roadmap & Upgrades

### 5.1 Multi-Modal RAG (Vision)
**Goal**: Enable the system to understand diagrams, flowcharts, and handwritten equations.
**Plan**: Integrate **LLaVA (Language-and-Vision Assistant)** to process PDF images alongside text, allowing users to ask questions about charts or diagrams in their notes.

### 5.2 Collaborative Knowledge Bases
**Goal**: Allow study groups to share resources.
**Plan**: Implement peer-to-peer (P2P) synchronization of vector stores, allowing a class representative to upload notes once, and the entire class to sync the processed knowledge base instantly.

### 5.3 AI Auto-Grading
**Goal**: Allow students to attempt answers and get instant feedback.
**Plan**: Users can type their answers to generated questions. The AI will then semantically compare their answer against the "Golden Answer" from the notes and provide a grade (0-10) with constructive feedback on what key points were missed.

### 5.4 Cross-Encoder Re-Ranking
**Goal**: Improve retrieval precision to near-perfect levels.
**Plan**: Add a second-stage "Re-Ranker" (using a Cross-Encoder model). This is slower but much more accurate than simple vector similarity, ensuring the top 3 results are always the exact answer paragraphs.

---
*Generated for Academic Assessment - ExamGen AI Team*
