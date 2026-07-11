import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard, AlertTriangle, ClipboardList, Cpu, Link as LinkIcon, Activity, Camera } from 'lucide-react';
import { getAlerts } from '../api/client';

const navItems = [
    { path: '/',          name: 'Dashboard',     icon: LayoutDashboard },
    { path: '/alerts',    name: 'Alerts',         icon: AlertTriangle },
    { path: '/activity',  name: 'Activity Log',   icon: ClipboardList },
    { path: '/model',     name: 'Query Tester',   icon: Cpu },
    { path: '/phishing',  name: 'Phishing',       icon: LinkIcon },
    { path: '/health',    name: 'System Health',  icon: Activity },
    { path: '/cctv',      name: 'CCTV Anomaly',   icon: Camera },
];

const Sidebar = () => {
    const location = useLocation();
    const [alertCount, setAlertCount] = useState(0);

    useEffect(() => {
        getAlerts(50).then(res => {
            setAlertCount(res.data.length);
        }).catch(() => {});
    }, []);

    return (
        <div className="sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">
                    <ShieldCheck size={16} color="#fff" />
                </div>
                <div>
                    <div className="sidebar-logo-text">Undersec</div>
                    <div className="sidebar-logo-sub">Security Gateway</div>
                </div>
            </div>

            {/* Nav */}
            <div style={{ marginBottom: '8px' }}>
                <div className="sidebar-section-label">Navigation</div>
            </div>
            <nav className="sidebar-nav">
                {navItems.map(({ path, name, icon: Icon }) => {
                    const isActive = location.pathname === path;
                    return (
                        <Link
                            key={path}
                            to={path}
                            className={`sidebar-link ${isActive ? 'active' : ''}`}
                        >
                            <span className="sidebar-link-icon">
                                <Icon size={15} />
                            </span>
                            {name}
                            {name === 'Alerts' && alertCount > 0 && (
                                <span className="sidebar-link-badge">{alertCount}</span>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer Status */}
            <div className="sidebar-footer">
                <div className="status-pill">
                    <div className="status-dot" />
                    <span className="status-pill-label">ML Engine</span>
                    <span className="status-pill-value">Active</span>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;