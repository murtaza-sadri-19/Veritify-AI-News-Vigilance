// ============================================
// Veritify - Main JavaScript
// Glass & Truth Interactions
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    initializeGlassEffects();
    initializeNavbar();
    initializeSearchCard();
});

// ============================================
// GLASSMORPHIC INTERACTIONS
// ============================================

function initializeGlassEffects() {
    // Add subtle parallax effect to glass cards
    const glassElements = document.querySelectorAll('.search-card, .feature-card');

    document.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;

        glassElements.forEach((el, index) => {
            const speed = (index + 1) * 0.5;
            const x = (mouseX - 0.5) * speed;
            const y = (mouseY - 0.5) * speed;

            el.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
}

// ============================================
// NAVBAR INTERACTIONS
// ============================================

function initializeNavbar() {
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        // Add shadow on scroll
        if (currentScroll > 50) {
            navbar.style.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.25)';
        } else {
            navbar.style.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.15)';
        }

        lastScroll = currentScroll;
    });
}

// ============================================
// SEARCH CARD INTERACTIONS
// ============================================

function initializeSearchCard() {
    const searchInput = document.getElementById('claim-input');
    const searchCard = document.querySelector('.search-card');

    if (!searchInput || !searchCard) return;

    // Add shimmer effect on focus
    searchInput.addEventListener('focus', () => {
        searchCard.classList.add('focused');
    });

    searchInput.addEventListener('blur', () => {
        searchCard.classList.remove('focused');
    });

    // Character count and validation
    searchInput.addEventListener('input', (e) => {
        const length = e.target.value.length;

        if (length > 500) {
            searchCard.style.borderColor = '#e53935';
        } else if (length > 0) {
            searchCard.style.borderColor = 'var(--primary-blue)';
        } else {
            searchCard.style.borderColor = '';
        }
    });
}

/**
 * Setup accessibility features
 */
function setupAccessibility() {
    // Add keyboard navigation support
    document.addEventListener('keydown', function(event) {
        // Skip to main content with Alt+M
        if (event.altKey && event.key === 'm') {
            event.preventDefault();
            const main = document.querySelector('main');
            if (main) main.focus();
        }
    });

    // Ensure buttons are keyboard accessible
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('keypress', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                this.click();
            }
        });
    });
}

/**
 * Helper function to escape HTML
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Helper function to format date
 */
function formatDate(dateString) {
    if (!dateString) return '';

    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;

        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

/**
 * Show notification with auto-dismiss
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications of the same type
    const existingNotifications = document.querySelectorAll(`.notification.${type}`);
    existingNotifications.forEach(n => {
        n.classList.remove('show');
        setTimeout(() => n.remove(), 300);
    });

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${escapeHtml(message)}</span>
        <button class="notification-close" aria-label="Close notification">×</button>
    `;

    document.body.appendChild(notification);

    // Show notification with animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Close button handler
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    });

    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, duration);
}

/**
 * Smooth scroll to element
 */
function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}