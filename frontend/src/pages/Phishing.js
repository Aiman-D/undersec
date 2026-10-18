import React, { useState, useEffect } from 'react';
import { 
    ShieldAlert, 
    ShieldCheck, 
    MailWarning, 
    Loader2, 
    Link as LinkIcon, 
    Globe 
} from 'lucide-react';
import { analyzePhishing, getRecentPhishingScans } from '../api/client';

const SAMPLE_URLS = [
    { label: "Panasonic Automotive", url: "https://na.panasonic.com/us/automotive-solutions", isPhish: false },
    { label: "Lexus RX Configurator", url: "https://lexus.com/models/RX/configurator", isPhish: false },
    { label: "IP Host Phishing", url: "http://192.168.1.55/panasonic/kiosk_login.php", isPhish: true },
    { label: "Apple Typosquat", url: "http://secure-login-apple-update.com/verify?token=9284", isPhish: true },
    { label: "Deep Subdomain Phish", url: "http://security.verify.paypal.com.account-update.info/signin", isPhish: true }
];

const Phishing = () => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [recentScans, setRecentScans] = useState([]);

    const fetchRecent = async () => {
        try {
            const res = await getRecentPhishingScans();
            setRecentScans(res.data.scans || []);
        } catch (e) {}
    };

    useEffect(() => {
        fetchRecent();
    }, []);

    const handleAnalyze = async (targetUrl = url) => {
        const queryUrl = targetUrl || url;
        if (!queryUrl) return;
        setLoading(true);
        setResult(null);
        try {
            const res = await analyzePhishing(queryUrl);
            setResult(res.data);
            fetchRecent();
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const feats = result?.features;

    return (
        <div className="page fade-in">
            {/* Header */}
            <div className="page-header" style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <h1 className="page-title">XGBoost Phishing Detection & Extension</h1>
                    <span style={{ 
                        background: 'rgba(239, 68, 68, 0.15)', 
                        border: '1px solid rgba(239, 68, 68, 0.3)', 
                        color: 'var(--accent-red)', 
                        padding: '3px 10px', 
                        borderRadius: '12px', 
                        fontSize: '11px', 
                        fontWeight: 700 
                    }}>
                        Layer 4 · 7 URL Heuristics
                    </span>
                </div>
                <p className="page-subtitle">
                    Real-time XGBoost ML classifier evaluating 7 structural URL heuristic features integrated into our Chrome Extension & Ollama GenAI reasoning
                </p>
            </div>

            {/* URL Input Bar & Presets */}
            <div className="card" style={{ padding: 20, marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <LinkIcon size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input 
                            type="text" 
                            placeholder="Enter any target URL (e.g., http://192.168.1.55/login.php or https://panasonic.com)"
                            value={url}
                            onChange={e => setUrl(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleAnalyze()}
                            style={{
                                width: '100%',
                                padding: '12px 16px 12px 42px',
                                background: 'var(--bg-surface)',
                                border: '1px solid var(--border)',
                                borderRadius: '8px',
                                color: '#fff',
                                outline: 'none',
                                fontSize: '13px'
                            }}
                        />
                    </div>
                    <button 
                        onClick={() => handleAnalyze()} 
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
                        Scan URL
                    </button>
                </div>

                {/* Sample Presets */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>Test Scenarios:</span>
                    {SAMPLE_URLS.map(s => (
                        <button
                            key={s.label}
                            onClick={() => { setUrl(s.url); handleAnalyze(s.url); }}
                            className="sample-tag"
                            style={{
                                borderColor: s.isPhish ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)',
                                color: s.isPhish ? '#fca5a5' : '#86efac'
                            }}
                        >
                            {s.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Analysis Result Card */}
            {result && (
                <div className="card fade-in" style={{ padding: 24, marginBottom: 20 }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
                        <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                                {result.status === 'BLOCKED' ? <ShieldAlert color="var(--accent-red)" size={20} /> :
                                 result.status === 'FLAGGED' ? <MailWarning color="var(--accent-yellow)" size={20} /> :
                                 <ShieldCheck color="var(--accent-green)" size={20} />}
                                <h3 style={{ margin: 0, fontSize: 18, color: result.status === 'BLOCKED' ? 'var(--accent-red)' : result.status === 'FLAGGED' ? 'var(--accent-yellow)' : 'var(--accent-green)' }}>
                                    {result.level} · {result.status}
                                </h3>
                            </div>
                            <div style={{ color: 'var(--text-muted)', fontSize: 13, fontFamily: 'monospace' }}>
                                {result.url}
                            </div>
                        </div>

                        <div style={{ textAlign: 'right' }}>
                            <div style={{ 
                                fontSize: 26, 
                                fontWeight: 800, 
                                fontFamily: 'monospace',
                                color: result.status === 'BLOCKED' ? 'var(--accent-red)' : result.status === 'FLAGGED' ? 'var(--accent-yellow)' : 'var(--accent-green)'
                            }}>
                                {result.score}%
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>XGBoost Threat Probability</div>
                        </div>
                    </div>

                    {/* 7 URL Heuristic Features Grid */}
                    <div style={{ marginBottom: 18 }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>
                            7 Heuristic Features Evaluated by XGBoost
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
                            <div className="feature-item">
                                <div className="feature-label">1. URL Length</div>
                                <div className="feature-val">{feats?.len_url ?? '--'}</div>
                            </div>
                            <div className="feature-item">
                                <div className="feature-label">2. Host Length</div>
                                <div className="feature-val">{feats?.len_host ?? '--'}</div>
                            </div>
                            <div className="feature-item">
                                <div className="feature-label">3. Digits Count</div>
                                <div className="feature-val">{feats?.count_digits ?? '--'}</div>
                            </div>
                            <div className="feature-item">
                                <div className="feature-label">4. Subdomain Depth</div>
                                <div className="feature-val">{feats?.subdomains ?? '--'}</div>
                            </div>
                            <div className="feature-item">
                                <div className="feature-label">5. IP Host Indicator</div>
                                <div className="feature-val" style={{ color: feats?.has_ip ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                                    {feats?.has_ip ? 'YES (1.0)' : 'NO (0.0)'}
                                </div>
                            </div>
                            <div className="feature-item">
                                <div className="feature-label">6. Non-Alnum Ratio</div>
                                <div className="feature-val">{feats?.non_alnum ?? '--'}</div>
                            </div>
                            <div className="feature-item">
                                <div className="feature-label">7. Shannon Entropy</div>
                                <div className="feature-val">{feats?.path_entropy ?? '--'}</div>
                            </div>
                        </div>
                    </div>

                    {/* GenAI Explanation */}
                    <div style={{ background: 'var(--bg-surface)', padding: 16, borderRadius: 8, borderLeft: '3px solid var(--accent-blue)', marginBottom: 16 }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: '#93c5fd', marginBottom: 4 }}>
                            Ollama LLM Security Analysis
                        </div>
                        <p style={{ margin: 0, fontSize: 13, color: '#cbd5e1', lineHeight: 1.5 }}>
                            {result.explanation}
                        </p>
                    </div>

                    {/* Detected Reasons */}
                    {result.reasons && (
                        <div>
                            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                                Model Explanations & Indicators
                            </div>
                            <ul style={{ margin: 0, paddingLeft: 18, color: '#cbd5e1', fontSize: 12 }}>
                                {result.reasons.map((r, i) => (
                                    <li key={i} style={{ marginBottom: 4 }}>{r}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* Chrome Extension Companion Info & Recent Scans */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                {/* Extension Overview */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <Globe size={16} color="var(--accent-blue)" />
                            UnderSec Chrome Extension (Manifest v3)
                        </div>
                    </div>
                    <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 14 }}>
                        The Chrome extension is located in <code style={{ color: 'var(--accent-blue)' }}>/extension</code>. It monitors active tabs in real time using background service workers and queries this FastAPI ML pipeline.
                    </p>
                    <div style={{ background: 'var(--bg-surface)', padding: 12, borderRadius: 6, fontSize: 12, color: '#cbd5e1' }}>
                        <b>To install in Google Chrome:</b>
                        <ol style={{ paddingLeft: 18, marginTop: 6 }}>
                            <li>Navigate to <code style={{ color: 'var(--accent-yellow)' }}>chrome://extensions</code></li>
                            <li>Enable <b>Developer mode</b> (top right toggle)</li>
                            <li>Click <b>Load unpacked</b> and select the <code style={{ color: 'var(--accent-blue)' }}>extension/</code> folder</li>
                        </ol>
                    </div>
                </div>

                {/* Recent Telemetry Scans */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">Recent Phishing Telemetry Feed</div>
                        <span className="card-tag">Live Log</span>
                    </div>

                    <div style={{ maxHeight: 180, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {recentScans.length === 0 ? (
                            <div className="empty-state" style={{ padding: 20 }}>
                                <div className="empty-state-sub">No recent scans logged</div>
                            </div>
                        ) : (
                            recentScans.map(s => (
                                <div 
                                    key={s.id}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        padding: '6px 8px',
                                        background: 'var(--bg-surface)',
                                        borderRadius: 4,
                                        fontSize: 11
                                    }}
                                >
                                    <span style={{ fontFamily: 'monospace', maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {s.url}
                                    </span>
                                    <span className={`badge badge-${s.status.toLowerCase()}`}>
                                        {s.score}%
                                    </span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Phishing;
