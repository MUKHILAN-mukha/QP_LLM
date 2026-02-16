import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    timeout: 120000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getSubjects = async () => {
    const response = await api.get('/subjects/');
    return response.data;
};

export const createSubject = async (name) => {
    const response = await api.post('/subjects/', { name });
    return response.data;
};

export const getSubjectDocuments = async (subjectId) => {
    const response = await api.get(`/subjects/${subjectId}/documents`);
    return response.data;
};

export const uploadFile = async (formData) => {
    const response = await api.post('/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const deleteDocument = async (documentId) => {
    const response = await api.delete(`/upload/${documentId}`);
    return response.data;
};

export const chat = async (subjectId, message) => {
    const response = await api.post('/chat/', {
        subject_id: subjectId,
        message
    });
    return response.data;
};

export const getChatHistory = async (subjectId) => {
    const response = await api.get(`/chat/${subjectId}/history`);
    return response.data;
};


export const generateExamPDF = async (subjectId, formattedQuestions = null) => {
    const payload = formattedQuestions ? { formatted_questions: formattedQuestions } : {};
    const response = await api.post(`/chat/${subjectId}/generate-pdf`, payload, {
        responseType: 'blob', // Important for file download
    });
    return response.data;
};

export default api;
