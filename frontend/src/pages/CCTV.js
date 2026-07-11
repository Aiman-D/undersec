import React, { useState, useEffect } from 'react';
import { ShieldAlert } from 'lucide-react';
import { getCCTVFeed } from '../api/client';

const CCTV = () => {
    const [feed, setFeed] = useState(null);
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        const fetchFeed = async () => {
            try {
                const res = await getCCTVFeed();
                setFeed(res.data);
                
                if (res.data.status === 'ALERT') {
                    const newAlert = {
                        id: Date.now(),
                        time: new Date(res.data.timestamp * 1000).toLocaleTimeString(),
                        score: res.data.anomaly_score
                    };
                    setAlerts(prev => [newAlert, ...prev].slice(0, 5));
                }
            } catch (err) {
                console.error(err);
            }
        };

        fetchFeed();
        const id = setInterval(fetchFeed, 1000); // Poll 1 FPS
        return () => clearInterval(id);
    }, []);

    return (
        <div className="page fade-in">
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1 className="page-title">CCTV Anomaly Detection</h1>
                    <p className="page-subtitle">Real-time computer vision analysis of showroom feeds.</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,0,0,0.1)', color: '#ef4444', padding: '6px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: 600 }}>
                    <div style={{ width: '8px', height: '8px', background: '#ef4444', borderRadius: '50%', animation: 'pulse 2s infinite' }} />
                    LIVE FEED
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '24px' }}>
                {/* Main Feed Container */}
                <div className="card" style={{ padding: '0', overflow: 'hidden', position: 'relative', background: '#0a0d14', height: '500px', border: feed?.status === 'ALERT' ? '2px solid #ef4444' : '1px solid var(--border)' }}>
                    
                    {/* Simulated Camera Background (Noise or static image placeholder) */}
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.2, backgroundImage: 'radial-gradient(#444 1px, transparent 1px)', backgroundSize: '10px 10px' }} />
                    
                    {/* Draw Bounding Boxes */}
                    {feed?.detections?.map((box, i) => (
                        <div key={i} style={{
                            position: 'absolute',
                            left: `${box.x}px`,
                            top: `${box.y}px`,
                            width: `${box.w}px`,
                            height: `${box.h}px`,
                            border: box.label.includes('unauthorized') ? '2px solid #ef4444' : '2px solid #22c55e',
                            backgroundColor: box.label.includes('unauthorized') ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
                            transition: 'all 0.3s ease'
                        }}>
                            <div style={{
                                position: 'absolute',
                                top: '-24px',
                                left: '-2px',
                                background: box.label.includes('unauthorized') ? '#ef4444' : '#22c55e',
                                color: '#fff',
                                fontSize: '11px',
                                padding: '2px 6px',
                                fontWeight: 600,
                                whiteSpace: 'nowrap'
                            }}>
                                {box.label.toUpperCase()} {Math.round(box.confidence * 100)}%
                            </div>
                        </div>
                    ))}
                    
                    {/* Overlay Stats */}
                    <div style={{ position: 'absolute', bottom: '20px', left: '20px', color: 'rgba(255,255,255,0.7)', fontSize: '12px', fontFamily: 'monospace' }}>
                        CAM-01 SHOWROOM<br/>
                        {new Date().toLocaleString()}<br/>
                        ANOMALY SCORE: {feed ? feed.anomaly_score : '0.00'}
                    </div>
                </div>

                {/* Alerts Sidebar */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                    <div className="card-header" style={{ paddingBottom: '16px', borderBottom: '1px solid var(--border)' }}>
                        <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <ShieldAlert size={16} /> Security Alerts
                        </div>
                    </div>
                    <div style={{ flex: 1, overflowY: 'auto', paddingTop: '16px' }}>
                        {alerts.length === 0 ? (
                            <div style={{ textAlign: 'center', color: '#8892a4', fontSize: '13px', marginTop: '20px' }}>
                                No recent alerts detected.
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                {alerts.map(alert => (
                                    <div key={alert.id} style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderLeft: '3px solid #ef4444', borderRadius: '4px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <span style={{ color: '#ef4444', fontWeight: 600, fontSize: '13px' }}>Unauthorized Access</span>
                                            <span style={{ color: '#8892a4', fontSize: '12px' }}>{alert.time}</span>
                                        </div>
                                        <div style={{ color: '#cbd5e1', fontSize: '12px' }}>
                                            Anomaly Score: {alert.score}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CCTV;
