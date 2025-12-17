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

// Helper functions
function formatDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

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