import React, { useState } from 'react';
import { sendTestQuery } from '../api/client';
import { Play, ShieldCheck, AlertOctagon, AlertTriangle } from 'lucide-react';

const ModelControl = () => {
    const [query, setQuery] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleTestQuery = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            // Send the query to our FastAPI backend
            const response = await sendTestQuery(query, 'admin_user');
            setResult(response.data);
        } catch (error) {
            console.error("Error testing query:", error);
            setResult({ status: 'ERROR', error: 'Failed to connect to backend' });
        }
        setLoading(false);
    };

    const getStatusUI = (status) => {
        if (status === 'ALLOWED') return { color: '#4ade80', icon: <ShieldCheck size={24} />, text: 'Query Allowed (Safe)' };
        if (status === 'FLAGGED') return { color: '#fbbf24', icon: <AlertTriangle size={24} />, text: 'Query Flagged (Medium Risk)' };
        if (status === 'BLOCKED') return { color: '#f87171', icon: <AlertOctagon size={24} />, text: 'Query Blocked (High Risk)' };
        return { color: '#8b8b9e', icon: null, text: 'Unknown Status' };
    };

    return (
        <div style={{ padding: '30px', color: '#fff', maxWidth: '800px' }}>
            <h1 style={{ margin: '0 0 10px 0', fontSize: '24px' }}>Live Gateway Simulator</h1>
            <p style={{ color: '#8b8b9e', marginBottom: '30px' }}>
                Test how the Undersec ML model grades and intercepts incoming database queries.
            </p>

            <div style={{ backgroundColor: '#1e1e2f', padding: '25px', borderRadius: '12px', marginBottom: '30px' }}>
                <form onSubmit={handleTestQuery}>
                    <label style={{ display: 'block', marginBottom: '10px', color: '#e2e8f0', fontWeight: '500' }}>
                        Enter SQL Query
                    </label>
                    <textarea 
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="SELECT * FROM users WHERE id = 1;"
                        style={{ 
                            width: '100%', height: '120px', padding: '15px', borderRadius: '8px', 
                            backgroundColor: '#13131a', border: '1px solid #2d2d44', color: '#fff', 
                            fontFamily: 'monospace', fontSize: '14px', marginBottom: '20px', resize: 'vertical'
                        }}
                    />
                    <button 
                        type="submit" 
                        disabled={loading}
                        style={{
                            backgroundColor: '#4f46e5', color: '#fff', border: 'none', padding: '12px 24px',
                            borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer',
                            display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold', fontSize: '14px',
                            opacity: loading ? 0.7 : 1
                        }}
                    >
                        <Play size={18} /> {loading ? 'Analyzing...' : 'Run Query Through Gateway'}
                    </button>
                </form>
            </div>

            {/* Results Display */}
            {result && (
                <div style={{ 
                    backgroundColor: '#1e1e2f', padding: '25px', borderRadius: '12px',
                    borderLeft: `4px solid ${getStatusUI(result.status).color}`
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
                        <div style={{ color: getStatusUI(result.status).color }}>
                            {getStatusUI(result.status).icon}
                        </div>
                        <h2 style={{ margin: 0, color: getStatusUI(result.status).color }}>
                            {getStatusUI(result.status).text}
                        </h2>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div>
                            <p style={{ color: '#8b8b9e', margin: '0 0 5px 0', fontSize: '12px', textTransform: 'uppercase' }}>Anomaly Score</p>
                            <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace' }}>
                                {result.score !== undefined ? result.score.toFixed(4) : 'N/A'}
                            </p>
                        </div>
                        <div>
                            <p style={{ color: '#8b8b9e', margin: '0 0 5px 0', fontSize: '12px', textTransform: 'uppercase' }}>Risk Level</p>
                            <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>{result.risk_level}</p>
                        </div>
                        <div>
                            <p style={{ color: '#8b8b9e', margin: '0 0 5px 0', fontSize: '12px', textTransform: 'uppercase' }}>Execution Time</p>
                            <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>{result.execution_time_ms} ms</p>
                        </div>
                        <div>
                            <p style={{ color: '#8b8b9e', margin: '0 0 5px 0', fontSize: '12px', textTransform: 'uppercase' }}>Gateway Action</p>
                            <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>{result.status}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ModelControl;