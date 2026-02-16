from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import subjects, upload, chat
from app.config import settings
from app.core.database import create_db_and_tables

app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Routers
app.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Exam Gen AI API"}
