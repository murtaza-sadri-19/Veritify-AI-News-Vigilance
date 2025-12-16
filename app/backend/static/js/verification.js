// Verification functionality for TruthTrack - Enhanced UX

document.addEventListener('DOMContentLoaded', function() {
    const verifyButton = document.getElementById('verify-button');
    const claimInput = document.getElementById('claim-input');
    const resultContainer = document.getElementById('result-container');
    const resultsSection = document.getElementById('results-section');

    if (verifyButton) {
        verifyButton.addEventListener('click', verifyFact);

        // Allow Ctrl+Enter or Cmd+Enter to submit
        claimInput.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                verifyFact();
            }
        });
    }

    function verifyFact() {
        const claim = claimInput.value.trim();

        // Validation
        if (!claim) {
            showNotification('Please enter a claim to verify', 'warning');
            claimInput.focus();
            return;
        }

        if (claim.length < 10) {
            showNotification('Please enter a more detailed claim (at least 10 characters)', 'warning');
            claimInput.focus();
            return;
        }

        if (claim.length > 500) {
            showNotification('Claim is too long (max 500 characters)', 'warning');
            return;
        }

        // Disable button and show loading
        verifyButton.disabled = true;
        const originalText = verifyButton.innerHTML;
        verifyButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';

        resultContainer.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>Analyzing claim across multiple sources...</p>
                <p style="font-size: 0.875rem; color: #9ca3af; margin-top: 1rem;">This may take a moment</p>
            </div>
        `;
        resultsSection.style.display = 'block';
        smoothScrollTo(resultsSection);

        // API call
        fetch('/api/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ claim: claim }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || `HTTP ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                displayResults(data.result, claim);
                showNotification('✓ Fact-check completed!', 'success');
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Verification error:', error);
            resultContainer.innerHTML = `
                <div class="error">
                    <h3><i class="fas fa-exclamation-circle"></i> Error Occurred</h3>
                    <p>${escapeHtml(error.message)}</p>
                    <button onclick="location.reload()" class="btn btn-primary" style="margin-top: 1rem;">
                        <i class="fas fa-redo"></i> Try Again
                    </button>
                </div>
            `;
            showNotification('Error during fact-check', 'error');
        })
        .finally(() => {
            verifyButton.disabled = false;
            verifyButton.innerHTML = originalText;
        });
    }

    function displayResults(result, originalClaim) {
        let scoreClass = 'medium-score';
        let scoreLabel = 'RELEVANCE';

        if (result.score === null) {
            scoreClass = 'no-score';
            scoreLabel = 'NO DATA';
        } else if (result.score >= 70) {
            scoreClass = 'high-score';
            scoreLabel = 'HIGH';
        } else if (result.score <= 30) {
            scoreClass = 'low-score';
            scoreLabel = 'LOW';
        }

        let html = `
            <div class="result-card">
                <div class="score-container ${scoreClass}">
                    <div class="score">${result.score !== null ? result.score : '?'}</div>
                    <div class="score-label">${scoreLabel}</div>
                </div>
                <div class="result-details">
                    <div class="claim-text">
                        <i class="fas fa-quote-left"></i>
                        ${escapeHtml(originalClaim)}
                    </div>
                    <div class="result-message">
                        <i class="fas fa-info-circle"></i>
                        ${escapeHtml(result.message)}
                    </div>
        `;

        // Add sources
        if (result.sources && result.sources.length > 0) {
            html += `<h3><i class="fas fa-link"></i> Related Sources (${result.sources.length})</h3><ul>`;

            result.sources.forEach((source, index) => {
                const date = source.date ? formatDate(source.date) : '';
                const relevance = source.relevance ? Math.round(source.relevance * 100) : 0;
                const typeIcon = source.type === 'fact-check' ? 'fas fa-badge-check' : 'fas fa-newspaper';

                html += `
                    <li>
                        <div class="source-header">
                            <strong>
                                <i class="${typeIcon}"></i>
                                ${escapeHtml(source.name)}
                            </strong>
                            ${relevance > 0 ? `<span class="relevance-badge">${relevance}% Match</span>` : ''}
                        </div>
                        ${source.source ? `<div class="source-name"><i class="fas fa-tag"></i> ${escapeHtml(source.source)}</div>` : ''}
                        ${date ? `<div class="source-date"><i class="fas fa-calendar"></i> ${date}</div>` : ''}
                        ${source.location ? `<div class="source-name"><i class="fas fa-map-marker-alt"></i> ${escapeHtml(source.location)}</div>` : ''}
                        ${source.genre ? `<div class="source-name"><i class="fas fa-film"></i> ${escapeHtml(source.genre)}</div>` : ''}
                        ${source.url ? `<a href="${escapeHtml(source.url)}" class="source-link" target="_blank" rel="noopener"><i class="fas fa-external-link-alt"></i> Read Full Article</a>` : ''}
                    </li>
                `;
            });

            html += `</ul>`;

            if (result.total_articles_found && result.total_articles_found > result.sources.length) {
                html += `<div class="sources-summary"><i class="fas fa-chart-bar"></i> Showing ${result.sources.length} of ${result.total_articles_found} total articles found</div>`;
            }
        } else {
            html += `<div class="no-sources"><i class="fas fa-search"></i> No specific news articles found for this claim. This could mean the claim is very new, highly specific, or not widely reported.</div>`;
        }

        // Debug info (development only)
        if (result.debug && window.location.hostname === 'localhost') {
            html += `
                <details class="debug-info">
                    <summary><i class="fas fa-bug"></i> Debug Information (Development)</summary>
                    <pre>${escapeHtml(JSON.stringify(result.debug, null, 2))}</pre>
                </details>
            `;
        }

        html += `</div></div>`;

        resultContainer.innerHTML = html;

        // Add smooth animation
        setTimeout(() => {
            smoothScrollTo(resultsSection);
        }, 100);
    }

    // Ensure helper functions are available
    window.escapeHtml = escapeHtml;
    window.formatDate = formatDate;
    window.smoothScrollTo = smoothScrollTo;
});