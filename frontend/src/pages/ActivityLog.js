import React, { useState, useEffect, useCallback } from 'react';
import { Search, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { getActivity } from '../api/client';

const PAGE_SIZE = 20;

const formatTimestamp = (ts) => {
    if (!ts) return '—';
    const d = new Date(ts);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
         + ' '
         + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

const getScoreClass = (score) => {
    if (score == null) return '';
    if (score > -0.05) return 'score-safe';
    if (score > -0.15) return 'score-medium';
    return 'score-high';
};

const ActivityLog = () => {
    const [data,    setData]    = useState([]);
    const [loading, setLoading] = useState(true);
    const [search,  setSearch]  = useState('');
    const [filter,  setFilter]  = useState('ALL');
    const [page,    setPage]    = useState(1);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await getActivity(200);
            setData(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);
    useEffect(() => { setPage(1); }, [search, filter]);

    const filtered = data.filter(q => {
        const matchesFilter = filter === 'ALL' || q.status === filter;
        const matchesSearch = !search || q.query_text.toLowerCase().includes(search.toLowerCase())
                                      || (q.db_user || '').toLowerCase().includes(search.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const totalPages   = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    const paginated    = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    const counts = {
        ALL:      data.length,
        ALLOWED:  data.filter(q => q.status === 'ALLOWED').length,
        FLAGGED:  data.filter(q => q.status === 'FLAGGED').length,
        BLOCKED:  data.filter(q => q.status === 'BLOCKED').length,
    };

    return (
        <div className="page fade-in">
            <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div>
                    <h1 className="page-title">Activity Log</h1>
                    <p className="page-subtitle">{filtered.length} queries{filter !== 'ALL' ? ` matching "${filter}"` : ''}{search ? ` · "${search}"` : ''}</p>
                </div>
                <button
                    onClick={fetchData}
                    style={{
                        display: 'flex', alignItems: 'center', gap: 6,
                        background: 'var(--bg-card)', border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)',
                        fontSize: 12, fontWeight: 500, padding: '8px 14px',
                        cursor: 'pointer', fontFamily: 'inherit', outline: 'none',
                    }}
                >
                    <RefreshCw size={13} />
                    Refresh
                </button>
            </div>

            {/* Toolbar */}
            <div className="toolbar">
                <div className="search-input-wrap">
                    <span className="search-input-icon"><Search size={14} /></span>
                    <input
                        id="activity-search"
                        className="search-input"
                        type="text"
                        placeholder="Search queries or users…"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </div>
                {['ALL', 'ALLOWED', 'FLAGGED', 'BLOCKED'].map(f => (
                    <button
                        key={f}
                        className={`filter-btn ${filter === f ? 'active' : ''}`}
                        onClick={() => setFilter(f)}
                    >
                        {f} ({counts[f]})
                    </button>
                ))}
            </div>

            {/* Table */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div className="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th style={{ width: 48 }}>#</th>
                                <th>Query</th>
                                <th>User</th>
                                <th>Type</th>
                                <th>Score</th>
                                <th>Latency</th>
                                <th>Status</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={8} style={{ textAlign: 'center', padding: '40px' }}>
                                        <div className="loading-pulse" style={{ justifyContent: 'center' }}>
                                            <span /><span /><span />
                                        </div>
                                    </td>
                                </tr>
                            ) : paginated.length === 0 ? (
                                <tr>
                                    <td colSpan={8}>
                                        <div className="empty-state">
                                            <div className="empty-state-title">No results</div>
                                            <div className="empty-state-sub">Try adjusting your search or filter</div>
                                        </div>
                                    </td>
                                </tr>
                            ) : paginated.map(q => (
                                <tr key={q.id}>
                                    <td style={{ color: 'var(--text-muted)', fontSize: 11, fontFamily: 'var(--font-mono)' }}>{q.id}</td>
                                    <td className="td-mono">{q.query_text}</td>
                                    <td style={{ fontSize: 13 }}>{q.db_user || '—'}</td>
                                    <td>
                                        <span style={{
                                            fontFamily: 'var(--font-mono)',
                                            fontSize: 11, fontWeight: 600,
                                            color: 'var(--text-secondary)',
                                            background: 'var(--bg-elevated)',
                                            padding: '2px 7px',
                                            borderRadius: 4,
                                        }}>
                                            {q.query_type || '—'}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`score-chip ${getScoreClass(q.anomaly_score)}`}>
                                            {q.anomaly_score != null ? q.anomaly_score.toFixed(4) : '—'}
                                        </span>
                                    </td>
                                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                                        {q.execution_time != null ? `${q.execution_time} ms` : '—'}
                                    </td>
                                    <td>
                                        <span className={`badge badge-${(q.status || '').toLowerCase()}`}>
                                            <span className="badge-dot" />
                                            {q.status || '—'}
                                        </span>
                                    </td>
                                    <td style={{ fontSize: 12, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                                        {formatTimestamp(q.timestamp)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {!loading && filtered.length > PAGE_SIZE && (
                    <div style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        padding: '12px 18px',
                        borderTop: '1px solid var(--border)',
                        fontSize: 12,
                        color: 'var(--text-muted)',
                    }}>
                        <span>Page {page} of {totalPages} · {filtered.length} entries</span>
                        <div style={{ display: 'flex', gap: 6 }}>
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="filter-btn"
                                style={{ padding: '6px 10px' }}
                            >
                                <ChevronLeft size={14} />
                            </button>
                            <button
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                                className="filter-btn"
                                style={{ padding: '6px 10px' }}
                            >
                                <ChevronRight size={14} />
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActivityLog;
