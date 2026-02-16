import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, RefreshCw, X } from 'lucide-react';
import { uploadFile, getSubjectDocuments, deleteDocument } from '../services/api';
import DocumentTable from './DocumentTable';

const UploadManager = ({ subject }) => {
    const [file, setFile] = useState(null);
    const [docType, setDocType] = useState('notes');
    const [status, setStatus] = useState('idle');
    const [message, setMessage] = useState('');
    const [documents, setDocuments] = useState([]);
    const [loadingDocs, setLoadingDocs] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    useEffect(() => {
        fetchDocuments();
    }, [subject.id]);

    const fetchDocuments = async () => {
        setLoadingDocs(true);
        try {
            const docs = await getSubjectDocuments(subject.id);
            setDocuments(docs);
        } catch (error) {
            console.error("Failed to fetch documents", error);
        } finally {
            setLoadingDocs(false);
        }
    };

    const handleDelete = async (docId) => {
        if (!window.confirm("Are you sure you want to delete this document? This will also remove its associated AI knowledge.")) {
            return;
        }

        try {
            await deleteDocument(docId);
            setStatus('success');
            setMessage('Document deleted successfully.');
            fetchDocuments(); // Refresh list

            setTimeout(() => {
                setStatus('idle');
                setMessage('');
            }, 3000);
        } catch (error) {
            console.error("Failed to delete document", error);
            setStatus('error');
            setMessage("Failed to delete document.");
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const validateAndSetFile = (selectedFile) => {
        if (selectedFile.type === "application/pdf") {
            setFile(selectedFile);
            setStatus('idle');
            setMessage('');
        } else {
            setStatus('error');
            setMessage("Only PDF files are supported.");
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('subject_id', subject.id);
        formData.append('document_type', docType);

        setStatus('uploading');
        try {
            await uploadFile(formData);
            setStatus('success');
            setMessage(`${file.name} uploaded successfully.`);
            setFile(null);
            fetchDocuments(); // Refresh list

            // Clear success message after 3 seconds
            setTimeout(() => {
                setStatus('idle');
                setMessage('');
            }, 3000);
        } catch (error) {
            setStatus('error');
            setMessage("Failed to upload file. Please try again.");
        }
    };

    return (
        <div className="upload-view animate-fade-in custom-scrollbar">
            <div className="glass-card">
                <h1 className="upload-title">Resource Library</h1>
                <p className="upload-description">
                    Populate the knowledge base for <strong>{subject.name}</strong> with PDF materials.
                </p>

                <div className="upload-grid">
                    {/* Upload Section */}
                    <div className="upload-form-section">
                        <div>
                            <label className="form-label">Material Type</label>
                            <div className="type-selector">
                                <button
                                    type="button"
                                    onClick={() => setDocType('notes')}
                                    className={`type-btn ${docType === 'notes' ? 'active' : ''}`}
                                >
                                    Lecture Notes
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setDocType('question_bank')}
                                    className={`type-btn ${docType === 'question_bank' ? 'active' : ''}`}
                                >
                                    Exam Bank
                                </button>
                            </div>
                        </div>

                        <div
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                            className={`drop-zone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf"
                                onChange={handleFileChange}
                                style={{ display: 'none' }}
                            />

                            <div className="drop-content">
                                {file ? (
                                    <div className="file-preview">
                                        <FileText size={40} className="file-icon" />
                                        <p className="file-name">{file.name}</p>
                                        <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                ) : (
                                    <>
                                        <Upload size={32} className="drop-icon" />
                                        <p className="drop-text">Drop PDF File</p>
                                        <p className="drop-subtext">Maximum size: 50MB</p>
                                    </>
                                )}
                            </div>
                        </div>

                        <button
                            onClick={handleUpload}
                            disabled={!file || status === 'uploading'}
                            className="index-btn-premium"
                        >
                            {status === 'uploading' ? (
                                <Loader2 size={18} className="animate-spin" />
                            ) : (
                                "INDEX TO AI KNOWLEDGE"
                            )}
                        </button>

                        {status === 'success' && (
                            <div style={{ color: 'var(--success)', display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.875rem' }}>
                                <CheckCircle size={14} /> {message}
                            </div>
                        )}
                    </div>

                    {/* Document List Section */}
                    <div className="indexes-panel">
                        <div className="indexes-header">
                            <h3 className="section-title">Active Indexes</h3>
                            <button onClick={fetchDocuments} className="refresh-btn">
                                <RefreshCw size={18} className={loadingDocs ? "animate-spin" : ""} />
                            </button>
                        </div>
                        <DocumentTable documents={documents} onDelete={handleDelete} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UploadManager;
