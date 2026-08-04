/**
 * Veritify AI - Verification Dashboard Component
 * Built from scratch with strict layout architecture to prevent UI breakage
 * 
 * ARCHITECTURE:
 * - Container with 3 Rigid Vertical Sections (gap-8)
 * - Section 1: Verdict Banner (Horizontal: Icon + Text)
 * - Section 2: Metrics Row (3-Column Grid)
 * - Section 3: Evidence Grid (2-Column Grid)
 */

// ============================================================================
// HELPER UTILITIES
// ============================================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showNotification(message, type = 'info') {
    // Simple notification implementation
    console.log(`[${type.toUpperCase()}] ${message}`);
    // You can enhance this with a toast library
}

// ============================================================================
// MAIN EVENT LISTENERS
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    const verifyButton = document.getElementById('verify-button');
    const claimInput = document.getElementById('claim-input');
    const resultContainer = document.getElementById('result-container');
    const resultsSection = document.getElementById('results-section');

    if (verifyButton) {
        verifyButton.addEventListener('click', verifyFact);

        // Allow Ctrl+Enter or Cmd+Enter to submit
        claimInput.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                verifyFact();
            }
        });
    }

    // ============================================================================
    // FACT VERIFICATION HANDLER
    // ============================================================================

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
            <div class="flex flex-col items-center justify-center p-12 bg-white rounded-xl border border-gray-200">
                <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
                <p class="text-lg font-medium text-gray-700">Analyzing claim across multiple sources...</p>
                <p class="text-sm text-gray-500 mt-2">This may take a moment</p>
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
                    <div class="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
                        <svg class="w-16 h-16 text-red-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h3 class="text-xl font-bold text-gray-900 mb-2">Error Occurred</h3>
                        <p class="text-gray-700 mb-4">${escapeHtml(error.message)}</p>
                        <button onclick="location.reload()" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            <i class="fas fa-redo mr-2"></i> Try Again
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

    // ============================================================================
    // RESULT RENDERING FUNCTION - PIXEL PERFECT DASHBOARD
    // ============================================================================

    function displayResults(result, originalClaim) {
        // Determine verdict state
        const verdict = (result.verdict || 'UNVERIFIED').toUpperCase();
        const isFalse = verdict === 'FALSE';
        const isTrue = verdict === 'TRUE';
        const confidencePercent = result.confidence ? Math.round(result.confidence * 100) : 0;
        const sources = result.evidence || [];

        // Dynamic styling based on verdict
        const bgColor = isFalse ? 'bg-red-50' : isTrue ? 'bg-green-50' : 'bg-yellow-50';
        const borderColor = isFalse ? 'border-red-600' : isTrue ? 'border-green-600' : 'border-yellow-600';
        const textColor = isFalse ? 'text-red-700' : isTrue ? 'text-green-700' : 'text-yellow-700';
        const iconColor = isFalse ? 'text-red-600' : isTrue ? 'text-green-600' : 'text-yellow-600';
        const iconBgColor = isFalse ? 'bg-red-100' : isTrue ? 'bg-green-100' : 'bg-yellow-100';
        const progressColor = isFalse ? 'bg-red-500' : isTrue ? 'bg-green-500' : 'bg-yellow-500';
        const verdictText = isFalse ? 'CLAIM PROVEN FALSE' : isTrue ? 'CLAIM CONFIRMED TRUE' : 'CLAIM PARTIALLY ACCURATE';

        // SVG Icons
        const shieldIcon = isFalse
            ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />'
            : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />';

        // Build HTML
        let html = `
            <div class="animate-in space-y-8">

                <!-- ================================================================== -->
                <!-- ZONE 1: The Verdict Banner -->
                <!-- ================================================================== -->
                <div class="${bgColor} ${borderColor} rounded-xl border-l-[8px] p-8 shadow-sm flex items-start gap-6">
                    <!-- Icon - LOCKED SIZE -->
                    <div class="p-3 rounded-full ${iconBgColor} flex-shrink-0">
                        <svg class="w-10 h-10 ${iconColor}" style="width: 40px; height: 40px; min-width: 40px; min-height: 40px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            ${shieldIcon}
                        </svg>
                    </div>
                    <div>
                        <h1 class="text-4xl font-black uppercase tracking-tight mb-2 ${textColor}">
                            ${verdictText}
                        </h1>
                        <p class="text-xl text-gray-700 font-medium">
                            Claim: <span class="italic text-gray-600">"${escapeHtml(originalClaim)}"</span>
                        </p>
                    </div>
                </div>

                <!-- ================================================================== -->
                <!-- ZONE 2: The "Trust Metrics" Grid -->
                <!-- ================================================================== -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    
                    <!-- Card 1: Confidence Score -->
                    <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm flex flex-col justify-between">
                        <div class="flex items-center gap-2 text-gray-500 mb-2">
                            <svg class="w-5 h-5" style="width: 20px; height: 20px; min-width: 20px; min-height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                            </svg>
                            <span class="font-semibold text-sm uppercase tracking-wider">Confidence Score</span>
                        </div>
                        <div class="mb-3">
                            <div class="text-xs text-gray-500 mb-1">AI Confidence</div>
                            <div class="text-5xl font-black text-gray-900">${confidencePercent}%</div>
                        </div>
                        <!-- Progress Bar -->
                        <div class="w-full bg-gray-100 h-3 rounded-full overflow-hidden">
                            <div class="${progressColor} h-full rounded-full transition-all duration-500" style="width: ${confidencePercent}%"></div>
                        </div>
                    </div>

                    <!-- Card 2: Sources Analyzed -->
                    <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                        <p class="text-gray-500 font-semibold text-sm uppercase tracking-wider mb-2">Sources Analyzed</p>
                        <p class="text-4xl font-bold text-gray-900">${sources.length}</p>
                        <p class="text-sm text-gray-400 mt-2">Cross-referenced sources</p>
                    </div>

                    <!-- Card 3: Bias Leaning -->
                    <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                        <p class="text-gray-500 font-semibold text-sm uppercase tracking-wider mb-2">Bias Leaning</p>
                        <p class="text-2xl font-bold text-gray-900">${result.bias || 'Neutral / Scientific'}</p>
                        <div class="flex gap-1 mt-3">
                            <div class="h-2 flex-1 bg-blue-200 rounded-l-full"></div>
                            <div class="h-2 flex-1 bg-gray-400"></div>
                            <div class="h-2 flex-1 bg-red-200 rounded-r-full"></div>
                        </div>
                    </div>
                </div>

                <!-- ================================================================== -->
                <!-- ZONE 3: Evidence Grid -->
                <!-- ================================================================== -->
                <div>
                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-[0.2em] mb-6">
                        PRIMARY EVIDENCE SOURCES
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        ${renderEvidenceSources(sources)}
                    </div>
                </div>

            </div>
        `;

        resultContainer.innerHTML = html;

        // Smooth scroll to results
        setTimeout(() => {
            smoothScrollTo(resultsSection);
        }, 100);
    }

    // ============================================================================
    // EVIDENCE SOURCES RENDERER
    // ============================================================================

    function renderEvidenceSources(sources) {
        if (!sources || sources.length === 0) {
            return `
                <div class="col-span-2 bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
                    <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p class="text-gray-500 text-lg">No evidence sources available for this claim.</p>
                </div>
            `;
        }

        return sources.map(source => {
            const title = source.title || source.source || 'Untitled Source';
            const snippet = source.snippet || source.excerpt || 'No description available.';
            const url = source.url || '#';
            const date = formatDate(source.published_date || source.date);

            // Determine stance badge
            const entailment = (source.entailment_label || source.entailment || 'NEUTRAL').toUpperCase();
            let badgeText = 'Context';
            let badgeClass = 'bg-gray-100 text-gray-800';

            if (entailment === 'ENTAILS' || entailment === 'SUPPORTS') {
                badgeText = 'Supports';
                badgeClass = 'bg-green-100 text-green-700';
            } else if (entailment === 'CONTRADICTS' || entailment === 'REFUTES') {
                badgeText = 'Contradicts';
                badgeClass = 'bg-red-100 text-red-700';
            }

            return `
                <div class="group bg-white border border-gray-200 rounded-lg p-5 hover:border-blue-400 hover:shadow-md transition-all duration-200 cursor-pointer">
                    <div class="flex justify-between items-start mb-3">
                        <div>
                            <p class="font-bold text-gray-900">${escapeHtml(title)}</p>
                            ${date ? `<p class="text-xs text-gray-500">${date}</p>` : ''}
                        </div>
                        <span class="px-2 py-1 rounded text-xs font-bold ${badgeClass}">
                            ${badgeText}
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 line-clamp-3 leading-relaxed mb-4">
                        ${escapeHtml(snippet)}
                    </p>
                    <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="flex items-center text-blue-600 font-semibold text-xs group-hover:underline">
                        Read Source
                        <svg class="w-3 h-3 ml-1" style="width: 12px; height: 12px; min-width: 12px; min-height: 12px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </a>
                </div>
            `;
        }).join('');
    }

    // Make helper functions globally accessible
    window.escapeHtml = escapeHtml;
    window.formatDate = formatDate;
    window.smoothScrollTo = smoothScrollTo;
});