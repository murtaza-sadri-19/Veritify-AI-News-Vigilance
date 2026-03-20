// ============================================
// Glass Effects & Navbar Interactions
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    initializeGlassEffects();
    initializeNavBar();
});

// ============================================
// GLASS EFFECTS - Parallax & Mouse Tracking
// ============================================

function initializeGlassEffects() {
    const searchCard = document.querySelector('.search-card');

    if (searchCard) {
        // Parallax effect on mouse move
        document.addEventListener('mousemove', (e) => {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;

            // Subtle tilt based on mouse position
            const rotateX = (y - 0.5) * 2;
            const rotateY = (x - 0.5) * 2;

            searchCard.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });

        // Reset on mouse leave
        document.addEventListener('mouseleave', () => {
            searchCard.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    }
}

// ============================================
// NAVBAR - Sticky Behavior & Shadow
// ============================================

function initializeNavBar() {
    const navbar = document.querySelector('.navbar');

    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                navbar.style.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.2)';
                navbar.style.backdropFilter = 'blur(14px)';
            } else {
                navbar.style.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.15)';
                navbar.style.backdropFilter = 'blur(12px)';
            }
        });
    }
}

// ============================================
// BUTTON ANIMATIONS
// ============================================

// Add ripple effect to buttons
document.querySelectorAll('.btn-verify, .btn-signup').forEach((btn) => {
    btn.addEventListener('click', function (e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

// ============================================
// SUGGESTION CHIPS
// ============================================

document.querySelectorAll('.suggestion-chip').forEach((chip) => {
    chip.addEventListener('click', function () {
        const text = this.textContent.trim();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.value = text;
            searchInput.focus();
        }
    });
});
