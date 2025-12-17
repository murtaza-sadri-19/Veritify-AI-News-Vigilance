// Verification functionality for TruthTrack

document.addEventListener('DOMContentLoaded', function () {
    const verifyButton = document.getElementById('verify-button');
    const claimInput = document.getElementById('claim-input');
    const resultContainer = document.getElementById('result-container');
    const resultsSection = document.getElementById('results-section');

    if (verifyButton) {
        verifyButton.addEventListener('click', verifyFact);

        // Allow Enter key to trigger verification
        claimInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                verifyFact();
            }
        });
    }

    function verifyFact() {
        // Validate input
        const claim = claimInput.value.trim();
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

        // Disable button and show loading state
        verifyButton.disabled = true;
        verifyButton.classList.add('loading');
        const originalHTML = verifyButton.innerHTML;
        verifyButton.innerHTML = `
            <svg class="verify-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"></circle>
            </svg>
            Verifying...
        `;

        resultContainer.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>Checking facts... This may take a moment.</p>
            </div>
        `;
        resultsSection.style.display = 'block';

        // Smooth scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Call the API
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
                    showNotification('Fact-check completed!', 'success');
                } else {
                    throw new Error(data.error || 'Unknown error occurred');
                }
            })
            .catch(error => {
                console.error('Verification error:', error);
                resultContainer.innerHTML = `
                <div class="error">
                    <h3>Error occurred</h3>
                    <p>${error.message}</p>
                    <button onclick="location.reload()" class="btn primary">Try Again</button>
                </div>
            `;
                showNotification('Error during fact-check', 'error');
            })
            .finally(() => {
                // Re-enable button
                verifyButton.disabled = false;
                verifyButton.classList.remove('loading');
                verifyButton.innerHTML = `
                <svg class="verify-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                Verify
            `;
            });
    }

    function displayResults(result, originalClaim) {
        // Determine score class and label
        let scoreClass = 'medium-score';
        let scoreLabel = 'Relevance Score';

        if (result.score === null) {
            scoreClass = 'no-score';
            scoreLabel = 'No Score';
        } else if (result.score >= 70) {
            scoreClass = 'high-score';
        } else if (result.score <= 30) {
            scoreClass = 'low-score';
        }

        // Create the result HTML
        let html = `
            <div class="result-card">
                <div class="score-container ${scoreClass}">
                    <div class="score">${result.score !== null ? result.score : '?'}</div>
                    <div class="score-label">${scoreLabel}</div>
                </div>
                <div class="result-details">
                    <div class="claim-text">"${escapeHtml(originalClaim)}"</div>
                    <div class="result-message">${escapeHtml(result.message)}</div>
        `;

        // Add sources if available
        if (result.sources && result.sources.length > 0) {
            html += `<h3>Related News Sources:</h3><ul>`;

            result.sources.forEach((source, index) => {
                const date = source.date ? formatDate(source.date) : '';
                const relevance = source.relevance ? ` (${Math.round(source.relevance * 100)}% relevant)` : '';

                html += `
                    <li>
                        <div class="source-header">
                            <strong>${escapeHtml(source.name)}</strong>
                            ${relevance ? `<span class="relevance-badge">${relevance}</span>` : ''}
                        </div>
                        ${source.source ? `<div class="source-name">Source: ${escapeHtml(source.source)}</div>` : ''}
                        ${date ? `<div class="source-date">${date}</div>` : ''}
                        ${source.url ? `<a href="${source.url}" class="source-link" target="_blank" rel="noopener">Read article →</a>` : ''}
                    </li>
                `;
            });

            html += `</ul>`;

            // Add summary if multiple sources
            if (result.total_articles_found && result.total_articles_found > result.sources.length) {
                html += `<p class="sources-summary">Showing top ${result.sources.length} of ${result.total_articles_found} articles found.</p>`;
            }
        } else {
            html += `<div class="no-sources">No specific news articles found for this claim.</div>`;
        }

        // Add debug info in development
        if (result.debug && window.location.hostname === 'localhost') {
            html += `
                <details class="debug-info">
                    <summary>Debug Information</summary>
                    <pre>${JSON.stringify(result.debug, null, 2)}</pre>
                </details>
            `;
        }

        html += `</div></div>`;

        // Update the container with animation
        resultContainer.innerHTML = html;

        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    // Helper functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${escapeHtml(message)}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    function formatDate(dateString) {
        if (!dateString) return '';

        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return dateString; // Return original if invalid

            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return dateString;
        }
    }
});