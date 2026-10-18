import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
    ShieldCheck, 
    LayoutDashboard, 
    AlertTriangle, 
    Database, 
    Monitor, 
    Camera, 
    Globe, 
    Cpu 
} from 'lucide-react';
import { getAlerts, getOverviewStatus } from '../api/client';

const navItems = [
    { path: '/',         name: 'Overview',             subtitle: '4-Layer Command Center', icon: LayoutDashboard },
    { path: '/activity', name: 'L1: Postgres Proxy',   subtitle: 'v3 Wire DPI & Isolation', icon: Database },
    { path: '/model',    name: 'L1: Query Tester',     subtitle: 'Inline Socket Dropper',   icon: Cpu },
    { path: '/health',   name: 'L2: Panasonic Displays', subtitle: 'Showroom Telemetry',    icon: Monitor },
    { path: '/cctv',     name: 'L3: YOLOv8 CCTV',      subtitle: 'Zone Intrusion Engine',  icon: Camera },
    { path: '/phishing', name: 'L4: Phishing Guard',   subtitle: '7-Feature XGBoost',      icon: Globe },
    { path: '/alerts',   name: 'Incidents & Alerts',   subtitle: 'Ollama GenAI Briefings', icon: AlertTriangle },
];

const Sidebar = () => {
    const location = useLocation();
    const [alertCount, setAlertCount] = useState(0);
    const [statusInfo, setStatusInfo] = useState(null);

    useEffect(() => {
        const fetchStatus = () => {
            getAlerts(50).then(res => setAlertCount(res.data.length)).catch(() => {});
            getOverviewStatus().then(res => setStatusInfo(res.data)).catch(() => {});
        };
        fetchStatus();
        const id = setInterval(fetchStatus, 15000);
        return () => clearInterval(id);
    }, []);

    return (
        <div className="sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">
                    <ShieldCheck size={18} color="#fff" />
                </div>
                <div>
                    <div className="sidebar-logo-text">UnderSec</div>
                    <div className="sidebar-logo-sub">Enterprise & Showroom</div>
                </div>
            </div>

            {/* Nav */}
            <div style={{ marginBottom: '8px' }}>
                <div className="sidebar-section-label">4-Layer Security Suite</div>
            </div>
            <nav className="sidebar-nav">
                {navItems.map(({ path, name, subtitle, icon: Icon }) => {
                    const isActive = location.pathname === path;
                    return (
                        <Link
                            key={path}
                            to={path}
                            className={`sidebar-link ${isActive ? 'active' : ''}`}
                            style={{ height: 'auto', padding: '9px 12px' }}
                        >
                            <span className="sidebar-link-icon" style={{ marginTop: '2px' }}>
                                <Icon size={16} />
                            </span>
                            <div style={{ flex: 1, overflow: 'hidden' }}>
                                <div style={{ fontWeight: 600, fontSize: '13px' }}>{name}</div>
                                <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>{subtitle}</div>
                            </div>
                            {name.includes('Alerts') && alertCount > 0 && (
                                <span className="sidebar-link-badge">{alertCount}</span>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer Status */}
            <div className="sidebar-footer">
                <div className="status-pill" style={{ marginBottom: 6 }}>
                    <div className="status-dot" style={{ background: statusInfo?.genai?.ollama_online ? 'var(--accent-green)' : 'var(--accent-yellow)' }} />
                    <span className="status-pill-label">GenAI LLM</span>
                    <span className="status-pill-value">{statusInfo?.genai?.ollama_online ? 'Ollama' : 'Deterministic'}</span>
                </div>
                <div className="status-pill">
                    <div className="status-dot" />
                    <span className="status-pill-label">Proxy Port</span>
                    <span className="status-pill-value">:5432</span>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;