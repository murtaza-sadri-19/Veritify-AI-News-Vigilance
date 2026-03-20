// ============================================
// Verification Logic & Dashboard Rendering
// ============================================

const API_BASE_URL = '/api';

// DOM Elements
const searchInput = document.querySelector('.search-input');
const verifyBtn = document.querySelector('.btn-verify');
const heroSection = document.querySelector('.hero');
const container = document.querySelector('.results-container');

// State
let isVerifying = false;
let currentClaim = '';

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    if (verifyBtn) {
        verifyBtn.addEventListener('click', verifyFact);
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                verifyFact();
            }
        });
    }
});

// ============================================
// VERIFY FACT - Main API Call
// ============================================

async function verifyFact() {
    const claim = searchInput ? searchInput.value.trim() : '';

    if (!claim) {
        showAlert('Please enter a claim to verify', 'error');
        return;
    }

    if (isVerifying) return;

    currentClaim = claim;
    isVerifying = true;
    updateButtonState(true);
    showLoadingView();

    try {
        // Simulate API call with timeout (3-8 seconds)
        const response = await new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    status: 'success',
                    data: generateMockResult(claim),
                });
            }, 3000 + Math.random() * 5000);
        });

        if (response.status === 'success') {
            displayResults(response.data, claim);
        } else {
            showAlert('Verification failed. Please try again.', 'error');
            hideLoadingView();
        }
    } catch (error) {
        console.error('Verification error:', error);
        showAlert('An error occurred during verification', 'error');
        hideLoadingView();
    } finally {
        isVerifying = false;
        updateButtonState(false);
    }
}

// ============================================
// DISPLAY RESULTS - Dashboard Rendering
// ============================================

