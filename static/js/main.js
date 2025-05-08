// Main JavaScript file for TruthTrack

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any global functionality
    initializeNavigation();
    setupEventListeners();
});

function initializeNavigation() {
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('nav ul li a');

    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath) {
            item.classList.add('active');
        }
    });
}

function setupEventListeners() {
    // Add any global event listeners here

    // Example: Toggle mobile navigation menu
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const nav = document.querySelector('nav ul');
            nav.classList.toggle('active');
        });
    }
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