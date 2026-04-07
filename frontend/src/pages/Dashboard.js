import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { ShieldAlert, Ban, CheckCircle, Database } from 'lucide-react';
import { getActivity } from '../api/client';

const COLORS = ['#4ade80', '#fbbf24', '#f87171']; // Safe (Green), Flagged (Yellow), Blocked (Red)

const Dashboard = () => {
    const [stats, setStats] = useState({ total: 0, safe: 0, flagged: 0, blocked: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch the latest 100 queries from your FastAPI backend
                const response = await getActivity(100);
                const data = response.data;

                // Calculate stats
                let safe = 0, flagged = 0, blocked = 0;
                data.forEach(q => {
                    if (q.status === 'ALLOWED' && q.anomaly_score > -0.1) safe++;
                    else if (q.status === 'FLAGGED' || (q.status === 'ALLOWED' && q.anomaly_score <= -0.1)) flagged++;
                    else if (q.status === 'BLOCKED') blocked++;
                });

                setStats({ total: data.length, safe, flagged, blocked });
                setLoading(false);
            } catch (error) {
                console.error("Error fetching data:", error);
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Format data for the charts
    const pieData = [
        { name: 'Safe', value: stats.safe },
        { name: 'Flagged', value: stats.flagged },
        { name: 'Blocked', value: stats.blocked }
    ];

    const StatCard = ({ title, value, icon, color }) => (
        <div style={{ backgroundColor: '#1e1e2f', padding: '20px', borderRadius: '12px', flex: 1, display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ backgroundColor: `${color}20`, padding: '15px', borderRadius: '10px', color: color }}>
                {icon}
            </div>
            <div>
                <h3 style={{ margin: 0, color: '#8b8b9e', fontSize: '14px', fontWeight: '500' }}>{title}</h3>
                <p style={{ margin: '5px 0 0 0', fontSize: '24px', fontWeight: 'bold', color: '#fff' }}>{value}</p>
            </div>
        </div>
    );

    return (
        <div style={{ padding: '30px', color: '#fff' }}>
            <h1 style={{ margin: '0 0 30px 0', fontSize: '24px' }}>Security Overview</h1>

            {/* Top Stat Cards */}
            <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                <StatCard title="Total Queries" value={stats.total} icon={<Database size={24} />} color="#60a5fa" />
                <StatCard title="Safe Traffic" value={stats.safe} icon={<CheckCircle size={24} />} color="#4ade80" />
                <StatCard title="Flagged Anomalies" value={stats.flagged} icon={<ShieldAlert size={24} />} color="#fbbf24" />
                <StatCard title="Blocked Attacks" value={stats.blocked} icon={<Ban size={24} />} color="#f87171" />
            </div>

            {/* Charts Section */}
            <div style={{ display: 'flex', gap: '20px', height: '350px' }}>
                
                {/* Risk Distribution Pie Chart */}
                <div style={{ flex: 1, backgroundColor: '#1e1e2f', padding: '20px', borderRadius: '12px' }}>
                    <h3 style={{ margin: '0 0 20px 0', color: '#e2e8f0', fontSize: '16px' }}>Risk Distribution</h3>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie data={pieData} cx="50%" cy="50%" innerRadius={80} outerRadius={110} paddingAngle={5} dataKey="value">
                                {pieData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: '#2d2d44', border: 'none', borderRadius: '8px', color: '#fff' }} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

            </div>
        </div>
    );
};

export default Dashboard;