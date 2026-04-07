import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, Activity, AlertTriangle, Settings } from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();

    const navItems = [
        { path: '/', name: 'Dashboard', icon: <Activity size={20} /> },
        { path: '/alerts', name: 'Alerts', icon: <AlertTriangle size={20} /> },
        { path: '/activity', name: 'Activity Log', icon: <Shield size={20} /> },
        { path: '/model', name: 'Model Control', icon: <Settings size={20} /> }
    ];

    return (
        <div style={{ width: '250px', backgroundColor: '#1e1e2f', color: '#fff', height: '100vh', padding: '20px', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#4ade80', marginBottom: '40px', marginTop: '10px' }}>
                <Shield size={28} /> Undersec
            </h2>
            
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {navItems.map((item) => (
                    <Link 
                        key={item.path} 
                        to={item.path}
                        style={{
                            display: 'flex', alignItems: 'center', gap: '12px', padding: '12px',
                            textDecoration: 'none', borderRadius: '8px',
                            color: location.pathname === item.path ? '#fff' : '#8b8b9e',
                            backgroundColor: location.pathname === item.path ? '#2d2d44' : 'transparent',
                            transition: 'all 0.2s ease-in-out'
                        }}
                    >
                        {item.icon} {item.name}
                    </Link>
                ))}
            </nav>
        </div>
    );
};

export default Sidebar;