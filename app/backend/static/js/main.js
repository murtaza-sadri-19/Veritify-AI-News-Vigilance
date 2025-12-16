// Main JavaScript file for TruthTrack - Enhanced UI/UX

document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    setupMobileMenu();
    setupCharacterCounter();
    setupAccessibility();
});

/**
 * Initialize navigation active state
 */
function initializeNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.style.borderBottomColor = 'var(--primary-color)';
        }
    });
}

/**
 * Setup mobile menu toggle
 */
function setupMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.navbar-menu');

    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            
            // Animate hamburger
            const spans = hamburger.querySelectorAll('span');
            spans.forEach((span, index) => {
                if (navMenu.classList.contains('active')) {
                    if (index === 0) span.style.transform = 'rotate(45deg) translateY(10px)';
                    if (index === 1) span.style.opacity = '0';
                    if (index === 2) span.style.transform = 'rotate(-45deg) translateY(-10px)';
                } else {
                    span.style.transform = 'none';
                    span.style.opacity = '1';
                }
            });
        });

        // Close menu when clicking on a link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                hamburger.querySelectorAll('span').forEach(span => {
                    span.style.transform = 'none';
                    span.style.opacity = '1';
                });
            });
        });
    }
}

/**
 * Setup character counter for claim input
 */
function setupCharacterCounter() {
    const claimInput = document.getElementById('claim-input');
    const charCount = document.getElementById('char-count');

    if (claimInput && charCount) {
        claimInput.addEventListener('input', function() {
            charCount.textContent = this.value.length;
            
            // Max length feedback
            if (this.value.length >= 500) {
                this.value = this.value.substring(0, 500);
                charCount.textContent = '500';
            }
        });
    }
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