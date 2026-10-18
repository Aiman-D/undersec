import React, { useState, useEffect, useCallback } from 'react';
import { 
    AlertTriangle, 
    AlertOctagon, 
    RefreshCw, 
    ChevronDown, 
    ChevronUp, 
    Sparkles, 
    ShieldCheck 
} from 'lucide-react';
import { getAlerts, getActivity, getIncidentSummary, summarizeCustomIncidents } from '../api/client';

const RISK_CONFIG = {
    'HIGH RISK': { color: 'var(--accent-red)', bg: 'var(--accent-red-glow)', icon: AlertOctagon, badgeClass: 'badge-blocked' },
    'CRITICAL':  { color: 'var(--accent-red)', bg: 'var(--accent-red-glow)', icon: AlertOctagon, badgeClass: 'badge-blocked' },
    'MEDIUM RISK': { color: 'var(--accent-yellow)', bg: 'var(--accent-yellow-glow)', icon: AlertTriangle, badgeClass: 'badge-flagged' },
    'WARNING':   { color: 'var(--accent-yellow)', bg: 'var(--accent-yellow-glow)', icon: AlertTriangle, badgeClass: 'badge-flagged' },
    'ALERT':     { color: 'var(--accent-red)', bg: 'var(--accent-red-glow)', icon: AlertOctagon, badgeClass: 'badge-blocked' },
};

const formatTimestamp = (ts) => {
    if (!ts) return '—';
    const d = new Date(ts);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
         + ' · '
         + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
};

