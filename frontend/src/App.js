import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';

// Temporary placeholder components until we build the real pages
const Dashboard = () => <div style={{ padding: '30px', color: '#fff' }}><h2>Dashboard</h2><p>Stats and charts will go here.</p></div>;
const Alerts = () => <div style={{ padding: '30px', color: '#fff' }}><h2>Alerts</h2><p>Flagged queries will go here.</p></div>;
const Activity = () => <div style={{ padding: '30px', color: '#fff' }}><h2>Activity Log</h2><p>All database traffic will go here.</p></div>;
const ModelControl = () => <div style={{ padding: '30px', color: '#fff' }}><h2>Model Control</h2><p>Retrain controls will go here.</p></div>;

function App() {
  return (
    <Router>
      <div style={{ display: 'flex', backgroundColor: '#13131a', minHeight: '100vh', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <Sidebar />
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/activity" element={<Activity />} />
            <Route path="/model" element={<ModelControl />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;