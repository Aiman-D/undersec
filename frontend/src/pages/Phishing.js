import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, MailWarning, Loader2, Link as LinkIcon } from 'lucide-react';
import { analyzePhishing } from '../api/client';

const Phishing = () => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
        if (!url) return;
        setLoading(true);
        setResult(null);
        try {
            const res = await analyzePhishing(url);
            setResult(res.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page fade-in">
            <div className="page-header">
                <h1 className="page-title">Phishing Detection</h1>
                <p className="page-subtitle">Analyze URLs and emails for phishing patterns using our Hybrid GenAI Model.</p>
            </div>

            <div className="card" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <LinkIcon size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#8892a4' }} />
                        <input 
                            type="text" 
                            placeholder="Enter suspicious URL (e.g., http://secure-login.apple.com.badsite.net)"
                            value={url}
                            onChange={e => setUrl(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px 16px 12px 42px',
                                background: 'rgba(255,255,255,0.03)',
                                border: '1px solid var(--border)',
                                borderRadius: '8px',
                                color: '#fff',
                                outline: 'none'
                            }}
                        />
                    </div>
                    <button 
                        onClick={handleAnalyze} 
                        disabled={loading || !url}
                        style={{
                            background: 'var(--accent-blue)',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '0 24px',
                            fontWeight: 600,
                            cursor: (loading || !url) ? 'not-allowed' : 'pointer',
                            opacity: (loading || !url) ? 0.7 : 1,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        {loading && <Loader2 size={16} className="spin" />}
                        Analyze
                    </button>
                </div>

                {result && (
                    <div style={{
                        background: 'rgba(0,0,0,0.2)',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        padding: '24px'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
                            <div>
                                <h3 style={{ margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    {result.status === 'BLOCKED' ? <ShieldAlert color="#ef4444" /> : result.status === 'FLAGGED' ? <MailWarning color="#f59e0b" /> : <ShieldCheck color="#22c55e" />}
                                    <span style={{ color: result.status === 'BLOCKED' ? '#ef4444' : result.status === 'FLAGGED' ? '#f59e0b' : '#22c55e' }}>
                                        {result.level}
                                    </span>
                                </h3>
                                <div style={{ color: '#8892a4', fontSize: '14px', wordBreak: 'break-all' }}>{result.url}</div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{result.score}%</div>
                                <div style={{ fontSize: '12px', color: '#8892a4' }}>Threat Score</div>
                            </div>
                        </div>

                        <div style={{ background: '#1a1f28', padding: '16px', borderRadius: '6px', marginBottom: '20px' }}>
                            <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#fff' }}>GenAI Explanation</h4>
                            <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', color: '#cbd5e1' }}>
                                {result.explanation}
                            </p>
                        </div>

                        {result.reasons && result.reasons.length > 0 && (
                            <div>
                                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#fff' }}>Detected Flags</h4>
                                <ul style={{ margin: 0, paddingLeft: '20px', color: '#cbd5e1', fontSize: '14px' }}>
                                    {result.reasons.map((r, i) => <li key={i} style={{ marginBottom: '6px' }}>{r}</li>)}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Phishing;
