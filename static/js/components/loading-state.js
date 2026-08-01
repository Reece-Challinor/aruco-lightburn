// @ts-check

/**
 * C-12 Loading/Empty States
 * 
 * @param {Object} options
 * @param {'instant'|'working'|'long'|'byte-honest'|'empty'} options.type - State type
 * @param {string} [options.label] - Progress/stage label
 * @param {string} [options.sizeString] - Size for byte-honest
 * @param {number} [options.progress] - 0-100 progress value
 * @param {Function} [options.onCancel] - Cancel callback for 'long'
 * @param {Object} [options.emptyActions] - Empty state actions
 * @returns {HTMLElement}
 */
export function createLoadingState({ type, label, sizeString, progress = 0, onCancel, emptyActions }) {
    const container = document.createElement('div');
    container.className = 'state-container';
    
    if (type === 'instant') {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-box';
        skeleton.style.width = '100%';
        skeleton.style.height = '200px';
        container.appendChild(skeleton);
        return container;
    }
    
    if (type === 'empty') {
        const icon = document.createElement('i');
        icon.className = 'bi bi-inbox fs-1 mb-3 text-muted';
        container.appendChild(icon);
        
        if (label) {
            const labelEl = document.createElement('p');
            labelEl.textContent = label;
            container.appendChild(labelEl);
        }
        
        if (emptyActions) {
            const actionsEl = document.createElement('div');
            actionsEl.className = 'mt-3 d-flex gap-2 justify-content-center';
            if (emptyActions.sampleDataAction) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-outline-secondary btn-sm';
                btn.textContent = 'Load Sample Data';
                btn.onclick = emptyActions.sampleDataAction;
                actionsEl.appendChild(btn);
            }
            if (emptyActions.handoffLabel && emptyActions.handoffAction) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-primary btn-sm';
                btn.innerHTML = `${emptyActions.handoffLabel} &rsaquo;`;
                btn.onclick = emptyActions.handoffAction;
                actionsEl.appendChild(btn);
            }
            container.appendChild(actionsEl);
        }
        return container;
    }
    
    // working, long, byte-honest
    if (label) {
        const labelEl = document.createElement('div');
        labelEl.textContent = type === 'byte-honest' && sizeString ? 
            `Loading vision engine (~${sizeString}, cached after first use)` : 
            label;
        container.appendChild(labelEl);
    }
    
    const pContainer = document.createElement('div');
    pContainer.className = 'progress-container';
    pContainer.setAttribute('role', 'progressbar');
    pContainer.setAttribute('aria-valuenow', progress.toString());
    pContainer.setAttribute('aria-valuemin', '0');
    pContainer.setAttribute('aria-valuemax', '100');
    
    const pBar = document.createElement('div');
    pBar.className = 'progress-bar';
    pBar.style.width = `${progress}%`;
    pContainer.appendChild(pBar);
    container.appendChild(pContainer);
    
    if (type === 'long' && onCancel) {
        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn btn-link text-muted mt-2';
        cancelBtn.textContent = 'Cancel';
        cancelBtn.onclick = onCancel;
        container.appendChild(cancelBtn);
    }
    
    return container;
}
