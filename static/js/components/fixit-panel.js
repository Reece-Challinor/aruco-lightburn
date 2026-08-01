// @ts-check

/**
 * C-13 FixItPanel
 * 
 * @param {Object} options
 * @param {string} options.title - What happened
 * @param {string} options.cause - Probable cause
 * @param {Array<{label: string, onClick: Function, primary?: boolean}>} options.actions - Fix actions
 * @param {boolean} [options.isWarning] - Use warning variant instead of error
 * @param {Function} [options.onCopyDiagnostics] - Action for "Copy diagnostics"
 * @returns {HTMLElement}
 */
export function createFixItPanel({ title, cause, actions, isWarning = false, onCopyDiagnostics }) {
    const panel = document.createElement('div');
    panel.className = `fixit-panel ${isWarning ? 'warning' : ''}`;
    panel.setAttribute('role', 'alert');
    
    const header = document.createElement('div');
    header.className = 'fixit-header';
    
    const icon = document.createElement('i');
    icon.className = `bi ${isWarning ? 'bi-exclamation-triangle' : 'bi-exclamation-octagon'} fs-5`;
    header.appendChild(icon);
    
    const titleEl = document.createElement('div');
    titleEl.className = 'fixit-title';
    titleEl.textContent = title;
    header.appendChild(titleEl);
    
    panel.appendChild(header);
    
    const causeEl = document.createElement('div');
    causeEl.className = 'fixit-cause';
    causeEl.textContent = cause;
    panel.appendChild(causeEl);
    
    const actionsEl = document.createElement('div');
    actionsEl.className = 'fixit-actions';
    
    if (actions && actions.length > 0) {
        actions.forEach((action, i) => {
            const btn = document.createElement('button');
            btn.className = `btn btn-sm ${action.primary ? 'btn-primary' : 'btn-outline-secondary'}`;
            btn.textContent = action.label;
            btn.addEventListener('click', action.onClick);
            actionsEl.appendChild(btn);
        });
    } else {
        // Fallback if no actions provided
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-outline-secondary';
        btn.textContent = 'Dismiss';
        btn.onclick = () => panel.remove();
        actionsEl.appendChild(btn);
    }
    
    if (onCopyDiagnostics) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn-quiet';
        copyBtn.textContent = 'Copy diagnostics';
        copyBtn.addEventListener('click', onCopyDiagnostics);
        actionsEl.appendChild(copyBtn);
    }
    
    panel.appendChild(actionsEl);
    
    return panel;
}
