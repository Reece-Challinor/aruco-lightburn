// @ts-check

/**
 * C-09 VerdictCard
 * 
 * @param {Object} options
 * @param {string} options.verdict - The main verdict text
 * @param {'pass'|'warn'|'fail'} options.tier - The tier of the verdict
 * @param {string} options.cause - The dominant cause text
 * @param {Array<{label: string, value: string|number}>} options.numerics - Layer 2 numerics
 * @param {string} [options.methodologyLink] - Optional methodology link
 * @returns {HTMLElement}
 */
export function createVerdictCard({ verdict, tier, cause, numerics = [], methodologyLink }) {
    const card = document.createElement('div');
    card.className = `verdict-card tier-${tier}`;
    
    const line = document.createElement('div');
    line.className = 'verdict-line';
    line.innerHTML = `<span>${verdict}</span>`;
    
    const expandBtn = document.createElement('button');
    expandBtn.className = 'btn btn-sm btn-link p-0 text-muted';
    expandBtn.innerHTML = '<i class="bi bi-chevron-down"></i>';
    expandBtn.setAttribute('aria-expanded', 'false');
    expandBtn.setAttribute('aria-label', 'View details');
    line.appendChild(expandBtn);
    
    const causeEl = document.createElement('div');
    causeEl.className = 'verdict-cause';
    causeEl.textContent = cause;
    
    card.appendChild(line);
    card.appendChild(causeEl);
    
    if (numerics.length > 0) {
        const details = document.createElement('div');
        details.className = 'verdict-details';
        
        const table = document.createElement('table');
        table.className = 'verdict-table';
        
        numerics.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${item.label}</td><td>${item.value}</td>`;
            table.appendChild(tr);
        });
        
        details.appendChild(table);
        
        if (methodologyLink) {
            const link = document.createElement('a');
            link.href = methodologyLink;
            link.className = 'small text-muted d-block mt-2';
            link.innerHTML = '<i class="bi bi-info-circle me-1"></i>Methodology';
            details.appendChild(link);
        }
        
        card.appendChild(details);
        
        expandBtn.addEventListener('click', () => {
            const isExpanded = card.classList.contains('expanded');
            if (isExpanded) {
                card.classList.remove('expanded');
                expandBtn.innerHTML = '<i class="bi bi-chevron-down"></i>';
                expandBtn.setAttribute('aria-expanded', 'false');
            } else {
                card.classList.add('expanded');
                expandBtn.innerHTML = '<i class="bi bi-chevron-up"></i>';
                expandBtn.setAttribute('aria-expanded', 'true');
            }
        });
    } else {
        expandBtn.style.display = 'none';
    }
    
    return card;
}
