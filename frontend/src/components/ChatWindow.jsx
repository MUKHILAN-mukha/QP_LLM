import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, Sparkles, FileDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { chat, getChatHistory, generateExamPDF } from '../services/api';

const ChatWindow = ({ subject }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [isPolling, setIsPolling] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);
    const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);
    const pollingTimeoutRef = useRef(null);

    const handleDownloadPDF = async () => {
        try {
            setIsGeneratingPDF(true);
            const blob = await generateExamPDF(subject.id);

            // Create download link
            const url = window.URL.createObjectURL(new Blob([blob]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Exam_${subject.name}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Failed to download PDF:", error);
            // Optional: Show toast error
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "❌ **PDF Generation Failed.** Please try again later."
            }]);
        } finally {
            setIsGeneratingPDF(false);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        if (subject) {
            fetchHistory();
            if (inputRef.current) inputRef.current.focus();
        }
        return () => {
            if (pollingTimeoutRef.current) clearTimeout(pollingTimeoutRef.current);
        };
    }, [subject.id]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading, isPolling]);

    const fetchHistory = async () => {
        setLoadingHistory(true);
        try {
            const history = await getChatHistory(subject.id);
            const formatted = history.map(msg => ({
                role: msg.role,
                content: msg.content
            }));

            if (formatted.length === 0) {
                setMessages([{
                    role: 'assistant',
                    content: `Hello! I'm ready to help you generate exam questions for **${subject.name}**. What topic should we cover?`
                }]);
            } else {
                setMessages(formatted);
            }
        } catch (error) {
            console.error("Failed to load history", error);
        } finally {
            setLoadingHistory(false);
        }
    };

    // Robust Polling: Keeps checking history if the server is slow
    const pollForResponse = async (lastMessageCount, retryCount = 0) => {
        if (retryCount > 15) { // Stop after 30 seconds
            setIsPolling(false);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "❌ **Sync failed.** The AI is taking longer than usual. Please refresh the page manually in a moment."
            }]);
            return;
        }

        try {
            const history = await getChatHistory(subject.id);
            const formattedHistory = history.map(msg => ({ role: msg.role, content: msg.content }));

            if (formattedHistory.length > lastMessageCount && formattedHistory[formattedHistory.length - 1].role === 'assistant') {
                // Success! New message found
                setMessages(formattedHistory);
                setIsPolling(false);
            } else {
                // Not ready yet, poll again in 2s
                pollingTimeoutRef.current = setTimeout(() => {
                    pollForResponse(lastMessageCount, retryCount + 1);
                }, 2000);
            }
        } catch (error) {
            console.error("Polling error:", error);
            setIsPolling(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading || isPolling) return;

        const userMessage = input;
        const currentMessageCount = messages.length;

        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setLoading(true);

        try {
            const response = await chat(subject.id, userMessage);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.answer,
                context: response.context_used
            }]);
        } catch (error) {
            console.error("Chat error:", error);
            // Don't show "error" immediately, start polling instead
            setLoading(false);
            setIsPolling(true);
            pollForResponse(currentMessageCount + 1); // +1 for the user message we just added
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-window">
            {/* Messages Area */}
            <div className="chat-messages-container custom-scrollbar">
                {loadingHistory ? (
                    <div className="loading-container animate-fade-in">
                        <Loader2 className="animate-spin mb-4" size={40} style={{ color: 'var(--accent-primary)' }} />
                        <p className="loading-text" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>PREPARING KNOWLEDGE...</p>
                    </div>
                ) : messages.length === 0 ? (
                    <div className="empty-chat-state">
                        <div className="empty-icon-wrapper">
                            <Bot size={64} style={{ opacity: 0.5 }} />
                        </div>
                        <h3>Ask me anything about {subject.name}</h3>
                        <p>I can help you study, summarize notes, or generate exam papers.</p>

                        <div className="quick-actions">
                            <button
                                onClick={handleDownloadPDF}
                                className="quick-action-btn"
                                disabled={isGeneratingPDF}
                            >
                                {isGeneratingPDF ? <Loader2 className="animate-spin" size={20} /> : <FileDown size={20} />}
                                <span>Generate Exam PDF</span>
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`message-wrapper animate-slide-up ${msg.role === 'user' ? 'user' : 'bot'}`}>
                                <div className={`message-bubble ${msg.role === 'user' ? 'user' : 'bot'}`}>
                                    <div className="markdown-content">
                                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                                    </div>

                                    {msg.context && msg.context.length > 0 && (
                                        <details className="context-details">
                                            <summary className="context-summary">
                                                <Sparkles size={14} style={{ color: 'var(--accent-primary)' }} />
                                                <span>Metadata Sources</span>
                                            </summary>
                                            <div className="context-content">
                                                {msg.context.slice(0, 3).map((ctx, i) => (
                                                    <div key={i} className="context-item">
                                                        {typeof ctx === 'string' ? `"${ctx.substring(0, 150)}..."` : `Source: ${ctx.metadata?.filename || 'Unknown'}`}
                                                    </div>
                                                ))}
                                            </div>
                                        </details>
                                    )}
                                </div>
                            </div>
                        ))}

                        {(loading || isPolling) && (
                            <div className="message-wrapper bot animate-slide-up">
                                <div className="message-bubble bot typing-bubble">
                                    <div className="typing-indicator" style={{ marginRight: '1rem' }}>
                                        <span className="dot"></span>
                                        <span className="dot delay-1"></span>
                                        <span className="dot delay-2"></span>
                                    </div>
                                    <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                                        {isPolling ? "SYNCING REAL-TIME..." : "EXTRACTING DATA..."}
                                    </span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} style={{ height: '2rem' }} />
                    </>
                )}
            </div>

            {/* Premium Input Area */}
            <div className="chat-input-wrapper">
                <div className="input-container-premium">
                    <form onSubmit={handleSubmit} style={{ display: 'flex', width: '100%', alignItems: 'center' }}>
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={isPolling ? "Waiting for sync..." : "Type your query here..."}
                            className="premium-input"
                            disabled={loading || isPolling}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || loading || isPolling}
                            className="send-btn-premium"
                        >
                            {(loading || isPolling) ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
                        </button>
                    </form>
                </div>
                <div className="disclaimer-text">
                    <p style={{ opacity: 0.5, fontStyle: 'italic' }}>Powered by ExamGen AI • Accuracy depends on source data</p>
                </div>
            </div>
        </div>
    );
};

export default ChatWindow;
