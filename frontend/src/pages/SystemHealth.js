import React, { useState, useEffect, useCallback } from 'react';
import { 
    AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer 
} from 'recharts';
import { 
    Thermometer, 
    Fingerprint, 
    Activity, 
    ShieldCheck, 
    RefreshCw, 
    Flame 
} from 'lucide-react';
import { 
    getShowroomFleet, 
    getShowroomDisplay, 
    injectShowroomFault, 
    clearAllShowroomFaults 
} from '../api/client';

const SystemHealth = () => {
    const [fleet, setFleet] = useState(null);
    const [selectedId, setSelectedId] = useState('PAN-CFG-01');
    const [selectedDetail, setSelectedDetail] = useState(null);
    const [injecting, setInjecting] = useState(false);

    const fetchFleetData = useCallback(async () => {
        try {
            const res = await getShowroomFleet();
            setFleet(res.data);
            
            // Fetch selected display detail
            const detailRes = await getShowroomDisplay(selectedId);
            setSelectedDetail(detailRes.data);
        } catch (err) {
            console.error(err);
        }
    }, [selectedId]);

    useEffect(() => {
        fetchFleetData();
        const id = setInterval(fetchFleetData, 2500);
        return () => clearInterval(id);
    }, [fetchFleetData]);

    const handleInjectFault = async (faultType) => {
        setInjecting(true);
        try {
            await injectShowroomFault(selectedId, faultType, 20.0);
            await fetchFleetData();
        } catch (err) {
            console.error(err);
        } finally {
            setInjecting(false);
        }
    };

    const handleClearFaults = async () => {
        setInjecting(true);
        try {
            await clearAllShowroomFaults();
            await fetchFleetData();
        } catch (err) {
            console.error(err);
        } finally {
            setInjecting(false);
        }
    };

    const currentDisplay = fleet?.displays?.find(d => d.id === selectedId) || fleet?.displays?.[0];

    return (
        <div className="page fade-in">
            {/* Header */}
            <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <h1 className="page-title">Panasonic Showroom Telemetry</h1>
                        <span style={{ 
                            background: 'rgba(34, 197, 94, 0.15)', 
                            border: '1px solid rgba(34, 197, 94, 0.3)', 
                            color: 'var(--accent-green)', 
                            padding: '3px 10px', 
                            borderRadius: '12px', 
                            fontSize: '11px', 
                            fontWeight: 700 
                        }}>
                            Layer 2 · Hardware Health
                        </span>
                    </div>
                    <p className="page-subtitle">
                        Real-time hardware health telemetry & device diagnostics tracking across interactive vehicle-configurator displays
                    </p>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    <button
                        onClick={handleClearFaults}
                        disabled={injecting}
                        style={{
                            background: 'var(--bg-elevated)', border: '1px solid var(--border)',
                            borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)',
                            fontSize: 12, fontWeight: 500, padding: '8px 14px', cursor: 'pointer'
                        }}
                    >
                        Restore Optimal State
                    </button>
                    <button
                        onClick={fetchFleetData}
                        style={{
                            display: 'flex', alignItems: 'center', gap: 6,
                            background: 'var(--bg-card)', border: '1px solid var(--border)',
                            borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)',
                            fontSize: 12, fontWeight: 500, padding: '8px 14px', cursor: 'pointer'
                        }}
                    >
                        <RefreshCw size={13} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Fleet Summary Cards */}
            <div className="stat-grid" style={{ marginBottom: 24 }}>
                <div className="stat-card" style={{ '--card-accent': 'var(--accent-green)' }}>
                    <div className="stat-card-top">
                        <span className="stat-card-label">Fleet Health Index</span>
                        <div className="stat-card-icon" style={{ background: 'var(--accent-green-glow)' }}>
                            <ShieldCheck size={16} color="var(--accent-green)" />
                        </div>
                    </div>
                    <div className="stat-card-value" style={{ color: 'var(--accent-green)' }}>
                        {fleet ? `${fleet.fleet_health_score}%` : '--'}
                    </div>
                    <div className="stat-card-sub">
                        {fleet?.counts?.healthy || 0} Healthy · {fleet?.counts?.warning || 0} Warning · {fleet?.counts?.critical || 0} Critical
                    </div>
                </div>

                <div className="stat-card" style={{ '--card-accent': 'var(--accent-blue)' }}>
                    <div className="stat-card-top">
                        <span className="stat-card-label">3D Rendering Rate</span>
                        <div className="stat-card-icon" style={{ background: 'var(--accent-blue-glow)' }}>
                            <Activity size={16} color="var(--accent-blue)" />
                        </div>
                    </div>
                    <div className="stat-card-value text-blue">
                        {fleet ? `${fleet.averages?.avg_fps} FPS` : '--'}
                    </div>
                    <div className="stat-card-sub">Real-time Unreal / WebGL viewport</div>
                </div>

                <div className="stat-card" style={{ '--card-accent': 'var(--accent-yellow)' }}>
                    <div className="stat-card-top">
                        <span className="stat-card-label">Average GPU Core</span>
                        <div className="stat-card-icon" style={{ background: 'var(--accent-yellow-glow)' }}>
                            <Thermometer size={16} color="var(--accent-yellow)" />
                        </div>
                    </div>
                    <div className="stat-card-value" style={{ color: 'var(--accent-yellow)' }}>
                        {fleet ? `${fleet.averages?.avg_gpu_temp_c} °C` : '--'}
                    </div>
                    <div className="stat-card-sub">Nominal threshold &lt; 78°C</div>
                </div>

                <div className="stat-card" style={{ '--card-accent': 'var(--accent-purple)' }}>
                    <div className="stat-card-top">
                        <span className="stat-card-label">Touch Input Latency</span>
                        <div className="stat-card-icon" style={{ background: 'var(--accent-purple-glow)' }}>
                            <Fingerprint size={16} color="var(--accent-purple)" />
                        </div>
                    </div>
                    <div className="stat-card-value" style={{ color: 'var(--accent-purple)' }}>
                        {fleet ? `${fleet.averages?.avg_touch_latency_ms} ms` : '--'}
                    </div>
                    <div className="stat-card-sub">Capacitive multi-touch polling</div>
                </div>
            </div>

            {/* Interactive Vehicle Configurator Displays Fleet */}
            <div style={{ marginBottom: 16 }}>
                <h3 style={{ fontSize: 15, fontWeight: 600, color: '#fff', marginBottom: 6 }}>
                    Interactive Vehicle-Configurator Display Fleet
                </h3>
                <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Select a display unit to view real-time thermal telemetry, touch digitizer latency, and frame rate metrics.
                </p>
            </div>

            <div className="display-grid">
                {fleet?.displays?.map(disp => {
                    const isSelected = disp.id === selectedId;
                    
                    return (
                        <div 
                            key={disp.id}
                            className={`showroom-display-card status-${disp.status}`}
                            onClick={() => setSelectedId(disp.id)}
                            style={{ 
                                cursor: 'pointer',
                                background: isSelected ? 'var(--bg-elevated)' : 'var(--bg-card)',
                                borderColor: isSelected ? 'var(--accent-blue)' : undefined,
                            }}
                        >
                            <div className="disp-header">
                                <div>
                                    <div className="disp-title" style={{ color: isSelected ? 'var(--accent-blue)' : '#fff' }}>
                                        {disp.name}
                                    </div>
                                    <div className="disp-sub">{disp.vehicle_model}</div>
                                </div>
                                <span className={`badge badge-${disp.status.toLowerCase()}`}>
                                    <span className="badge-dot" />
                                    {disp.status}
                                </span>
                            </div>

                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>
                                <b>Hardware:</b> {disp.model}
                            </div>

                            <div className="disp-metrics-grid">
                                <div className="disp-metric-item">
                                    <span className="disp-metric-label">3D FPS</span>
                                    <span className="disp-metric-val" style={{ color: disp.diagnostics.fps < 30 ? 'var(--accent-red)' : 'var(--text-primary)' }}>
                                        {disp.diagnostics.fps} FPS
                                    </span>
                                </div>
                                <div className="disp-metric-item">
                                    <span className="disp-metric-label">GPU Temp</span>
                                    <span className="disp-metric-val" style={{ color: disp.diagnostics.gpu_temp_c > 80 ? 'var(--accent-red)' : 'var(--text-primary)' }}>
                                        {disp.diagnostics.gpu_temp_c} °C
                                    </span>
                                </div>
                                <div className="disp-metric-item">
                                    <span className="disp-metric-label">Panel Backlight</span>
                                    <span className="disp-metric-val">
                                        {disp.diagnostics.panel_temp_c} °C
                                    </span>
                                </div>
                                <div className="disp-metric-item">
                                    <span className="disp-metric-label">Touch Latency</span>
                                    <span className="disp-metric-val" style={{ color: disp.diagnostics.touch_latency_ms > 40 ? 'var(--accent-yellow)' : 'var(--text-primary)' }}>
                                        {disp.diagnostics.touch_latency_ms} ms
                                    </span>
                                </div>
                            </div>

                            {disp.fault_reasons?.length > 0 && (
                                <div style={{ 
                                    background: 'rgba(239, 68, 68, 0.1)', 
                                    borderLeft: '3px solid var(--accent-red)', 
                                    padding: '6px 8px', 
                                    borderRadius: 4, 
                                    fontSize: 11, 
                                    color: '#fca5a5' 
                                }}>
                                    {disp.fault_reasons[0]}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Selected Display Live Inspector & Fault Simulation */}
            {currentDisplay && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
                    {/* Live Performance History Chart */}
                    <div className="card">
                        <div className="card-header">
                            <div>
                                <div className="card-title">Live Telemetry Diagnostics · {currentDisplay.name}</div>
                                <div className="card-subtitle">Real-time FPS and GPU thermal telemetry curve</div>
                            </div>
                            <span className="card-tag">Live Sensor Buffer</span>
                        </div>

                        <ResponsiveContainer width="100%" height={260}>
                            <AreaChart data={selectedDetail?.history || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorFps" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                    </linearGradient>
                                    <linearGradient id="colorGpu" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="time" tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis tick={{ fill: '#4d5a6b', fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 140]} />
                                <Tooltip 
                                    contentStyle={{ background: '#141920', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                />
                                <Area type="monotone" dataKey="fps" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorFps)" name="3D Viewport FPS" />
                                <Area type="monotone" dataKey="gpu_temp" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorGpu)" name="GPU Core Temp (°C)" />
                                <Area type="monotone" dataKey="touch_latency" stroke="#8b5cf6" strokeWidth={2} fillOpacity={0} name="Touch Latency (ms)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Diagnostic Fault Injection Sandbox */}
                    <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                        <div className="card-header" style={{ paddingBottom: 10 }}>
                            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <Flame size={15} color="var(--accent-yellow)" />
                                Fault Injection Sandbox
                            </div>
                        </div>

                        <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 14 }}>
                            Inject realistic showroom hardware anomalies into <b>{currentDisplay.id}</b> to test real-time alert dispatch and Ollama incident correlation.
                        </p>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                            <button
                                onClick={() => handleInjectFault('gpu_thermal')}
                                disabled={injecting}
                                style={{
                                    background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)',
                                    color: '#f87171', padding: '8px 12px', borderRadius: 6, fontSize: 12,
                                    fontWeight: 600, cursor: 'pointer', textAlign: 'left', display: 'flex', justifyContent: 'space-between'
                                }}
                            >
                                <span>🔥 GPU Thermal Surge (92°C)</span>
                                <span style={{ fontSize: 10, opacity: 0.8 }}>Overheat</span>
                            </button>

                            <button
                                onClick={() => handleInjectFault('touch_lag')}
                                disabled={injecting}
                                style={{
                                    background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)',
                                    color: '#fbbf24', padding: '8px 12px', borderRadius: 6, fontSize: 12,
                                    fontWeight: 600, cursor: 'pointer', textAlign: 'left', display: 'flex', justifyContent: 'space-between'
                                }}
                            >
                                <span>👆 Touch Digitizer Lag (84ms)</span>
                                <span style={{ fontSize: 10, opacity: 0.8 }}>Latency</span>
                            </button>

                            <button
                                onClick={() => handleInjectFault('chassis_tamper')}
                                disabled={injecting}
                                style={{
                                    background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.5)',
                                    color: '#ef4444', padding: '8px 12px', borderRadius: 6, fontSize: 12,
                                    fontWeight: 700, cursor: 'pointer', textAlign: 'left', display: 'flex', justifyContent: 'space-between'
                                }}
                            >
                                <span>⚠️ Chassis Tamper Alert</span>
                                <span style={{ fontSize: 10, opacity: 0.8 }}>Physical</span>
                            </button>

                            <button
                                onClick={() => handleInjectFault('frame_drop')}
                                disabled={injecting}
                                style={{
                                    background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)',
                                    color: '#c4b5fd', padding: '8px 12px', borderRadius: 6, fontSize: 12,
                                    fontWeight: 600, cursor: 'pointer', textAlign: 'left', display: 'flex', justifyContent: 'space-between'
                                }}
                            >
                                <span>📉 3D Configurator Frame Crash</span>
                                <span style={{ fontSize: 10, opacity: 0.8 }}>12 FPS</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SystemHealth;
