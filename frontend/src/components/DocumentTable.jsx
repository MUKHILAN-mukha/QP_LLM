import React from 'react';
import { FileText, Calendar, Trash2 } from 'lucide-react';

const DocumentTable = ({ documents, onDelete }) => {
    if (!documents || documents.length === 0) {
        return (
            <div className="empty-table-state">
                <FileText size={40} style={{ margin: '0 auto 1rem', opacity: 0.2 }} />
                <p style={{ fontWeight: 500 }}>No documents indexed</p>
            </div>
        );
    }

    return (
        <div className="doc-table-container">
            <table className="doc-table">
                <thead className="doc-table-header">
                    <tr>
                        <th>Name</th>
                        <th>Category</th>
                        <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {documents.map((doc) => (
                        <tr key={doc.id} className="doc-table-row">
                            <td className="doc-table-cell">
                                <div className="doc-table-file-info">
                                    <FileText size={16} style={{ color: doc.document_type === 'notes' ? '#60a5fa' : '#c084fc' }} />
                                    <span className="doc-table-filename">{doc.filename}</span>
                                </div>
                            </td>
                            <td className="doc-table-cell">
                                <span className="doc-table-type">{doc.document_type.replace('_', ' ')}</span>
                            </td>
                            <td className="doc-table-cell doc-table-actions">
                                <button
                                    onClick={() => onDelete(doc.id)}
                                    className="doc-table-btn-delete"
                                    title="Delete resource"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default DocumentTable;
