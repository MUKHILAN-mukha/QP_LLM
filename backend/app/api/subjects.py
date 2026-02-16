from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.models import Subject, Document
from app.schemas.schemas import SubjectCreate, SubjectResponse, DocumentResponse

router = APIRouter()

@router.post("/", response_model=SubjectResponse)
def create_subject(subject: SubjectCreate, session: Session = Depends(get_session)):
    db_subject = Subject(name=subject.name)
    try:
        session.add(db_subject)
        session.commit()
        session.refresh(db_subject)
        return db_subject
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail="Subject already exists or invalid data.")

@router.get("/", response_model=List[SubjectResponse])
def read_subjects(session: Session = Depends(get_session)):
    subjects = session.exec(select(Subject)).all()
    return subjects

@router.get("/{subject_id}/documents", response_model=List[DocumentResponse])
def read_subject_documents(subject_id: int, session: Session = Depends(get_session)):
    documents = session.exec(select(Document).where(Document.subject_id == subject_id)).all()
    return documents
