(function() {
    'use strict';

    const CONFIG = {
        validateOnBlur: true,
        validateOnChange: false,
        showSuccessState: true,
        debounceDelay: 300
    };

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func(...args), wait);
        };
    }

    function validateField(field) {
        const isValid = field.checkValidity();

        field.classList.remove('is-valid', 'is-invalid');

        if (field.value.trim() === '' && !field.required) {
            return true;
        }

        if (isValid) {
            if (CONFIG.showSuccessState && field.value.trim() !== '') {
                field.classList.add('is-valid');
            }
            return true;
        } else {
            field.classList.add('is-invalid');

            const feedback = field.parentElement.querySelector('.invalid-feedback');
            if (feedback && field.validationMessage) {
                feedback.textContent = field.validationMessage;
            }
            return false;
        }
    }

    function validateForm(form) {
        let isValid = true;
        const fields = form.querySelectorAll('input, select, textarea');

        fields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    function showAlert(message, type = 'danger') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <strong>${type === 'danger' ? 'Error!' : 'Success!'}</strong> ${message}
        `;

        const cardBody = document.querySelector('.card-body');
        if (cardBody) {
            cardBody.insertBefore(alert, cardBody.firstChild);

            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 300ms';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    }

    function handleFormSubmit(form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();

                const firstError = form.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    firstError.focus();
                }

                showAlert('Please correct the errors before submitting.');
                return false;
            }

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm" style="margin-right: 0.5rem;"></span>
                    Submitting...
                `;
            }
        });
    }

    function enhanceNumberField(field) {
        const min = parseFloat(field.getAttribute('min'));
        const max = parseFloat(field.getAttribute('max'));

        field.addEventListener('change', function() {
            let value = parseFloat(this.value);
            if (isNaN(value)) return;

            if (!isNaN(min) && value < min) this.value = min;
            if (!isNaN(max) && value > max) this.value = max;
        });
    }

    function enhanceEmailField(field) {
        field.addEventListener('input', debounce(function() {
            const value = this.value.trim();
            if (value && !value.includes('@')) {
                this.setCustomValidity('Please include an @ symbol');
            } else {
                this.setCustomValidity('');
            }
        }, CONFIG.debounceDelay));
    }

    function enhancePasswordField(field) {
        const wrapper = field.parentElement;
        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'password-toggle';
        toggle.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
        `;

        toggle.style.cssText = `
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            border: none;
            background: transparent;
            cursor: pointer;
            padding: 4px;
            color: var(--color-text-muted);
            transition: color 150ms;
        `;

        wrapper.style.position = 'relative';

        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            field.type = field.type === 'password' ? 'text' : 'password';
            this.style.color = field.type === 'text' ? 'var(--color-primary)' : 'var(--color-text-muted)';
        });

        wrapper.appendChild(toggle);
    }

    function addCharacterCounter(field) {
        const maxLength = field.getAttribute('maxlength');
        if (!maxLength) return;

        const counter = document.createElement('small');
        counter.className = 'field-helper-text';
        counter.style.cssText = 'display: block; text-align: right; margin-top: 0.5rem;';

        const updateCounter = () => {
            const remaining = maxLength - field.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.style.color = remaining < 10 ? 'var(--color-error)' : 'var(--color-text-muted)';
        };

        field.addEventListener('input', updateCounter);
        field.parentElement.appendChild(counter);
        updateCounter();
    }

    function addKeyboardShortcuts(form) {
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                form.requestSubmit();
            }
        });
    }

    function initializeForm() {
        const form = document.querySelector('form');
        if (!form) return;

        console.log('🚀 Initializing form enhancements...');

        const fields = form.querySelectorAll('input:not([type="submit"]):not([type="reset"]), select, textarea');

        fields.forEach(field => {
            if (CONFIG.validateOnBlur) {
                field.addEventListener('blur', function() {
                    if (this.value.trim() !== '') {
                        validateField(this);
                    }
                });
            }

            if (CONFIG.validateOnChange) {
                field.addEventListener('input', debounce(function() {
                    if (this.value.trim() !== '') {
                        validateField(this);
                    }
                }, CONFIG.debounceDelay));
            }

            if (field.type === 'number') {
                enhanceNumberField(field);
            } else if (field.type === 'email') {
                enhanceEmailField(field);
            } else if (field.type === 'password') {
                enhancePasswordField(field);
            }

            if ((field.tagName === 'INPUT' || field.tagName === 'TEXTAREA') && field.getAttribute('maxlength')) {
                addCharacterCounter(field);
            }
        });

        handleFormSubmit(form);
        addKeyboardShortcuts(form);

        const resetBtn = form.querySelector('button[type="reset"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to reset the form?')) {
                    e.preventDefault();
                }
            });
        }

        console.log('Form enhancements initialized');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeForm);
    } else {
        initializeForm();
    }

})();