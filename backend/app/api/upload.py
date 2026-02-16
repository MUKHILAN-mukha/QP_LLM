from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from app.core.database import get_session
from app.models.models import Subject, Document
from app.schemas.schemas import UploadResponse, DocumentType
from app.services.pdf_service import PDFService
from app.services.vector_store import vector_store
from app.config import settings
import os
import shutil
import logging
import uuid
# import magic  # Removed dependency to avoid installation issues on Windows

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    subject_id: int = Form(...),
    document_type: DocumentType = Form(...),
    session: Session = Depends(get_session)
):
    # 0. Validate File Type
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only PDF files are currently supported."
        )

    # 1. Verify Subject
    subject = session.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Subject with ID {subject_id} not found."
        )

    try:
        # 2. Save File (with unique name to avoid overwrite issues)
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Extract Text (Pre-check to ensure it's a valid PDF)
        text = PDFService.extract_text(file_path)
        if not text or len(text.strip()) == 0:
            os.remove(file_path) # Cleanup
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Could not extract text from this PDF. It might be scanned or empty."
            )

        # 4. Create Document Record
        db_doc = Document(
            filename=file.filename,
            file_path=file_path, # Store the unique path
            document_type=document_type,
            subject_id=subject_id
        )
        session.add(db_doc)
        session.commit()
        session.refresh(db_doc)

        # 5. Index in FAISS
        chunk_data = PDFService.split_text(text)
        chunks = [c["text"] for c in chunk_data]
        
        metadatas = [
            {
                "text": c["text"],
                "subject_id": subject_id,
                "document_type": document_type,
                "filename": file.filename,
                "doc_id": db_doc.id,
                "unit": c["unit"],
                "part": c["part"],
                "co": c["co"]
            }
            for c in chunk_data
        ]
        
        # Add to vector store (wrapping in try/except to ensure DB consistency if indexing fails)
        try:
            vector_store.add_texts(subject_id, chunks, metadatas)
        except Exception as vs_e:
            logger.error(f"Vector store indexing failed: {vs_e}")
            # Optional: Rollback DB entry if strict consistency is needed
            # For now, we keep the file but maybe mark it as 'unindexed' in a future schema update
            # Continuing to return success but with a warning log
            
        return UploadResponse(
            filename=file.filename,
            subject=subject.name,
            type=document_type,
            status="Uploaded and Processed Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
        # Attempt cleanup if file was saved but processing failed
        if 'file_path' in locals() and os.path.exists(file_path):
             try:
                 os.remove(file_path)
             except:
                 pass
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    session: Session = Depends(get_session)
):
    # 1. Find document
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found."
        )

    try:
        # 2. Delete file from disk
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            logger.info(f"Deleted file: {doc.file_path}")

        # 3. Clean up Vector Store
        try:
            vector_store.remove_document(doc.subject_id, document_id)
        except Exception as vs_e:
            logger.error(f"Failed to scrub vector store for doc {document_id}: {vs_e}")

        # 4. Delete from DB
        session.delete(doc)
        session.commit()

        return {"status": "success", "message": f"Document '{doc.filename}' deleted successfully."}

    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
