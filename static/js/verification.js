// Verification functionality for TruthTrack

document.addEventListener('DOMContentLoaded', function() {
    const verifyButton = document.getElementById('verify-button');
    const claimInput = document.getElementById('claim-input');
    const resultContainer = document.getElementById('result-container');
    const resultsSection = document.getElementById('results-section');

    if (verifyButton) {
        verifyButton.addEventListener('click', verifyFact);
    }

    function verifyFact() {
        // Validate input
        const claim = claimInput.value.trim();
        if (!claim) {
            showNotification('Please enter a claim to verify', 'warning');
            return;
        }

        // Show loading state
        resultContainer.innerHTML = '<div class="loading">Checking facts... This may take a moment.</div>';
        resultsSection.classList.add('active');

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
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                displayResults(data.result, claim);
            } else {
                throw new Error(data.error || 'An unknown error occurred');
            }
        })
        .catch(error => {
            resultContainer.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        });
    }

    function displayResults(result, originalClaim) {
        // Determine score class
        let scoreClass = 'medium-score';
        if (result.score >= 70) {
            scoreClass = 'high-score';
        } else if (result.score <= 30) {
            scoreClass = 'low-score';
        }

        // Create the result HTML
        let html = `
            <div class="result-card">
                <div class="score-container ${scoreClass}">
                    <div class="score">${result.score}</div>
                    <div class="score-label">Truth Score</div>
                </div>
                <div class="result-details">
                    <div class="claim-text">"${originalClaim}"</div>
                    <div class="result-message">${result.message}</div>
        `;

        // Add sources if available
        if (result.sources && result.sources.length > 0) {
            html += `<h3>Fact-Check Sources:</h3><ul>`;

            result.sources.forEach(source => {
                let date = source.reviewDate ? formatDate(source.reviewDate) : '';
                html += `
                    <li>
                        <strong>${source.source}</strong>: ${source.rating || 'See analysis'}
                        ${date ? ` (${date})` : ''}
                        <br>
                        <a href="${source.url}" class="source-link" target="_blank">${source.title || 'View source'}</a>
                    </li>
                `;
            });

            html += `</ul>`;
        } else {
            html += `<p>No specific fact-checks were found for this claim.</p>`;
        }

        html += `</div></div>`;

        // Update the container
        resultContainer.innerHTML = html;
    }

    // Helper function to show notifications
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    }

    // Format date helper function
    function formatDate(dateString) {
        if (!dateString) return '';

        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
});