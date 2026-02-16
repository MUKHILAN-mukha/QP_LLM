from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SubjectCreate(BaseModel):
    name: str

class SubjectResponse(BaseModel):
    id: int
    name: str

class DocumentType(str, Enum):
    NOTES = "notes"
    QUESTION_BANK = "question_bank"

class DocumentResponse(BaseModel):
    id: int
    filename: str
    document_type: str
    uploaded_at: datetime

class UploadResponse(BaseModel):
    filename: str
    subject: str
    type: DocumentType
    status: str

class ChatRequest(BaseModel):
    subject_id: int
    message: str
    # History now managed by backend, but we can still accept client context if needed
    # history: List[dict] = [] 

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

class ChatResponse(BaseModel):
    answer: str
    context_used: List[str]
    message_id: int
