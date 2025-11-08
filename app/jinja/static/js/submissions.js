/**
 * Submissions Page Enhancement
 * Handles filtering and dynamic interactions
 */

(function() {
    'use strict';

    // Toggle filters panel (backup in case inline handler doesn't work)
    function initFilterToggle() {
        const toggleBtn = document.getElementById('toggleFilters');
        const panel = document.getElementById('filtersPanel');

        if (toggleBtn && panel) {
            // Remove any existing inline onclick
            toggleBtn.removeAttribute('onclick');

            toggleBtn.addEventListener('click', function() {
                const isVisible = panel.style.display !== 'none';
                panel.style.display = isVisible ? 'none' : 'block';

                // Update button icon
                const svg = this.querySelector('svg');
                if (svg) {
                    svg.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
                    svg.style.transition = 'transform 200ms';
                }
            });
        }
    }

    // Handle filter form submission
    function initFilterForm() {
        const form = document.getElementById('filtersForm');
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const params = new URLSearchParams();
            const formData = new FormData(form);

            // Add base params
            params.set('page', '1');
            params.set('page_size', formData.get('page_size') || '10');
            params.set('sort_by', formData.get('sort_by') || 'id');
            params.set('sort_desc', formData.get('sort_desc') || 'false');

            // Collect operator/value pairs
            const ops = {};
            const elements = Array.from(form.elements);

            elements.forEach(el => {
                if (!el.name) return;

                if (el.name.endsWith('__op')) {
                    const field = el.name.slice(0, -4);
                    ops[field] = el.value;
                }
            });

            elements.forEach(el => {
                if (!el.name) return;

                if (el.name.endsWith('__value')) {
                    const field = el.name.slice(0, -7);
                    const op = ops[field] || 'eq';
                    if (el.value) {
                        params.set(`${field}__${op}`, el.value);
                    }
                }

                if (el.name.endsWith('__from') && el.value) {
                    params.set(el.name, el.value);
                }

                if (el.name.endsWith('__to') && el.value) {
                    params.set(el.name, el.value);
                }
            });

            window.location.href = `${location.pathname}?${params.toString()}`;
        });
    }

    // Add loading states to links
    function initLoadingStates() {
        const links = document.querySelectorAll('.page-link, .data-table a');

        links.forEach(link => {
            link.addEventListener('click', function(e) {
                // Show loading indicator
                this.style.opacity = '0.6';
                this.style.pointerEvents = 'none';
            });
        });
    }

    // Highlight active filters
    function highlightActiveFilters() {
        const urlParams = new URLSearchParams(window.location.search);
        let hasFilters = false;

        urlParams.forEach((value, key) => {
            if (key.includes('__') && value) {
                hasFilters = true;
            }
        });

        if (hasFilters) {
            const toggleBtn = document.getElementById('toggleFilters');
            if (toggleBtn) {
                toggleBtn.classList.add('btn-primary');
                toggleBtn.classList.remove('btn-secondary');
            }
        }
    }

    // Initialize
    function init() {
        console.log('🚀 Initializing submissions page...');

        initFilterToggle();
        initFilterForm();
        initLoadingStates();
        highlightActiveFilters();

        console.log('✅ Submissions page initialized');
    }

    // Auto-initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();