function displayResults(result, originalClaim) {
    hideLoadingView();

    // Clear previous results
    const previousResults = document.querySelector('.results-view');
    if (previousResults) {
        previousResults.remove();
    }

    // Create results view
    const resultsView = document.createElement('div');
    resultsView.className = 'results-view fade-in';
    resultsView.innerHTML = `
        <div class="results-container">
            <!-- Verdict Banner -->
            <div class="verdict-banner ${result.verdict.value}">
                <div class="verdict-header">
                    <div class="verdict-icon">${getVerdictIcon(result.verdict.value)}</div>
                    <div class="verdict-content">
                        <div class="verdict-label">${result.verdict.label}</div>
                        <h2>${result.verdict.title}</h2>
                    </div>
                </div>
                <div class="verdict-summary">${result.verdict.summary}</div>
            </div>

            <!-- Trust Metrics -->
            <div class="trust-metrics">
                <div class="metric-card">
                    <div class="metric-label">Source Quality</div>
                    <div class="metric-value">${result.metrics.sourceQuality}%</div>
                    <div class="metric-subtitle">Credibility Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Evidence Found</div>
                    <div class="metric-value">${result.metrics.evidenceCount}</div>
                    <div class="metric-subtitle">Supporting Sources</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Verdict Confidence</div>
                    <div class="metric-value">${result.metrics.confidence}%</div>
                    <div class="metric-subtitle">Analysis Confidence</div>
                </div>
            </div>

            <!-- Supporting Evidence -->
            ${renderEvidenceSection(result.evidence.supporting, 'Supporting Evidence')}

            <!-- Contradicting Evidence -->
            ${renderEvidenceSection(result.evidence.contradicting, 'Contradicting Evidence')}

            <!-- Related Articles -->
            ${renderRelatedArticles(result.relatedArticles)}

            <!-- New Search Button -->
            <div style="text-align: center; margin: 3rem 0;">
                <button onclick="resetSearch()" class="btn-verify">
                    <span>Search Again</span>
                </button>
            </div>
        </div>
    `;

    // Insert results view
    if (heroSection && container) {
        container.innerHTML = '';
        container.appendChild(resultsView);
    }

    // Scroll to results
    setTimeout(() => {
        resultsView.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// ============================================
// EVIDENCE SECTION RENDERER
// ============================================

function renderEvidenceSection(evidenceList, title) {
    if (!evidenceList || evidenceList.length === 0) {
        return '';
    }

    const evidenceHTML = evidenceList
        .map(
            (evidence) => `
        <div class="evidence-card">
            <div class="evidence-header">
                <div class="source-icon">${getSourceInitials(evidence.source)}</div>
                <div class="evidence-info">
                    <div class="source-name">${evidence.source}</div>
                    <div class="source-date">${formatDate(evidence.date)}</div>
                </div>
                <div class="stance-badge ${evidence.stance.toLowerCase()}">
                    ${capitalizeFirst(evidence.stance)}
                </div>
            </div>
            <div class="evidence-text">${evidence.excerpt}</div>
            <div class="score-bar">
                <div class="score-fill" style="width: ${evidence.relevanceScore}%"></div>
            </div>
        </div>
    `
        )
        .join('');

    return `
        <div class="evidence-section">
            <h3 class="section-heading">
                ${title}
                <span style="font-size: 0.9em; color: #9ca3af;">(${evidenceList.length})</span>
            </h3>
            <div class="evidence-grid">
                ${evidenceHTML}
            </div>
        </div>
    `;
}

// ============================================
// RELATED ARTICLES SECTION
// ============================================

function renderRelatedArticles(articles) {
    if (!articles || articles.length === 0) {
        return '';
    }

    const articlesHTML = articles
        .slice(0, 4)
        .map(
            (article) => `
        <div class="evidence-card" style="cursor: pointer;">
            <div class="evidence-header">
                <div class="source-icon" style="background: linear-gradient(135deg, #8b5cf6, #06b6d4);">
                    ${getSourceInitials(article.source)}
                </div>
                <div class="evidence-info">
                    <div class="source-name">${article.title}</div>
                    <div class="source-date">${article.source} • ${formatDate(article.date)}</div>
                </div>
            </div>
            <div class="evidence-text">${article.snippet}</div>
        </div>
    `
        )
        .join('');

    return `
        <div class="evidence-section">
            <h3 class="section-heading">
                Related Articles
                <span style="font-size: 0.9em; color: #9ca3af;">(${articles.length})</span>
            </h3>
            <div class="evidence-grid">
                ${articlesHTML}
            </div>
        </div>
    `;
}

// ============================================
// LOADING VIEW
// ============================================

function showLoadingView() {
    const loadingView = document.createElement('div');
    loadingView.className = 'loading-view fade-in';
    loadingView.innerHTML = `
        <div style="text-align: center; padding: 3rem;">
            <div class="loading-spinner"></div>
            <p style="color: #6b7280; font-size: 1.125rem; margin-top: 1.5rem;">
                Verifying your claim...
            </p>
            <p style="color: #9ca3af; font-size: 0.875rem; margin-top: 0.5rem;">
                Scanning news sources and fact-checking databases
            </p>
        </div>
    `;

    if (container) {
        container.innerHTML = '';
        container.appendChild(loadingView);
    }
}

function hideLoadingView() {
    const loadingView = document.querySelector('.loading-view');
    if (loadingView) {
        loadingView.style.opacity = '0';
        setTimeout(() => loadingView.remove(), 300);
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function resetSearch() {
    if (searchInput) searchInput.value = '';
    if (container) container.innerHTML = '';
    if (heroSection) {
        setTimeout(() => {
            heroSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }
}

function getVerdictIcon(verdict) {
    const icons = {
        true: '✓',
        false: '✗',
        partial: '⚠',
        unclear: '?',
        nosources: '—',
    };
    return icons[verdict] || '?';
}

function getSourceInitials(source) {
    return source
        .split(' ')
        .map((word) => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
}

function formatDate(dateString) {
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
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function showAlert(message, type) {
    // Could be enhanced with a toast/alert UI
    console.log(`[${type.toUpperCase()}] ${message}`);
}

function updateButtonState(loading) {
    if (verifyBtn) {
        if (loading) {
            verifyBtn.disabled = true;
            verifyBtn.textContent = 'Verifying...';
            verifyBtn.style.opacity = '0.7';
        } else {
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<span>Verify Claim</span>';
            verifyBtn.style.opacity = '1';
        }
    }
}

// ============================================
// MOCK DATA GENERATOR
// ============================================

function generateMockResult(claim) {
    const verdicts = [
        {
            value: 'true',
            label: 'Mostly True',
            title: 'Claim is Supported by Evidence',
            summary: `Based on our analysis of ${Math.floor(Math.random() * 30) + 5} verified sources, this claim appears to be accurate and well-supported by recent news reports and credible sources.`,
        },
        {
            value: 'false',
            label: 'False',
            title: 'Claim is Not Supported',
            summary: `Our analysis found contradicting information from multiple reliable sources. The claim appears to be inaccurate or misleading.`,
        },
        {
            value: 'partial',
            label: 'Partially True',
            title: 'Claim is Partially Accurate',
            summary: `While some aspects of this claim are supported by evidence, other parts are disputed or lack sufficient verification.`,
        },
        {
            value: 'unclear',
            label: 'Unclear',
            title: 'Insufficient Evidence',
            summary: `There is limited available evidence on this specific claim. Further research or clarification may be needed for conclusive verification.`,
        },
    ];

    const selectedVerdict = verdicts[Math.floor(Math.random() * verdicts.length)];

    const supportingSources = [
        {
            source: 'Reuters',
            date: '2024-01-15',
            excerpt:
                'Recent reports confirm the claim with substantial evidence from field researchers and official records.',
            stance: 'supports',
            relevanceScore: 95,
        },
        {
            source: 'Associated Press',
            date: '2024-01-14',
            excerpt:
                'Multiple independent sources corroborate the key facts stated in the claim. Verification complete.',
            stance: 'supports',
            relevanceScore: 88,
        },
        {
            source: 'BBC',
            date: '2024-01-13',
            excerpt:
                'Investigation into the matter supports the accuracy of these statements based on expert analysis.',
            stance: 'supports',
            relevanceScore: 82,
        },
    ];

    const contradictingSources = [
        {
            source: 'Fact Check Daily',
            date: '2024-01-16',
            excerpt:
                'While parts of the claim are accurate, the overall conclusion contradicts recent studies and data analysis.',
            stance: 'contradicts',
            relevanceScore: 78,
        },
    ];

    const relatedArticles = [
        {
            source: 'The Guardian',
            title: 'Deep Dive: Understanding the Context Behind These Claims',
            date: '2024-01-12',
            snippet: 'This comprehensive analysis explores the background and related factors that may influence the accuracy...',
        },
        {
            source: 'NPR',
            title: 'Experts Weigh In: What the Data Really Shows',
            date: '2024-01-11',
            snippet: 'Leading researchers discuss the scientific evidence and methodologies used to verify such claims...',
        },
        {
            source: 'The New York Times',
            title: 'Fact-Checking 101: How We Verify Information',
            date: '2024-01-10',
            snippet: 'Learn about the rigorous process fact-checkers use to ensure accuracy and prevent misinformation...',
        },
    ];

    return {
        verdict: selectedVerdict,
        metrics: {
            sourceQuality: Math.floor(Math.random() * 30) + 70, // 70-100%
            evidenceCount: Math.floor(Math.random() * 15) + 5, // 5-20 sources
            confidence: Math.floor(Math.random() * 20) + 80, // 80-100%
        },
        evidence: {
            supporting: supportingSources.slice(0, Math.floor(Math.random() * 2) + 2),
            contradicting: contradictingSources,
        },
        relatedArticles: relatedArticles,
    };
}
