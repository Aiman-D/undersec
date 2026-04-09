import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import ActivityLog from './pages/ActivityLog';
import ModelControl from './pages/ModelControl';
import './index.css';

function App() {
    return (
        <Router>
            <div className="app-shell">
                <Sidebar />
                <main className="main-content">
                    <Routes>
                        <Route path="/"         element={<Dashboard />}   />
                        <Route path="/alerts"   element={<Alerts />}      />
                        <Route path="/activity" element={<ActivityLog />} />
                        <Route path="/model"    element={<ModelControl />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;