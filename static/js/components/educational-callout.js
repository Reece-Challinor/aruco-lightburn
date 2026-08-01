// @ts-check

/**
 * C-14 EducationalCallout
 * 
 * @param {Object} options
 * @param {string} options.id - Unique ID for dismissal persistence
 * @param {string} options.content - The educational text
 * @param {string} [options.linkUrl] - Optional "Learn more" URL
 * @returns {HTMLElement|null} Returns null if already dismissed
 */
export function createEducationalCallout({ id, content, linkUrl }) {
    // Check if dismissed
    const stateKey = `aruco_dismissed_${id}`;
    let isDismissed = false;
    try {
        if (window.StateManager) {
            isDismissed = window.StateManager.get(stateKey) === true;
        } else {
            isDismissed = localStorage.getItem(stateKey) === 'true';
        }
    } catch (e) { }

    if (isDismissed) return null;

    const callout = document.createElement('div');
    callout.className = 'edu-callout';
    
    const icon = document.createElement('div');
    icon.className = 'edu-callout-icon';
    icon.innerHTML = '<i class="bi bi-info-circle"></i>';
    callout.appendChild(icon);
    
    const contentEl = document.createElement('div');
    contentEl.className = 'edu-callout-content';
    contentEl.textContent = content;
    
    if (linkUrl) {
        const link = document.createElement('a');
        link.href = linkUrl;
        link.className = 'd-inline-block ms-1';
        link.innerHTML = 'Learn more &rsaquo;';
        contentEl.appendChild(link);
    }
    
    callout.appendChild(contentEl);
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'edu-callout-close';
    closeBtn.innerHTML = '<i class="bi bi-x fs-5"></i>';
    closeBtn.setAttribute('aria-label', 'Dismiss');
    
    closeBtn.addEventListener('click', () => {
        try {
            if (window.StateManager) {
                window.StateManager.set(stateKey, true);
            } else {
                localStorage.setItem(stateKey, 'true');
            }
        } catch (e) { }
        callout.remove();
    });
    
    callout.appendChild(closeBtn);
    
    return callout;
}