const AlertCard = ({ alert, query }) => {
    const [expanded, setExpanded] = useState(false);
    const cfg = RISK_CONFIG[alert.risk_level] || RISK_CONFIG['MEDIUM RISK'];
    const Icon = cfg.icon;

    return (
        <div className="alert-card fade-in" style={{ borderLeft: `3px solid ${cfg.color}` }}>
            <div className="alert-card-header">
                <div className="alert-risk-icon" style={{ background: cfg.bg }}>
                    <Icon size={18} color={cfg.color} />
                </div>
                <div className="alert-card-meta">
                    <div className="alert-card-title">{alert.risk_level}</div>
                    <div className="alert-card-time">
                        Alert #{alert.id} · {formatTimestamp(alert.created_at)}
                        {query && <span style={{ marginLeft: 6, color: 'var(--text-muted)' }}>· {query.db_user}</span>}
                    </div>
                </div>
                <span className={`badge ${cfg.badgeClass}`} style={{ marginLeft: 'auto' }}>
                    <span className="badge-dot" />
                    {alert.risk_level?.includes('HIGH') || alert.risk_level === 'CRITICAL' ? 'BLOCKED' : 'FLAGGED'}
                </span>
            </div>

            {query && (
                <div className="alert-card-query">{query.query_text}</div>
            )}

            {alert.explanation && (
                <>
                    <div
                        className="alert-card-explanation"
                        style={{
                            maxHeight: expanded ? 'none' : '56px',
                            overflow: expanded ? 'visible' : 'hidden',
                            position: 'relative',
                        }}
                    >
                        {alert.explanation}
                        {!expanded && (
                            <div style={{
                                position: 'absolute', bottom: 0, left: 0, right: 0,
                                height: 28, background: 'linear-gradient(transparent, var(--bg-card))'
                            }} />
                        )}
                    </div>
                    <button
                        onClick={() => setExpanded(e => !e)}
                        style={{
                            display: 'flex', alignItems: 'center', gap: 4,
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: 'var(--text-muted)', fontSize: 12, fontWeight: 500,
                            fontFamily: 'inherit', padding: '2px 0',
                        }}
                    >
                        {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                        {expanded ? 'Show less' : 'Show GenAI explanation'}
                    </button>
                </>
            )}
        </div>
    );
};

const Alerts = () => {
    const [alerts, setAlerts] = useState([]);
    const [queries, setQueries] = useState({});
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [summarizing, setSummarizing] = useState(false);
    const [filter, setFilter] = useState('ALL');

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const [alertsRes, activityRes, sumRes] = await Promise.all([
                getAlerts(100),
                getActivity(100),
                getIncidentSummary().catch(() => ({ data: { summary: null } }))
            ]);

            setAlerts(alertsRes.data);
            setSummary(sumRes.data?.summary);

            const map = {};
            activityRes.data.forEach(q => { map[q.id] = q; });
            setQueries(map);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSummarize = async () => {
        setSummarizing(true);
        try {
            const res = await summarizeCustomIncidents();
            setSummary(res.data?.summary);
        } catch (e) {
            console.error(e);
        } finally {
            setSummarizing(false);
        }
    };

    const filtered = filter === 'ALL'
        ? alerts
        : alerts.filter(a => a.risk_level === filter);

    const highCount   = alerts.filter(a => a.risk_level === 'HIGH RISK').length;
    const mediumCount = alerts.filter(a => a.risk_level === 'MEDIUM RISK').length;

    return (
        <div className="page fade-in">
            {/* Header */}
            <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
                <div>
                    <h1 className="page-title">Incidents & Security Alerts</h1>
                    <p className="page-subtitle">
                        Multi-layer security alert feed with automated Ollama LLM correlation & root-cause explanations
                    </p>
                </div>
                <button
                    onClick={fetchData}
                    style={{
                        display: 'flex', alignItems: 'center', gap: 6,
                        background: 'var(--bg-card)', border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)',
                        fontSize: 12, fontWeight: 500, padding: '8px 14px',
                        cursor: 'pointer', fontFamily: 'inherit', outline: 'none',
                    }}
                >
                    <RefreshCw size={13} />
                    Refresh Feed
                </button>
            </div>

            {/* GenAI Incident Briefing Card */}
            <div className="incident-briefing-card fade-in">
                <div className="briefing-header">
                    <div className="briefing-title">
                        <Sparkles size={17} color="#c4b5fd" />
                        Executive Incident Intelligence (Ollama LLM)
                        <span style={{ 
                            fontSize: 10, padding: '2px 8px', borderRadius: 12,
                            background: summary?.threat_level === 'CRITICAL' || summary?.threat_level === 'HIGH' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                            color: summary?.threat_level === 'CRITICAL' || summary?.threat_level === 'HIGH' ? 'var(--accent-red)' : 'var(--accent-green)',
                            fontWeight: 700
                        }}>
                            {summary?.threat_level || 'NORMAL'}
                        </span>
                    </div>
                    <button
                        onClick={handleSummarize}
                        disabled={summarizing}
                        style={{
                            display: 'flex', alignItems: 'center', gap: 6,
                            background: 'rgba(139, 92, 246, 0.25)', border: '1px solid rgba(139, 92, 246, 0.4)',
                            borderRadius: 'var(--radius-sm)', color: '#ede9fe',
                            fontSize: 11, fontWeight: 600, padding: '5px 10px',
                            cursor: summarizing ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <Sparkles size={12} className={summarizing ? 'spin' : ''} />
                        {summarizing ? 'Analyzing...' : 'Re-Generate Briefing'}
                    </button>
                </div>

                <div className="briefing-text">
                    {summary?.executive_summary || "Ollama security engine correlating cross-layer threat indicators across Database DPI, Panasonic Showroom Hardware, CCTV Perimeter, and Phishing."}
                </div>

                {summary?.action_items && (
                    <div className="briefing-actions">
                        {summary.action_items.map((act, i) => (
                            <div key={i} className="briefing-action-chip">
                                • {act}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Filter Bar */}
            <div className="toolbar" style={{ marginBottom: 20 }}>
                {[
                    { key: 'ALL',         label: `All Alerts (${alerts.length})` },
                    { key: 'HIGH RISK',   label: `High Risk (${highCount})` },
                    { key: 'MEDIUM RISK', label: `Medium Risk (${mediumCount})` },
                ].map(f => (
                    <button
                        key={f.key}
                        className={`filter-btn ${filter === f.key ? 'active' : ''}`}
                        onClick={() => setFilter(f.key)}
                    >
                        {f.label}
                    </button>
                ))}
            </div>

            {/* Alert List */}
            {loading ? (
                <div className="loading-pulse" style={{ padding: 60 }}><span /><span /><span /></div>
            ) : filtered.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon"><ShieldCheck size={20} color="var(--accent-green)" /></div>
                    <div className="empty-state-title">No alerts matching filter</div>
                    <div className="empty-state-sub">
                        Run demo_runner.py to simulate live security events
                    </div>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {filtered.map(alert => (
                        <AlertCard
                            key={alert.id}
                            alert={alert}
                            query={queries[alert.query_id]}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default Alerts;
