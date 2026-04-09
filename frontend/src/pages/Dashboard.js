import React, { useState, useEffect, useCallback } from 'react';
import {
    AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { Database, CheckCircle2, AlertTriangle, Ban, RefreshCw } from 'lucide-react';
import { getActivity } from '../api/client';

const PIE_COLORS = {
    Safe:    '#22c55e',
    Flagged: '#f59e0b',
    Blocked: '#ef4444',
};

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div style={{
                background: '#141920',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 8,
                padding: '10px 14px',
                fontSize: 12,
            }}>
                <div style={{ color: '#8892a4', marginBottom: 4 }}>{label}</div>
                {payload.map(p => (
                    <div key={p.name} style={{ color: p.color, fontWeight: 600 }}>
                        {p.name}: {p.value}
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

const StatCard = ({ title, value, icon: Icon, color, bgColor, sub }) => (
    <div className="stat-card" style={{ '--card-accent': color }}>
        <div className="stat-card-top">
            <span className="stat-card-label">{title}</span>
            <div className="stat-card-icon" style={{ background: bgColor }}>
                <Icon size={16} color={color} />
            </div>
        </div>
        <div className="stat-card-value" style={{ color }}>{value}</div>
        {sub && <div className="stat-card-sub">{sub}</div>}
    </div>
);

const Dashboard = () => {
    const [stats, setStats]     = useState({ total: 0, safe: 0, flagged: 0, blocked: 0 });
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastRefresh, setLastRefresh] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res  = await getActivity(100);
            const data = res.data;

            let safe = 0, flagged = 0, blocked = 0;
            data.forEach(q => {
                if (q.status === 'BLOCKED') blocked++;
                else if (q.status === 'FLAGGED' || (q.status === 'ALLOWED' && q.anomaly_score <= -0.1)) flagged++;
                else safe++;
            });

            setStats({ total: data.length, safe, flagged, blocked });

            // Build sparkline: group last 20 entries into buckets of 4
            const reversed = [...data].reverse();
            const buckets  = [];
            const size     = 5;
            for (let i = 0; i < Math.min(reversed.length, 20); i += size) {
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
        const id = setInterval(fetchData, 20000);
        return () => clearInterval(id);
    }, [fetchData]);

    const pieData = [
        { name: 'Safe',    value: stats.safe },
        { name: 'Flagged', value: stats.flagged },
        { name: 'Blocked', value: stats.blocked },
    ].filter(d => d.value > 0);

    const threatRate = stats.total > 0
        ? (((stats.flagged + stats.blocked) / stats.total) * 100).toFixed(1)
        : '0.0';

    return (
        <div className="page fade-in">
            {/* Header */}
            <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div>
                    <h1 className="page-title">Security Overview</h1>
                    <p className="page-subtitle">
                        Real-time monitoring of your database query gateway
                        {lastRefresh && (
                            <span style={{ marginLeft: 12, color: '#4d5a6b' }}>
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
                    Refresh
                </button>
            </div>

            {/* Stat Cards */}
            <div className="stat-grid">
                <StatCard
                    title="Total Queries"
                    value={stats.total}
                    icon={Database}
                    color="var(--accent-blue)"
                    bgColor="var(--accent-blue-glow)"
                    sub="Last 100 requests"
                />
                <StatCard
                    title="Safe Traffic"
                    value={stats.safe}
                    icon={CheckCircle2}
                    color="var(--accent-green)"
                    bgColor="var(--accent-green-glow)"
                    sub={stats.total > 0 ? `${((stats.safe / stats.total) * 100).toFixed(0)}% pass rate` : '—'}
                />
                <StatCard
                    title="Flagged"
                    value={stats.flagged}
                    icon={AlertTriangle}
                    color="var(--accent-yellow)"
                    bgColor="var(--accent-yellow-glow)"
                    sub="Needs review"
                />
                <StatCard
                    title="Blocked"
                    value={stats.blocked}
                    icon={Ban}
                    color="var(--accent-red)"
                    bgColor="var(--accent-red-glow)"
                    sub={`${threatRate}% threat rate`}
                />
            </div>

            {/* Charts */}
            <div className="charts-grid">
                {/* Area Chart */}
                <div className="card">
                    <div className="card-header">
                        <div>
                            <div className="card-title">Traffic Breakdown</div>
                            <div className="card-subtitle">Query status over recent batches</div>
                        </div>
                        <span className="card-tag">Live</span>
                    </div>
                    {loading ? (
                        <div className="loading-pulse"><span /><span /><span /></div>
                    ) : history.length > 0 ? (
                        <ResponsiveContainer width="100%" height={220}>
                            <AreaChart data={history} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="gSafe"    x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.25} />
                                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="gFlagged" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.25} />
                                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="gBlocked" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.25} />
                                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="name" tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                                <Tooltip content={<CustomTooltip />} />
                                <Area type="monotone" dataKey="Safe"    stroke="#22c55e" strokeWidth={2} fill="url(#gSafe)" />
                                <Area type="monotone" dataKey="Flagged" stroke="#f59e0b" strokeWidth={2} fill="url(#gFlagged)" />
                                <Area type="monotone" dataKey="Blocked" stroke="#ef4444" strokeWidth={2} fill="url(#gBlocked)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="empty-state">
                            <div className="empty-state-icon"><Database size={20} /></div>
                            <div className="empty-state-title">No data yet</div>
                            <div className="empty-state-sub">Run some queries through the gateway to see data here</div>
                        </div>
                    )}
                </div>

                {/* Pie Chart */}
                <div className="card">
                    <div className="card-header">
                        <div>
                            <div className="card-title">Risk Distribution</div>
                            <div className="card-subtitle">Query classification breakdown</div>
                        </div>
                    </div>
                    {loading ? (
                        <div className="loading-pulse"><span /><span /><span /></div>
                    ) : pieData.length > 0 ? (
                        <>
                            <ResponsiveContainer width="100%" height={160}>
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%" cy="50%"
                                        innerRadius={50} outerRadius={72}
                                        paddingAngle={3}
                                        dataKey="value"
                                        stroke="none"
                                    >
                                        {pieData.map((entry) => (
                                            <Cell key={entry.name} fill={PIE_COLORS[entry.name]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{
                                            background: '#141920',
                                            border: '1px solid rgba(255,255,255,0.08)',
                                            borderRadius: 8,
                                            fontSize: 12,
                                        }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="pie-legend">
                                {pieData.map(d => (
                                    <div key={d.name} className="pie-legend-item">
                                        <div className="pie-legend-dot" style={{ background: PIE_COLORS[d.name] }} />
                                        <span className="pie-legend-name">{d.name}</span>
                                        <span className="pie-legend-value" style={{ color: PIE_COLORS[d.name] }}>{d.value}</span>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div className="empty-state" style={{ padding: '30px 20px' }}>
                            <div className="empty-state-title" style={{ fontSize: 13 }}>No data</div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;