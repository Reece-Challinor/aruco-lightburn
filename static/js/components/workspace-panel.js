// @ts-check

/**
 * C-03 WorkspacePanel Set
 * 
 * @param {Object} options
 * @param {string} options.id - The panel ID
 * @param {string} options.title - The panel title
 * @param {HTMLElement|string} options.content - The panel content
 * @returns {HTMLElement}
 */
export function createWorkspacePanel({ id, title, content }) {
    const panel = document.createElement('section');
    panel.className = 'workspace-panel';
    panel.id = id;
    panel.setAttribute('aria-label', title);

    const header = document.createElement('header');
    header.className = 'workspace-panel-header';
    
    const titleEl = document.createElement('h2');
    titleEl.className = 'h6 mb-0';
    titleEl.textContent = title;
    
    header.appendChild(titleEl);
    
    const contentEl = document.createElement('div');
    contentEl.className = 'workspace-panel-content';
    
    if (typeof content === 'string') {
        contentEl.innerHTML = content;
    } else if (content) {
        contentEl.appendChild(content);
    }
    
    panel.appendChild(header);
    panel.appendChild(contentEl);
    
    return panel;
}

/**
 * Creates a mode segmented control
 * 
 * @param {Object} options
 * @param {string} options.name - The radio group name
 * @param {Array<{value: string, label: string}>} options.modes - The modes
 * @param {string} options.initialValue - The initial mode
 * @param {Function} options.onChange - Callback on change
 * @returns {HTMLElement}
 */
export function createSegmentedControl({ name, modes, initialValue, onChange }) {
    const group = document.createElement('div');
    group.className = 'segmented-control';
    group.setAttribute('role', 'radiogroup');
    
    modes.forEach(mode => {
        const id = `mode-${name}-${mode.value}`;
        
        const input = document.createElement('input');
        input.type = 'radio';
        input.name = name;
        input.id = id;
        input.value = mode.value;
        if (mode.value === initialValue) {
            input.checked = true;
        }
        
        input.addEventListener('change', (e) => {
            if (input.checked && onChange) {
                onChange(mode.value);
            }
        });
        
        const label = document.createElement('label');
        label.htmlFor = id;
        label.textContent = mode.label;
        
        group.appendChild(input);
        group.appendChild(label);
    });
    
    return group;
}
