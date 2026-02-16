from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.schemas.schemas import ChatRequest, ChatResponse, ChatMessageResponse
from app.services.rag_service import rag_service
from app.models.models import Subject, ChatMessage
from app.core.database import get_session
from sqlmodel import Session, select

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, session: Session = Depends(get_session)):
    # Verify subject exists
    subject = session.get(Subject, request.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # 1. Save User Message
    user_msg = ChatMessage(role="user", content=request.message, subject_id=request.subject_id)
    session.add(user_msg)
    session.commit()
    session.refresh(user_msg)

    # 2. Retrieve history for context (optional, RAG service uses vector store primarily)
    # We could pass recent history to the LLM if we wanted multi-turn context
    history_msgs = session.exec(select(ChatMessage).where(ChatMessage.subject_id == request.subject_id).order_by(ChatMessage.created_at)).all()
    history = [{"role": m.role, "content": m.content} for m in history_msgs]
    
    # 3. Generate response
    response_data = rag_service.generate_response(request.subject_id, request.message, history)
    
    # 4. Save Assistant Message
    assistant_msg = ChatMessage(role="assistant", content=response_data["answer"], subject_id=request.subject_id)
    session.add(assistant_msg)
    session.commit()
    session.refresh(assistant_msg)
    
    return ChatResponse(
        answer=response_data["answer"],
        context_used=response_data["context_used"],
        message_id=assistant_msg.id
    )

@router.get("/{subject_id}/history", response_model=List[ChatMessageResponse])
def get_history(subject_id: int, session: Session = Depends(get_session)):
    messages = session.exec(select(ChatMessage).where(ChatMessage.subject_id == subject_id).order_by(ChatMessage.created_at)).all()
    return messages

from pydantic import BaseModel
class PDFRequest(BaseModel):
    formatted_questions: Optional[dict] = None

@router.post("/{subject_id}/generate-pdf")
def generate_pdf(subject_id: int, request: PDFRequest = None, session: Session = Depends(get_session)):
    # 1. Verify Subject
    subject = session.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # 2. Use Provided Content OR Generate New
    if request and request.formatted_questions:
        exam_data = request.formatted_questions
    else:
        # Fallback to auto-generation if no context provided (e.g. direct API access)
        exam_data = rag_service.generate_structured_exam(subject_id)
    
    # 3. Generate PDF Binary
    from app.services.pdf_generator import pdf_generator
    pdf_buffer = pdf_generator.create_pdf(subject.name, exam_data)
    
    # 4. Return as File Download
    from fastapi import Response
    pdf_bytes = pdf_buffer.getvalue()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Exam_{subject.name}.pdf",
            "Content-Length": str(len(pdf_bytes))
        }
    )
