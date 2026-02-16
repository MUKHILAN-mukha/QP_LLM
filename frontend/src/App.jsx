import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import UploadManager from './components/UploadManager';
import Layout from './components/Layout';
import { getSubjects, createSubject, generateExamPDF } from './services/api';
import { BookOpen, Upload, MessageSquare, Menu, Sparkles, FileDown, Loader2 } from 'lucide-react';
import './index.css';

function App() {
  const [subjects, setSubjects] = useState([]);
  const [activeSubject, setActiveSubject] = useState(null);
  const [view, setView] = useState('chat'); // 'chat' or 'upload'
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

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

  const handleDownloadPDF = async () => {
    if (!activeSubject) return;
    try {
      setIsGeneratingPDF(true);

      // 1. Scan Chat History for the latest "Exam-like" response
      // We look for the last message from 'assistant'
      let formattedQuestions = null;

      try {
        // Fetch latest history to be sure
        const history = await import('./services/api').then(m => m.getChatHistory(activeSubject.id));
        const lastBotMsg = [...history].reverse().find(m => m.role === 'assistant');

        if (lastBotMsg && lastBotMsg.content) {
          // Simple heuristic parsing (can be improved with regex)
          // We try to find numbered lists and split them into Part A (2 marks) and Part B (16 marks)
          const text = lastBotMsg.content;

          // Regex to find questions like "1. What is..." or "1. Explain..."
          // This is a basic parser; for robust results, the LLM should output JSON, 
          // but since we are parsing natural language chat, we do a best-effort extraction.

          const part_a = [];
          const part_b = [];

          const lines = text.split('\n');
          let currentSection = 'part_a'; // Default to A
          lines.forEach(line => {
            const trimmedLine = line.trim();

            // Section Detection
            if (trimmedLine.match(/part\s*b|16\s*marks|fourteen|sixteen/i)) {
              currentSection = 'part_b';
              return; // specific skip
            } else if (trimmedLine.match(/part\s*a|2\s*marks|two/i)) {
              currentSection = 'part_a';
              return;
            }

            // Question Extraction
            // Matches: "1. Question...", "1. Unit 1 - Question...", "1) Question..."
            // Also looks for trailing metadata like (Un CO1) or (Re CO2)
            const match = trimmedLine.match(/^\d+[\.\)]\s*(.+)/);
            if (match && trimmedLine.length > 10) {
              let qText = match[1];

              // Extract CL and CO if present
              // Pattern: (Un CO1), (Re CO2), (Ap CO4), etc.
              const metaMatch = qText.match(/\((Re|Un|Ap|An|Ev|Cr)\s*(CO\d+)\)/i);

              let cl = currentSection === 'part_a' ? "Re" : "Ap"; // Default
              let co = "CO1"; // Default co

              if (metaMatch) {
                cl = metaMatch[1];
                co = metaMatch[2].toUpperCase();
              } else {
                // Fallback 1: Check for just (CO1)
                const coMatch = qText.match(/(CO\d+)/i);
                if (coMatch) co = coMatch[1].toUpperCase();

                // Fallback 2: Check for (Unit X) -> Map to CO X
                const unitMatch = qText.match(/Unit\s*(\d+)/i);
                if (unitMatch) {
                  co = `CO${unitMatch[1]}`;
                }

                const clMatch = qText.match(/\b(Re|Un|Ap|An|Ev|Cr)\b/i);
                if (clMatch) cl = clMatch[1];
              }

              // Capitalize CL first letter (Re, Un, Ap)
              cl = cl.charAt(0).toUpperCase() + cl.slice(1).toLowerCase();

              const qObj = {
                question: qText, // Backend will strip the metadata tags
                marks: currentSection === 'part_a' ? 2 : 16,
                cl: cl,
                co: co
              };

              if (currentSection === 'part_a') part_a.push(qObj);
              else part_b.push(qObj);
            }
          });

          if (part_a.length > 0 || part_b.length > 0) {
            formattedQuestions = { part_a, part_b };
            console.log("Extracted Questions for PDF:", formattedQuestions);
          }
        }
      } catch (e) {
        console.warn("Failed to parse chat history for PDF, falling back to auto-gen", e);
      }

      const blob = await generateExamPDF(activeSubject.id, formattedQuestions);

      // Create download link
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Exam_${activeSubject.name}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download PDF:", error);
      alert("Failed to generate PDF. Please try again.");
    } finally {
      setIsGeneratingPDF(false);
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
          <div className="header-right-actions" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            {view === 'chat' && (
              <button
                onClick={handleDownloadPDF}
                className="pdf-btn"
                disabled={isGeneratingPDF}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  background: 'linear-gradient(135deg, #FF6B6B 0%, #EE5253 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  fontWeight: 600,
                  cursor: isGeneratingPDF ? 'wait' : 'pointer',
                  fontSize: '0.875rem',
                  boxShadow: '0 4px 12px rgba(238, 82, 83, 0.3)'
                }}
              >
                {isGeneratingPDF ? <Loader2 size={16} className="animate-spin" /> : <FileDown size={16} />}
                <span>{isGeneratingPDF ? "Generating..." : "Download PDF"}</span>
              </button>
            )}

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
