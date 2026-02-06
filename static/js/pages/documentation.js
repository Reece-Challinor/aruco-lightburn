/**
 * Documentation Page JavaScript
 * Handles smooth scrolling and navigation highlighting
 */

document.addEventListener('DOMContentLoaded', () => {
    setupSmoothScrolling();
    setupScrollSpy();
});

function setupSmoothScrolling() {
    document.querySelectorAll('.doc-nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Update active state
                document.querySelectorAll('.doc-nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });
}

function setupScrollSpy() {
    window.addEventListener('scroll', () => {
        const sections = document.querySelectorAll('section[id]');
        let current = '';

        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            if (rect.top <= 100 && rect.bottom >= 100) {
                current = section.getAttribute('id');
            }
        });

        if (current) {
            document.querySelectorAll('.doc-nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}
