// ============================================
// Verification Dashboard React Component
// ============================================

import React, { useState } from 'react';

const VerificationDashboard = ({ result = null, loading = false }) => {
    const [activeTab, setActiveTab] = useState('evidence');

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '3rem' }}>
                <div className="loading-spinner"></div>
                <p style={{ color: '#6b7280', fontSize: '1.125rem', marginTop: '1.5rem' }}>
                    Verifying your claim...
                </p>
            </div>
        );
    }

    if (!result) {
        return <div></div>;
    }

    const { verdict, metrics, evidence, relatedArticles } = result;

    const getVerdictColor = () => {
        switch (verdict.value) {
            case 'true':
                return '#10b981';
            case 'false':
                return '#ef4444';
            case 'partial':
                return '#f59e0b';
            case 'unclear':
                return '#8b5cf6';
            default:
                return '#9ca3af';
        }
    };

    return (
        <div className="results-container">
            {/* Verdict Banner */}
            <div className={`verdict-banner ${verdict.value}`}>
                <div className="verdict-header">
                    <div className="verdict-icon">
                        {verdict.value === 'true' && '✓'}
                        {verdict.value === 'false' && '✗'}
                        {verdict.value === 'partial' && '⚠'}
                        {verdict.value === 'unclear' && '?'}
                    </div>
                    <div className="verdict-content">
                        <div className="verdict-label">{verdict.label}</div>
                        <h2>{verdict.title}</h2>
                    </div>
                </div>
                <div className="verdict-summary">{verdict.summary}</div>
            </div>

            {/* Trust Metrics Grid */}
            <div className="trust-metrics">
                <div className="metric-card">
                    <div className="metric-label">Source Quality</div>
                    <div className="metric-value text-gradient">{metrics.sourceQuality}%</div>
                    <div className="metric-subtitle">Credibility Score</div>
                </div>
                <div className="metric-card">
                    <div className="metric-label">Evidence Found</div>
                    <div className="metric-value text-gradient">{metrics.evidenceCount}</div>
                    <div className="metric-subtitle">Supporting Sources</div>
                </div>
                <div className="metric-card">
                    <div className="metric-label">Verdict Confidence</div>
                    <div className="metric-value text-gradient">{metrics.confidence}%</div>
                    <div className="metric-subtitle">Analysis Confidence</div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div
                style={{
                    display: 'flex',
                    gap: '1rem',
                    marginBottom: '2rem',
                    borderBottom: '1px solid #e5e7eb',
                    paddingBottom: '1rem',
                }}
            >
                <button
                    onClick={() => setActiveTab('evidence')}
                    style={{
                        padding: '0.75rem 1.5rem',
                        background: activeTab === 'evidence' ? '#1e88e5' : 'transparent',
                        color: activeTab === 'evidence' ? 'white' : '#6b7280',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        fontSize: '0.95rem',
                        fontWeight: '600',
                    }}
                >
                    Evidence ({evidence.supporting.length})
                </button>
                <button
                    onClick={() => setActiveTab('related')}
                    style={{
                        padding: '0.75rem 1.5rem',
                        background: activeTab === 'related' ? '#1e88e5' : 'transparent',
                        color: activeTab === 'related' ? 'white' : '#6b7280',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        fontSize: '0.95rem',
                        fontWeight: '600',
                    }}
                >
                    Related Articles
                </button>
            </div>

            {/* Evidence Tab */}
            {activeTab === 'evidence' && (
                <div className="evidence-section">
                    <h3 className="section-heading">
                        Supporting Evidence
                        <span style={{ fontSize: '0.9em', color: '#9ca3af' }}>
                            ({evidence.supporting.length})
                        </span>
                    </h3>
                    <div className="evidence-grid">
                        {evidence.supporting.map((item, index) => (
                            <EvidenceCard key={index} evidence={item} />
                        ))}
                    </div>

                    {evidence.contradicting.length > 0 && (
                        <>
                            <h3 className="section-heading">
                                Contradicting Evidence
                                <span style={{ fontSize: '0.9em', color: '#9ca3af' }}>
                                    ({evidence.contradicting.length})
                                </span>
                            </h3>
                            <div className="evidence-grid">
                                {evidence.contradicting.map((item, index) => (
                                    <EvidenceCard key={index} evidence={item} />
                                ))}
                            </div>
                        </>
                    )}
                </div>
            )}

            {/* Related Articles Tab */}
            {activeTab === 'related' && (
                <div className="evidence-section">
                    <h3 className="section-heading">
                        Related Articles
                        <span style={{ fontSize: '0.9em', color: '#9ca3af' }}>
                            ({relatedArticles.length})
                        </span>
                    </h3>
                    <div className="evidence-grid">
                        {relatedArticles.map((article, index) => (
                            <div key={index} className="evidence-card" style={{ cursor: 'pointer' }}>
                                <div className="evidence-header">
                                    <div
                                        className="source-icon"
                                        style={{ background: 'linear-gradient(135deg, #8b5cf6, #06b6d4)' }}
                                    >
                                        {article.source.substring(0, 2).toUpperCase()}
                                    </div>
                                    <div className="evidence-info">
                                        <div className="source-name">{article.title}</div>
                                        <div className="source-date">
                                            {article.source} • {formatDate(article.date)}
                                        </div>
                                    </div>
                                </div>
                                <div className="evidence-text">{article.snippet}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

// ============================================
// Evidence Card Component
// ============================================

const EvidenceCard = ({ evidence }) => {
    const stanceStyles = {
        supports: { background: 'rgba(16, 185, 129, 0.1)', color: '#047857' },
        contradicts: { background: 'rgba(239, 68, 68, 0.1)', color: '#dc2626' },
        neutral: { background: 'rgba(107, 114, 128, 0.1)', color: '#374151' },
    };

    const stanceStyle = stanceStyles[evidence.stance.toLowerCase()] || stanceStyles.neutral;

    return (
        <div className="evidence-card">
            <div className="evidence-header">
                <div className="source-icon">
                    {evidence.source.substring(0, 2).toUpperCase()}
                </div>
                <div className="evidence-info">
                    <div className="source-name">{evidence.source}</div>
                    <div className="source-date">{formatDate(evidence.date)}</div>
                </div>
                <div
                    className="stance-badge"
                    style={{
                        background: stanceStyle.background,
                        color: stanceStyle.color,
                        border: `1px solid ${stanceStyle.color}20`,
                    }}
                >
                    {evidence.stance.charAt(0).toUpperCase() + evidence.stance.slice(1).toLowerCase()}
                </div>
            </div>
            <div className="evidence-text">{evidence.excerpt}</div>
            <div className="score-bar">
                <div className="score-fill" style={{ width: `${evidence.relevanceScore}%` }}></div>
            </div>
        </div>
    );
};

// ============================================
// Utility Functions
// ============================================

const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days < 1) return 'Today';
    if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (days < 30) return `${Math.floor(days / 7)} week${Math.floor(days / 7) > 1 ? 's' : ''} ago`;
    if (days < 365)
        return `${Math.floor(days / 30)} month${Math.floor(days / 30) > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
};

export default VerificationDashboard;
