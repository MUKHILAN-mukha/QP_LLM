from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    documents: List["Document"] = Relationship(back_populates="subject")
    messages: List["ChatMessage"] = Relationship(back_populates="subject")

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    file_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    document_type: str # notes or question_bank
    
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")
    subject: Optional[Subject] = Relationship(back_populates="documents")

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str # user or assistant
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")
    subject: Optional[Subject] = Relationship(back_populates="messages")
