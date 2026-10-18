import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
    AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import { 
    Database, 
    Sparkles, 
    RefreshCw, 
    ArrowRight
} from 'lucide-react';
import { 
    getOverviewStatus, 
    getIncidentSummary, 
    summarizeCustomIncidents, 
    getActivity, 
    triggerCCTVIntrusion,
    CCTV_FRAME_URL 
} from '../api/client';

const Dashboard = () => {
    const [overview, setOverview] = useState(null);
    const [incidentSummary, setIncidentSummary] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [summarizing, setSummarizing] = useState(false);
    const [lastRefresh, setLastRefresh] = useState(null);

    const fetchData = useCallback(async () => {
        try {
            const [ovRes, sumRes, actRes] = await Promise.all([
                getOverviewStatus().catch(() => ({ data: null })),
                getIncidentSummary().catch(() => ({ data: { summary: null } })),
                getActivity(100).catch(() => ({ data: [] }))
            ]);

            setOverview(ovRes.data);
            setIncidentSummary(sumRes.data?.summary);

            const data = actRes.data || [];
            const reversed = [...data].reverse();
            const buckets = [];
            const size = 5;
            for (let i = 0; i < Math.min(reversed.length, 25); i += size) {
                const chunk = reversed.slice(i, i + size);
                const s = chunk.filter(q => q.status !== 'BLOCKED' && q.status !== 'FLAGGED').length;
                const f = chunk.filter(q => q.status === 'FLAGGED').length;
                const b = chunk.filter(q => q.status === 'BLOCKED').length;
                buckets.push({ name: `T-${buckets.length + 1}`, Safe: s, Flagged: f, Blocked: b });
            }
            setHistory(buckets.reverse());
            setLastRefresh(new Date());
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const id = setInterval(fetchData, 12000);
        return () => clearInterval(id);
    }, [fetchData]);

    const handleGenerateAIIncidentSummary = async () => {
        setSummarizing(true);
        try {
            const res = await summarizeCustomIncidents();
            setIncidentSummary(res.data?.summary);
        } catch (err) {
            console.error(err);
        } finally {
            setSummarizing(false);
        }
    };

    const handleTriggerCCTVDemo = async () => {
        try {
            await triggerCCTVIntrusion('ZONE-01-CONCEPT', 10.0);
            fetchData();
        } catch (err) {
            console.error(err);
        }
    };

    const l1 = overview?.layers?.layer1_db_proxy;
    const l2 = overview?.layers?.layer2_showroom_telemetry;
    const l3 = overview?.layers?.layer3_cctv_engine;
    const l4 = overview?.layers?.layer4_phishing_guard;

    const threatRate = l1 && l1.total_queries > 0
        ? (((l1.blocked_sockets + l1.flagged_queries) / l1.total_queries) * 100).toFixed(1)
        : '0.0';

    return (
        <div className="page fade-in">
            {/* Header */}
            <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <h1 className="page-title">UnderSec Security Suite</h1>
                        <span style={{ 
                            background: 'rgba(59, 130, 246, 0.15)', 
                            border: '1px solid rgba(59, 130, 246, 0.3)', 
                            color: 'var(--accent-blue)', 
                            padding: '3px 10px', 
                            borderRadius: '12px', 
                            fontSize: '11px', 
                            fontWeight: 700 
                        }}>
                            Track Winner Apr 2026
                        </span>
                    </div>
                    <p className="page-subtitle">
                        4-Layer Enterprise & Panasonic Showroom Security Suite: PostgreSQL v3 DPI Proxy, Display Diagnostics, YOLOv8 CCTV & XGBoost Phishing
                        {lastRefresh && (
                            <span style={{ marginLeft: 12, color: 'var(--text-muted)' }}>
                                · Updated {lastRefresh.toLocaleTimeString()}
                            </span>
                        )}
                    </p>
                </div>
                <button
                    onClick={fetchData}
                    disabled={loading}
                    style={{
                        display: 'flex', alignItems: 'center', gap: 6,
                        background: 'var(--bg-card)', border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)',
                        fontSize: 12, fontWeight: 500, padding: '8px 14px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        transition: 'all 0.15s', fontFamily: 'inherit', outline: 'none',
                    }}
                >
                    <RefreshCw size={13} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                    Refresh Suite
                </button>
            </div>

            {/* GenAI Incident Summarization Banner */}
            <div className="incident-briefing-card fade-in">
                <div className="briefing-header">
                    <div className="briefing-title">
                        <Sparkles size={18} color="#a78bfa" />
                        Ollama LLM Multi-Layer Security Briefing
                        <span style={{ 
                            fontSize: '10px', 
                            padding: '2px 8px', 
                            borderRadius: '12px', 
                            background: incidentSummary?.threat_level === 'CRITICAL' || incidentSummary?.threat_level === 'HIGH' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                            color: incidentSummary?.threat_level === 'CRITICAL' || incidentSummary?.threat_level === 'HIGH' ? 'var(--accent-red)' : 'var(--accent-green)',
                            border: '1px solid currentColor',
                            fontWeight: 700
                        }}>
                            THREAT LEVEL: {incidentSummary?.threat_level || 'NORMAL'}
                        </span>
                    </div>
                    <button
                        onClick={handleGenerateAIIncidentSummary}
                        disabled={summarizing}
                        style={{
                            display: 'flex', alignItems: 'center', gap: 6,
                            background: 'rgba(139, 92, 246, 0.25)', border: '1px solid rgba(139, 92, 246, 0.5)',
                            borderRadius: 'var(--radius-sm)', color: '#e9d5ff',
                            fontSize: 11, fontWeight: 600, padding: '6px 12px',
                            cursor: summarizing ? 'not-allowed' : 'pointer',
                            transition: 'all 0.15s', outline: 'none',
                        }}
                    >
                        <Sparkles size={12} style={{ animation: summarizing ? 'spin 1s linear infinite' : 'none' }} />
                        {summarizing ? 'Correlating Telemetry...' : 'Generate AI Briefing'}
                    </button>
                </div>

                <div className="briefing-text">
                    {incidentSummary?.executive_summary || "Ollama LLM engine actively monitoring all 4 UnderSec security layers. Click 'Generate AI Briefing' to synthesize current database, showroom hardware, CCTV, and phishing events."}
                </div>

                {incidentSummary?.action_items && (
                    <div className="briefing-actions">
                        <span style={{ fontSize: 11, color: '#a78bfa', fontWeight: 600, alignSelf: 'center', marginRight: 4 }}>
                            Immediate Containment:
                        </span>
                        {incidentSummary.action_items.map((item, idx) => (
                            <div key={idx} className="briefing-action-chip">
                                • {item}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* The 4 Architecture Layers Grid */}
            <div className="layer-grid">
                {/* Layer 1 */}
                <div className="layer-card">
                    <span className="layer-card-tag" style={{ background: 'rgba(59, 130, 246, 0.2)', color: 'var(--accent-blue)' }}>
                        Layer 1 · PostgreSQL Proxy
                    </span>
                    <div className="layer-card-title">v3 Wire Protocol DPI</div>
                    <div className="layer-card-desc">
                        Asyncio TCP proxy on port 5432 with sqlparse AST inspection & inline Isolation Forest scoring to drop SQLi sockets.
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                        <div>
                            <div className="layer-card-metric text-blue">{l1?.blocked_sockets ?? 0} Dropped</div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{l1?.total_queries ?? 0} total queries · {threatRate}% threat</div>
                        </div>
                        <Link to="/activity" style={{ color: 'var(--accent-blue)', display: 'flex', alignItems: 'center' }}>
                            <ArrowRight size={15} />
                        </Link>
                    </div>
                </div>

                {/* Layer 2 */}
                <div className="layer-card">
                    <span className="layer-card-tag" style={{ background: 'rgba(34, 197, 94, 0.2)', color: 'var(--accent-green)' }}>
                        Layer 2 · Panasonic Telemetry
                    </span>
                    <div className="layer-card-title">Vehicle Configurator Displays</div>
                    <div className="layer-card-desc">
                        Real-time hardware health telemetry across 5 interactive vehicle-configurator displays (FPS, GPU/panel thermal, touch latency).
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                        <div>
                            <div className="layer-card-metric text-green">{l2?.fleet_health_score ?? 100}% Health</div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                {l2?.counts?.healthy ?? 5} Healthy · {l2?.averages?.avg_fps ?? 60} avg FPS
                            </div>
                        </div>
                        <Link to="/health" style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center' }}>
                            <ArrowRight size={15} />
                        </Link>
                    </div>
                </div>

                {/* Layer 3 */}
                <div className="layer-card">
                    <span className="layer-card-tag" style={{ background: 'rgba(245, 158, 11, 0.2)', color: 'var(--accent-yellow)' }}>
                        Layer 3 · Computer Vision
                    </span>
                    <div className="layer-card-title">YOLOv8 CCTV Zone Engine</div>
                    <div className="layer-card-desc">
                        Real-time spatial bounding-box zone intrusion detection over restricted concept vehicle stage & DB proxy enclosure.
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                        <div>
                            <div className="layer-card-metric" style={{ color: l3?.has_breach ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                                {l3?.has_breach ? 'BREACH ALERT' : 'SECURE'}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                Score: {l3?.anomaly_score ?? '0.0'} · 3 zones active
                            </div>
                        </div>
                        <Link to="/cctv" style={{ color: 'var(--accent-yellow)', display: 'flex', alignItems: 'center' }}>
                            <ArrowRight size={15} />
                        </Link>
                    </div>
                </div>

                {/* Layer 4 */}
                <div className="layer-card">
                    <span className="layer-card-tag" style={{ background: 'rgba(239, 68, 68, 0.2)', color: 'var(--accent-red)' }}>
                        Layer 4 · Client Phishing Guard
                    </span>
                    <div className="layer-card-title">7-Feature XGBoost Model</div>
                    <div className="layer-card-desc">
                        Real-time Chrome Extension inspecting URL length, host, digits, subdomains, IP presence, non-alnum ratio & Shannon entropy.
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                        <div>
                            <div className="layer-card-metric text-red">{l4?.phishing_blocked ?? 0} Blocked</div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                {l4?.scans_conducted ?? 0} URLs evaluated · 7 features
                            </div>
                        </div>
                        <Link to="/phishing" style={{ color: 'var(--accent-red)', display: 'flex', alignItems: 'center' }}>
                            <ArrowRight size={15} />
                        </Link>
                    </div>
                </div>
            </div>

            {/* Charts & Live Feeds Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 20 }}>
                {/* Traffic Breakdown Chart */}
                <div className="card">
                    <div className="card-header">
                        <div>
                            <div className="card-title">Database DPI Stream Telemetry</div>
                            <div className="card-subtitle">Real-time PostgreSQL query classification & socket status</div>
                        </div>
                        <span className="card-tag">Live Stream</span>
                    </div>

                    {loading ? (
                        <div className="loading-pulse"><span /><span /><span /></div>
                    ) : history.length > 0 ? (
                        <ResponsiveContainer width="100%" height={230}>
                            <AreaChart data={history} margin={{ top: 6, right: 10, left: -24, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="gSafe" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="gFlagged" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="gBlocked" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="name" tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                                <Tooltip 
                                    contentStyle={{ background: '#141920', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }}
                                />
                                <Area type="monotone" dataKey="Safe" stroke="#22c55e" strokeWidth={2} fill="url(#gSafe)" />
                                <Area type="monotone" dataKey="Flagged" stroke="#f59e0b" strokeWidth={2} fill="url(#gFlagged)" />
                                <Area type="monotone" dataKey="Blocked" stroke="#ef4444" strokeWidth={2} fill="url(#gBlocked)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="empty-state">
                            <div className="empty-state-icon"><Database size={20} /></div>
                            <div className="empty-state-title">Awaiting Gateway Traffic</div>
                            <div className="empty-state-sub">Run demo_runner.py to simulate live enterprise queries</div>
                        </div>
                    )}
                </div>

                {/* Live CCTV Mini Stream & Quick Trigger */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                    <div className="card-header" style={{ paddingBottom: 10 }}>
                        <div>
                            <div className="card-title">Live CCTV Showroom Feed</div>
                            <div className="card-subtitle">YOLOv8 Automated Spatial Tracking</div>
                        </div>
                        <span style={{ 
                            fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                            background: l3?.has_breach ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                            color: l3?.has_breach ? 'var(--accent-red)' : 'var(--accent-green)'
                        }}>
                            {l3?.has_breach ? 'ZONE BREACH' : 'SECURE'}
                        </span>
                    </div>

                    <div style={{ 
                        flex: 1, 
                        minHeight: 180, 
                        background: '#070a0f', 
                        borderRadius: 6, 
                        overflow: 'hidden', 
                        position: 'relative',
                        border: l3?.has_breach ? '2px solid var(--accent-red)' : '1px solid var(--border)'
                    }}>
                        <img 
                            src={`${CCTV_FRAME_URL}?t=${lastRefresh ? lastRefresh.getTime() : 0}`} 
                            alt="Live Showroom CCTV" 
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            onError={(e) => { e.target.style.display = 'none'; }}
                        />
                        <div style={{ position: 'absolute', bottom: 6, left: 8, fontSize: 10, fontFamily: 'monospace', color: 'rgba(255,255,255,0.7)' }}>
                            CAM-04 · CONCEPT EV STAGE
                        </div>
                    </div>

                    <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                        <button
                            onClick={handleTriggerCCTVDemo}
                            style={{
                                flex: 1,
                                background: 'rgba(239, 68, 68, 0.15)',
                                border: '1px solid rgba(239, 68, 68, 0.4)',
                                color: 'var(--accent-red)',
                                padding: '6px 10px',
                                borderRadius: 6,
                                fontSize: 11,
                                fontWeight: 600,
                                cursor: 'pointer'
                            }}
                        >
                            Simulate Zone Breach
                        </button>
                        <Link
                            to="/cctv"
                            style={{
                                background: 'var(--bg-elevated)',
                                border: '1px solid var(--border)',
                                color: 'var(--text-secondary)',
                                padding: '6px 12px',
                                borderRadius: 6,
                                fontSize: 11,
                                fontWeight: 500,
                                textDecoration: 'none',
                                display: 'flex',
                                alignItems: 'center'
                            }}
                        >
                            Full View →
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;