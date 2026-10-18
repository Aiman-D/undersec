import React, { useState, useEffect, useCallback } from 'react';
import { ShieldAlert, Zap, CheckCircle } from 'lucide-react';
import { getCCTVFeed, triggerCCTVIntrusion, clearCCTVIntrusion, CCTV_FRAME_URL } from '../api/client';

const CCTV = () => {
    const [feed, setFeed] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [refreshNonce, setRefreshNonce] = useState(Date.now());

    const fetchFeed = useCallback(async () => {
        try {
            const res = await getCCTVFeed();
            setFeed(res.data);
            setRefreshNonce(Date.now());
            
            if (res.data.has_breach || res.data.status === 'ALERT') {
                const newAlert = {
                    id: Date.now(),
                    time: new Date(res.data.timestamp * 1000).toLocaleTimeString(),
                    score: res.data.anomaly_score,
                    zone: res.data.intrusions?.[0]?.zone_name || 'Restricted Showroom Zone',
                    severity: res.data.intrusions?.[0]?.severity || 'HIGH'
                };
                setAlerts(prev => [newAlert, ...prev.slice(0, 9)]);
            }
        } catch (err) {
            console.error(err);
        }
    }, []);

    useEffect(() => {
        fetchFeed();
        const id = setInterval(fetchFeed, 1000); // 1 FPS polling
        return () => clearInterval(id);
    }, [fetchFeed]);

    const handleTrigger = async (zoneId) => {
        setLoading(true);
        try {
            await triggerCCTVIntrusion(zoneId, 12.0);
            await fetchFeed();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = async () => {
        setLoading(true);
        try {
            await clearCCTVIntrusion();
            await fetchFeed();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const hasBreach = feed?.has_breach || feed?.status === 'ALERT';

    return (
        <div className="page fade-in">
            {/* Header */}
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <h1 className="page-title">YOLOv8 CCTV Zone-Intrusion Engine</h1>
                        <span style={{ 
                            background: 'rgba(245, 158, 11, 0.15)', 
                            border: '1px solid rgba(245, 158, 11, 0.3)', 
                            color: 'var(--accent-yellow)', 
                            padding: '3px 10px', 
                            borderRadius: '12px', 
                            fontSize: '11px', 
                            fontWeight: 700 
                        }}>
                            Layer 3 · Vision AI
                        </span>
                    </div>
                    <p className="page-subtitle">
                        Real-time YOLOv8 computer vision inference tracking spatial bounding-box zone intrusions across showroom stages & proxy infrastructure
                    </p>
                </div>
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 8, 
                    background: hasBreach ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)', 
                    color: hasBreach ? 'var(--accent-red)' : 'var(--accent-green)', 
                    border: `1px solid ${hasBreach ? 'rgba(239, 68, 68, 0.4)' : 'rgba(34, 197, 94, 0.4)'}`,
                    padding: '6px 14px', 
                    borderRadius: '20px', 
                    fontSize: '12px', 
                    fontWeight: 700 
                }}>
                    <div style={{ 
                        width: 8, 
                        height: 8, 
                        background: hasBreach ? 'var(--accent-red)' : 'var(--accent-green)', 
                        borderRadius: '50%', 
                        animation: 'bounce 1s infinite' 
                    }} />
                    {hasBreach ? 'PERIMETER BREACH ACTIVE' : 'PERIMETER SECURE'}
                </div>
            </div>

            {/* Quick Trigger Bar */}
            <div className="card" style={{ padding: '12px 18px', marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Zap size={15} color="var(--accent-yellow)" />
                    <span style={{ fontSize: 12, fontWeight: 600, color: '#fff' }}>Simulate Zone Intrusion:</span>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    <button
                        onClick={() => handleTrigger('ZONE-01-CONCEPT')}
                        disabled={loading}
                        style={{
                            background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)',
                            color: 'var(--accent-red)', padding: '6px 12px', borderRadius: 6,
                            fontSize: 11, fontWeight: 600, cursor: 'pointer'
                        }}
                    >
                        Concept Vehicle Stage Breach
                    </button>
                    <button
                        onClick={() => handleTrigger('ZONE-02-PROXY-CORE')}
                        disabled={loading}
                        style={{
                            background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.4)',
                            color: 'var(--accent-yellow)', padding: '6px 12px', borderRadius: 6,
                            fontSize: 11, fontWeight: 600, cursor: 'pointer'
                        }}
                    >
                        DB Proxy Cabinet Enclosure Breach
                    </button>
                    <button
                        onClick={handleClear}
                        disabled={loading}
                        style={{
                            background: 'var(--bg-elevated)', border: '1px solid var(--border)',
                            color: 'var(--text-secondary)', padding: '6px 12px', borderRadius: 6,
                            fontSize: 11, fontWeight: 500, cursor: 'pointer'
                        }}
                    >
                        Clear Intrusion
                    </button>
                </div>
            </div>

            {/* Main Visual Feed and Events Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
                {/* Camera Live Stream Card */}
                <div className="card" style={{ padding: 0, overflow: 'hidden', border: hasBreach ? '2px solid var(--accent-red)' : '1px solid var(--border)' }}>
                    <div style={{ position: 'relative', width: '100%', minHeight: 480, background: '#070a0f' }}>
                        <img 
                            src={`${CCTV_FRAME_URL}?t=${refreshNonce}`} 
                            alt="YOLOv8 Live CCTV Feed"
                            style={{ width: '100%', height: '100%', display: 'block', objectFit: 'contain' }}
                        />
                        
                        {/* Stream Watermark / HUD */}
                        <div style={{ 
                            position: 'absolute', 
                            top: 10, 
                            left: 10, 
                            background: 'rgba(10, 14, 22, 0.85)', 
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: 4,
                            padding: '4px 8px',
                            fontSize: 11,
                            fontFamily: 'monospace',
                            color: '#93c5fd'
                        }}>
                            CAM-04 · SHOWROOM HQ · 1080P
                        </div>

                        <div style={{ 
                            position: 'absolute', 
                            top: 10, 
                            right: 10, 
                            background: hasBreach ? 'rgba(239, 68, 68, 0.9)' : 'rgba(34, 197, 94, 0.9)', 
                            color: '#fff',
                            borderRadius: 4,
                            padding: '4px 10px',
                            fontSize: 11,
                            fontWeight: 700,
                            letterSpacing: '0.05em'
                        }}>
                            {hasBreach ? 'INTRUSION DETECTED' : 'ALL ZONES CLEAR'}
                        </div>
                    </div>

                    {/* Active Zones Legend */}
                    <div style={{ padding: '12px 18px', background: 'var(--bg-card)', borderTop: '1px solid var(--border)', display: 'flex', gap: 16 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
                            <div style={{ width: 10, height: 10, borderRadius: 2, background: 'var(--accent-red)' }} />
                            <span>Zone 1: Concept EV Stage (Restricted)</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
                            <div style={{ width: 10, height: 10, borderRadius: 2, background: 'var(--accent-yellow)' }} />
                            <span>Zone 2: DB Proxy Core Cabinet (Critical)</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
                            <div style={{ width: 10, height: 10, borderRadius: 2, background: 'var(--accent-blue)' }} />
                            <span>Zone 3: Configurator Pods (Public)</span>
                        </div>
                    </div>
                </div>

                {/* Sidebar Alerts & Detection Logs */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {/* Live Telemetry Card */}
                    <div className="card" style={{ padding: 16 }}>
                        <div className="card-title" style={{ fontSize: 13, marginBottom: 10 }}>Inference Telemetry</div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                            <div style={{ background: 'var(--bg-surface)', padding: 8, borderRadius: 6 }}>
                                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>THREAT SCORE</div>
                                <div style={{ fontSize: 16, fontWeight: 700, fontFamily: 'monospace', color: hasBreach ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                                    {feed ? feed.anomaly_score : '--'}
                                </div>
                            </div>
                            <div style={{ background: 'var(--bg-surface)', padding: 8, borderRadius: 6 }}>
                                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>TRACKED PERSONS</div>
                                <div style={{ fontSize: 16, fontWeight: 700, fontFamily: 'monospace', color: '#fff' }}>
                                    {feed?.detections?.length ?? 0}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Zone Security Events Log */}
                    <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                        <div className="card-header" style={{ paddingBottom: 12 }}>
                            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <ShieldAlert size={15} color="var(--accent-red)" />
                                CCTV Intrusion History
                            </div>
                        </div>

                        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
                            {alerts.length === 0 ? (
                                <div className="empty-state" style={{ padding: 30 }}>
                                    <div className="empty-state-icon"><CheckCircle size={18} color="var(--accent-green)" /></div>
                                    <div className="empty-state-sub">No recent perimeter breaches</div>
                                </div>
                            ) : (
                                alerts.map(a => (
                                    <div 
                                        key={a.id} 
                                        style={{ 
                                            background: 'rgba(239, 68, 68, 0.08)', 
                                            borderLeft: '3px solid var(--accent-red)', 
                                            borderRadius: 4, 
                                            padding: '8px 10px' 
                                        }}
                                    >
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                                            <span style={{ color: 'var(--accent-red)', fontWeight: 600, fontSize: 12 }}>
                                                {a.zone}
                                            </span>
                                            <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>{a.time}</span>
                                        </div>
                                        <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                                            Anomaly Score: <b>{a.score}</b> · Severity: {a.severity}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CCTV;
