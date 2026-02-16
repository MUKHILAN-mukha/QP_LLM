import React from 'react';

const Layout = ({ sidebar, children }) => {
    return (
        <div className="app-container">
            {/* Sidebar Area */}
            <div className="sidebar">
                {sidebar}
            </div>

            {/* Main Content Area */}
            <div className="main-content">
                {children}
            </div>
        </div>
    );
};

export default Layout;
