import React, { useState } from 'react';
import { Play, ShieldCheck, AlertTriangle, AlertOctagon, Zap, Code, ChevronRight } from 'lucide-react';
import { sendTestQuery } from '../api/client';

const SAMPLE_QUERIES = [
    { label: 'Safe SELECT',  query: 'SELECT id, name FROM users WHERE id = 42;' },
    { label: 'UNION Attack', query: "SELECT * FROM users WHERE id = 1 UNION SELECT username, password, NULL, NULL FROM admin;" },
    { label: 'OR Bypass',    query: "SELECT * FROM accounts WHERE username = 'admin' OR 1=1 --;" },
    { label: 'DROP Table',   query: 'DROP TABLE users;' },
    { label: 'Subquery',     query: 'SELECT name FROM products WHERE id IN (SELECT product_id FROM orders WHERE user_id = 5);' },
];

const STATUS_CONFIG = {
    ALLOWED: {
        color:   'var(--accent-green)',
        bg:      'var(--accent-green-glow)',
        border:  'rgba(34,197,94,0.2)',
        icon:    ShieldCheck,
        label:   'Query Allowed',
        sub:     'Safe — transaction passed all security rules',
    },
    FLAGGED: {
        color:   'var(--accent-yellow)',
        bg:      'var(--accent-yellow-glow)',
        border:  'rgba(245,158,11,0.2)',
        icon:    AlertTriangle,
        label:   'Query Flagged',
        sub:     'Medium risk — anomalous pattern detected',
    },
    BLOCKED: {
        color:   'var(--accent-red)',
        bg:      'var(--accent-red-glow)',
        border:  'rgba(239,68,68,0.2)',
        icon:    AlertOctagon,
        label:   'Query Blocked',
        sub:     'High risk — attack signature matched',
    },
    ERROR: {
        color:   'var(--text-muted)',
        bg:      'var(--bg-elevated)',
        border:  'var(--border)',
        icon:    AlertOctagon,
        label:   'Connection Error',
        sub:     'Could not reach the backend',
    },
};

const ScoreMeter = ({ score }) => {
    // score is negative (anomaly): closer to 0 = more normal, more negative = more anomalous
    // clamp to [−1, 0] and display
    const pct = Math.min(100, Math.max(0, (-score) * 100));
    const color = pct < 10 ? '#22c55e' : pct < 30 ? '#f59e0b' : '#ef4444';
    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>Anomaly Score</span>
                <span style={{ fontSize: 13, fontFamily: 'var(--font-mono)', fontWeight: 600, color }}>{score.toFixed(4)}</span>
            </div>
            <div style={{ height: 5, borderRadius: 3, background: 'var(--bg-elevated)', overflow: 'hidden' }}>
                <div style={{
                    height: '100%', borderRadius: 3,
                    width: `${pct}%`,
                    background: color,
                    transition: 'width 0.6s ease, background 0.3s',
                    boxShadow: `0 0 8px ${color}66`,
                }} />
            </div>
        </div>
    );
};

