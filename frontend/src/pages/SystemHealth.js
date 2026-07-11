import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Server, HardDrive, Cpu, Activity } from 'lucide-react';
import { getSystemHealth } from '../api/client';

const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="stat-card" style={{ '--card-accent': color }}>
        <div className="stat-card-top">
            <span className="stat-card-label">{title}</span>
            <div className="stat-card-icon" style={{ background: `rgba(255,255,255,0.05)` }}>
                <Icon size={16} color={color} />
            </div>
        </div>
        <div className="stat-card-value" style={{ color }}>{value}</div>
    </div>
);

const SystemHealth = () => {
    const [history, setHistory] = useState([]);
    const [current, setCurrent] = useState(null);

    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const res = await getSystemHealth();
                const data = res.data;
                const now = new Date().toLocaleTimeString();
                const newPoint = {
                    time: now,
                    cpu: data.cpu_usage,
                    memory: data.memory_usage,
                    anomaly: data.anomaly_score
                };
                
                setCurrent(data);
                setHistory(prev => {
                    const next = [...prev, newPoint];
                    if (next.length > 20) return next.slice(1);
                    return next;
                });
            } catch (err) {
                console.error(err);
            }
        };

        fetchHealth();
        const id = setInterval(fetchHealth, 2000); // 2 second updates
        return () => clearInterval(id);
    }, []);

    return (
        <div className="page fade-in">
            <div className="page-header">
                <h1 className="page-title">System Health Monitoring</h1>
                <p className="page-subtitle">Real-time metrics and anomaly detection for server infrastructure.</p>
            </div>

            <div className="stat-grid" style={{ marginBottom: '24px' }}>
                <StatCard title="CPU Usage" value={current ? `${current.cpu_usage}%` : '--'} icon={Cpu} color="var(--accent-blue)" />
                <StatCard title="Memory Usage" value={current ? `${current.memory_usage}%` : '--'} icon={Server} color="var(--accent-yellow)" />
                <StatCard title="Disk Usage" value={current ? `${current.disk_usage}%` : '--'} icon={HardDrive} color="var(--text-secondary)" />
                <StatCard title="Anomaly Score" value={current ? current.anomaly_score : '--'} icon={Activity} color={current && current.status === 'WARNING' ? 'var(--accent-red)' : 'var(--accent-green)'} />
            </div>

            <div className="card">
                <div className="card-header">
                    <div>
                        <div className="card-title">Resource Utilization Over Time</div>
                        <div className="card-subtitle">Live CPU and Memory tracking</div>
                    </div>
                    <span className="card-tag">Live</span>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                            </linearGradient>
                            <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <XAxis dataKey="time" tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 100]} />
                        <Tooltip 
                            contentStyle={{ background: '#141920', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                        />
                        <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" name="CPU %" />
                        <Area type="monotone" dataKey="memory" stroke="#f59e0b" fillOpacity={1} fill="url(#colorMem)" name="Memory %" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default SystemHealth;
