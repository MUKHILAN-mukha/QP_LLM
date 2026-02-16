import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import UploadManager from './components/UploadManager';
import Layout from './components/Layout';
import { getSubjects, createSubject } from './services/api';
import { BookOpen, Upload, MessageSquare, Menu, Sparkles } from 'lucide-react';
import './index.css';

function App() {
  const [subjects, setSubjects] = useState([]);
  const [activeSubject, setActiveSubject] = useState(null);
  const [view, setView] = useState('chat'); // 'chat' or 'upload'

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const data = await getSubjects();
      setSubjects(data);
      if (data.length > 0 && !activeSubject) {
        setActiveSubject(data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch subjects", error);
    }
  };

  const handleCreateSubject = async (name) => {
    try {
      const newSubject = await createSubject(name);
      setSubjects([...subjects, newSubject]);
      setActiveSubject(newSubject);
    } catch (error) {
      alert("Failed to create subject");
    }
  };


  return (
    <Layout
      sidebar={
        <Sidebar
          subjects={subjects}
          activeSubject={activeSubject}
          onSelectSubject={setActiveSubject}
          onCreateSubject={handleCreateSubject}
        />
      }
    >
      {/* Top Header */}
      <header className="app-header">
        <div className="header-left">
          <div className="header-icon-wrapper">
            {view === 'chat' ? <MessageSquare size={18} /> : <Upload size={18} />}
          </div>
          <div>
            <h2 className="header-title">
              {activeSubject ? activeSubject.name : "Select a Subject"}
            </h2>
            <p className="header-subtitle">
              {view === 'chat' ? 'Interactive AI Assistant' : 'Knowledge Base Control'}
            </p>
          </div>
        </div>

        {activeSubject && (
          <div className="view-toggle">
            <button
              onClick={() => setView('chat')}
              className={`toggle-btn ${view === 'chat' ? 'active' : ''}`}
            >
              <MessageSquare size={16} />
              <span>Assistant</span>
            </button>
            <button
              onClick={() => setView('upload')}
              className={`toggle-btn ${view === 'upload' ? 'active' : ''}`}
            >
              <Upload size={16} />
              <span>Library</span>
            </button>
          </div>
        )}
      </header>

      {/* Content Area */}
      <div className="content-area">
        {activeSubject ? (
          view === 'chat' ? (
            <ChatWindow subject={activeSubject} />
          ) : (
            <UploadManager subject={activeSubject} />
          )
        ) : (
          <div className="empty-state-main animate-fade-in">
            <div className="logo-glow" style={{ width: '80px', height: '80px', borderRadius: '24px', marginBottom: '2rem' }}>
              <Sparkles size={40} color="white" />
            </div>
            <h2 className="brand-name" style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>ExamGen AI</h2>
            <p className="empty-desc">
              Unlock the power of your documents. Select a subject or create a new one to begin your intelligent learning journey.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default App;
