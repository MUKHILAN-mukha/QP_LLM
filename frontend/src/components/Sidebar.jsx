import React, { useState } from 'react';
import { Plus, Book, GraduationCap, Github } from 'lucide-react';

const Sidebar = ({ subjects, activeSubject, onSelectSubject, onCreateSubject }) => {
    const [isCreating, setIsCreating] = useState(false);
    const [newSubjectName, setNewSubjectName] = useState('');

    const submitCreate = (e) => {
        e.preventDefault();
        if (newSubjectName.trim()) {
            onCreateSubject(newSubjectName);
            setNewSubjectName('');
            setIsCreating(false);
        }
    };

    return (
        <div className="sidebar-container">
            {/* Premium Logo Area */}
            <div className="sidebar-header">
                <div className="logo-container">
                    <div className="logo-glow">
                        <GraduationCap className="text-white" size={24} />
                    </div>
                    <h1 className="brand-name">ExamGen</h1>
                </div>
            </div>

            {/* Subjects List */}
            <div className="sidebar-nav custom-scrollbar">
                <h3 className="nav-section-label">Knowledge Base</h3>

                <button
                    onClick={() => setIsCreating(true)}
                    className="subject-btn"
                    style={{ border: '1px dashed var(--border-color)', marginBottom: '0.5rem' }}
                >
                    <Plus size={18} />
                    <span>New Subject</span>
                </button>

                {isCreating && (
                    <form onSubmit={submitCreate} className="animate-fade-in" style={{ padding: '0 0.5rem 1rem' }}>
                        <input
                            autoFocus
                            type="text"
                            value={newSubjectName}
                            onChange={(e) => setNewSubjectName(e.target.value)}
                            placeholder="Type name & press Enter..."
                            style={{
                                width: '100%',
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--accent-primary)',
                                borderRadius: '8px',
                                padding: '8px 12px',
                                color: 'white',
                                outline: 'none'
                            }}
                            onBlur={() => !newSubjectName && setIsCreating(false)}
                        />
                    </form>
                )}

                <div className="subject-list">
                    {subjects.map(subject => {
                        const isActive = activeSubject?.id === subject.id;
                        return (
                            <button
                                key={subject.id}
                                onClick={() => onSelectSubject(subject)}
                                className={`subject-btn ${isActive ? 'active' : ''}`}
                            >
                                <div className="subject-dot" />
                                <span className="subject-name">{subject.name}</span>
                            </button>
                        );
                    })}

                    {subjects.length === 0 && !isCreating && (
                        <div className="empty-state-sidebar">
                            <p className="empty-text">No subjects found</p>
                            <p className="empty-subtext">Add one to begin</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Footer */}
            <div className="sidebar-footer">
                <a href="#" className="github-link">
                    <Github size={16} />
                    <span>View on GitHub</span>
                </a>
            </div>
        </div>
    );
};

export default Sidebar;
