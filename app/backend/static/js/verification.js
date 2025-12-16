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
        let verdictClass = 'verdict-insufficient';
        let verdictIcon = 'fa-question-circle';
        let verdictLabel = 'INSUFFICIENT DATA';
        let verdictColor = '#9ca3af';

        // Map verdict to UI representation
        if (result.verdict) {
            switch (result.verdict.toUpperCase()) {
                case 'TRUE':
                    verdictClass = 'verdict-true';
                    verdictIcon = 'fa-check-circle';
                    verdictLabel = 'TRUE';
                    verdictColor = '#10b981';
                    break;
                case 'FALSE':
                    verdictClass = 'verdict-false';
                    verdictIcon = 'fa-times-circle';
                    verdictLabel = 'FALSE';
                    verdictColor = '#ef4444';
                    break;
                case 'PARTIALLY_TRUE':
                case 'PARTIALLY FALSE':
                    verdictClass = 'verdict-partial';
                    verdictIcon = 'fa-exclamation-circle';
                    verdictLabel = 'PARTIALLY FALSE';
                    verdictColor = '#f59e0b';
                    break;
                case 'OPINION':
                    verdictClass = 'verdict-opinion';
                    verdictIcon = 'fa-comment-dots';
                    verdictLabel = 'OPINION';
                    verdictColor = '#8b5cf6';
                    break;
                case 'INSUFFICIENT':
                    verdictClass = 'verdict-insufficient';
                    verdictIcon = 'fa-question-circle';
                    verdictLabel = 'INSUFFICIENT DATA';
                    verdictColor = '#9ca3af';
                    break;
            }
        }

        const confidencePercent = result.confidence ? Math.round(result.confidence * 100) : 0;

        let html = `
            <div class="result-card">
                <div class="verdict-container ${verdictClass}">
                    <div class="verdict-badge">
                        <i class="fas ${verdictIcon}"></i>
                        <div>
                            <div class="verdict-label">${verdictLabel}</div>
                            <div class="confidence-score">
                                ${confidencePercent}% confidence
                            </div>
                        </div>
                    </div>
                </div>
                <div class="result-details">
                    <div class="claim-text">
                        <i class="fas fa-quote-left"></i>
                        ${escapeHtml(originalClaim)}
                    </div>
        `;

        // Add explanation if available
        if (result.explanation) {
            html += `
                <div class="explanation">
                    <h4>Why ${verdictLabel.toLowerCase()}?</h4>
                    <p>${escapeHtml(result.explanation)}</p>
                </div>
            `;
        }

        // Add evidence table
        if (result.evidence && result.evidence.length > 0) {
            html += `
                <div class="evidence-section">
                    <h3><i class="fas fa-link"></i> Supporting Evidence</h3>
                    <table class="evidence-table">
                        <thead>
                            <tr>
                                <th>Source</th>
                                <th>Entailment</th>
                                <th>Details</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            result.evidence.forEach((evidence) => {
                // Map backend field names: entailment_label, entailment_confidence, published_date, snippet
                const rawEntailment = evidence.entailment_label || evidence.entailment || 'NEUTRAL';
                const entailmentConfidence = evidence.entailment_confidence;
                const entailmentClass = `entailment-${String(rawEntailment).toLowerCase()}`;
                const entailmentLabel = rawEntailment;
                const date = evidence.published_date ? formatDate(evidence.published_date) : (evidence.date ? formatDate(evidence.date) : '');
                const snippet = evidence.snippet || evidence.excerpt || '';

                html += `
                    <tr class="${entailmentClass}">
                        <td class="source-cell">
                            <strong>${escapeHtml(evidence.source || 'Unknown')}</strong>
                            <div class="source-meta">${escapeHtml(evidence.title || '')}</div>
                        </td>
                        <td class="entailment-cell">
                            <span class="entailment-badge ${entailmentClass}">
                                ${entailmentLabel}${typeof entailmentConfidence === 'number' ? ` (${Math.round(entailmentConfidence * 100)}%)` : ''}
                            </span>
                        </td>
                        <td class="details-cell">
                            ${snippet ? `<p>${escapeHtml(snippet)}</p>` : ''}
                            ${evidence.location ? `<div><i class="fas fa-map-marker-alt"></i> ${escapeHtml(evidence.location)}</div>` : ''}
                            ${evidence.genre ? `<div><i class="fas fa-tag"></i> ${escapeHtml(evidence.genre)}</div>` : ''}
                            ${date ? `<div><i class="fas fa-calendar"></i> ${date}</div>` : ''}
                        </td>
                        <td class="action-cell">
                            ${evidence.url ? `<a href="${escapeHtml(evidence.url)}" class="btn-small" target="_blank" rel="noopener"><i class="fas fa-external-link-alt"></i> Read</a>` : '-'}
                        </td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
        } else if (result.verdict && result.verdict.toUpperCase() === 'OPINION') {
            html += `
                <div class="opinion-notice">
                    <i class="fas fa-comment-dots"></i>
                    <p>This appears to be a matter of opinion or prediction rather than a factual claim. The system cannot verify opinions.</p>
                </div>
            `;
        } else {
            html += `
                <div class="no-sources">
                    <i class="fas fa-search"></i> 
                    <p>No specific evidence found for this claim. This could mean the claim is very new, highly specific, or not widely reported.</p>
                </div>
            `;
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