const ModelControl = () => {
    const [query,   setQuery]   = useState('');
    const [result,  setResult]  = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        setLoading(true);
        setResult(null);
        try {
            const res = await sendTestQuery(query, 'admin_user');
            setResult(res.data);
        } catch {
            setResult({ status: 'ERROR', score: 0, risk_level: 'N/A', execution_time_ms: 0 });
        } finally {
            setLoading(false);
        }
    };

    const cfg = result ? (STATUS_CONFIG[result.status] || STATUS_CONFIG.ERROR) : null;

    return (
        <div className="page fade-in">
            <div className="page-header">
                <h1 className="page-title">Query Tester</h1>
                <p className="page-subtitle">Submit SQL queries through the live security gateway and inspect results in real time</p>
            </div>

            <div className="query-tester">
                {/* Left: Input */}
                <div className="query-panel">
                    <div className="card" style={{ padding: '20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
                            <Code size={14} color="var(--text-muted)" />
                            <span style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-muted)' }}>SQL Input</span>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <textarea
                                id="query-input"
                                className="query-textarea"
                                value={query}
                                onChange={e => setQuery(e.target.value)}
                                placeholder="SELECT * FROM users WHERE id = 1;"
                                spellCheck={false}
                            />
                            <button
                                id="run-query-btn"
                                type="submit"
                                className="run-btn"
                                disabled={loading || !query.trim()}
                                style={{ marginTop: 14, width: '100%' }}
                            >
                                {loading ? (
                                    <>
                                        <div className="loading-pulse" style={{ padding: 0, gap: 4 }}>
                                            <span style={{ background: '#fff' }} />
                                            <span style={{ background: '#fff' }} />
                                            <span style={{ background: '#fff' }} />
                                        </div>
                                        Analyzing…
                                    </>
                                ) : (
                                    <>
                                        <Play size={15} />
                                        Run Through Gateway
                                        <ChevronRight size={15} style={{ marginLeft: 2 }} />
                                    </>
                                )}
                            </button>
                        </form>
                    </div>

                    {/* Sample Queries */}
                    <div className="card" style={{ padding: '16px 20px' }}>
                        <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-muted)', marginBottom: 10 }}>
                            Sample Queries
                        </div>
                        <div className="sample-queries">
                            {SAMPLE_QUERIES.map(s => (
                                <button
                                    key={s.label}
                                    className="sample-tag"
                                    onClick={() => setQuery(s.query)}
                                >
                                    {s.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right: Result */}
                <div className="result-panel">
                    {!result && !loading && (
                        <div className="card">
                            <div className="empty-state" style={{ padding: '50px 20px' }}>
                                <div className="empty-state-icon">
                                    <Zap size={20} color="var(--text-muted)" />
                                </div>
                                <div className="empty-state-title">Awaiting query</div>
                                <div className="empty-state-sub">Results will appear here after analysis</div>
                            </div>
                        </div>
                    )}

                    {loading && (
                        <div className="card">
                            <div className="empty-state" style={{ padding: '50px 20px' }}>
                                <div className="loading-pulse"><span /><span /><span /></div>
                                <div className="empty-state-sub" style={{ marginTop: 8 }}>Running ML analysis…</div>
                            </div>
                        </div>
                    )}

                    {result && cfg && (
                        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                            {/* Status Header */}
                            <div
                                className="result-status-header"
                                style={{ background: cfg.bg, borderColor: cfg.border }}
                            >
                                <div className="result-status-icon" style={{ background: `${cfg.color}22` }}>
                                    <cfg.icon size={22} color={cfg.color} />
                                </div>
                                <div>
                                    <div className="result-status-label">Gateway Decision</div>
                                    <div className="result-status-value" style={{ color: cfg.color }}>{cfg.label}</div>
                                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{cfg.sub}</div>
                                </div>
                            </div>

                            {/* Score Meter */}
                            {result.score !== undefined && (
                                <div className="card" style={{ padding: '18px 20px' }}>
                                    <ScoreMeter score={result.score} />
                                </div>
                            )}

                            {/* Metrics Grid */}
                            <div className="result-metrics">
                                <div className="result-metric">
                                    <div className="result-metric-label">Risk Level</div>
                                    <div className="result-metric-value" style={{ fontSize: 16, fontFamily: 'inherit' }}>
                                        {result.risk_level || '—'}
                                    </div>
                                </div>
                                <div className="result-metric">
                                    <div className="result-metric-label">Latency</div>
                                    <div className="result-metric-value">
                                        {result.execution_time_ms != null ? `${result.execution_time_ms} ms` : '—'}
                                    </div>
                                </div>
                                <div className="result-metric">
                                    <div className="result-metric-label">Gateway Action</div>
                                    <div className="result-metric-value" style={{ fontSize: 15, fontFamily: 'inherit' }}>
                                        {result.status}
                                    </div>
                                </div>
                                <div className="result-metric">
                                    <div className="result-metric-label">Detection Type</div>
                                    <div className="result-metric-value" style={{ fontSize: 13, fontFamily: 'inherit', color: 'var(--text-secondary)' }}>
                                        {result.hardcoded_catch ? 'Rule-based' : 'ML Model'}
                                    </div>
                                </div>
                            </div>

                            {/* Hardcoded flag notice */}
                            {result.hardcoded_catch && (
                                <div className="hardcoded-flag">
                                    <AlertTriangle size={14} />
                                    Policy override — caught by deterministic rule before ML evaluation
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ModelControl;