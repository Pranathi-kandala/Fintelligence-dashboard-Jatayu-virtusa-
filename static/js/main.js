/**
 * Fintelligence - Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Add loader for form submissions
    setupFormLoaders();
    
    // Format currency values
    formatCurrencyValues();
    
    // Enable nl2br filter for elements with class 'nl2br'
    applyNl2br();
});

/**
 * Add loading indicators to forms
 */
function setupFormLoaders() {
    const forms = document.querySelectorAll('form:not(.no-loader)');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Don't add loader for forms with AJAX handling
            if (this.hasAttribute('data-ajax')) {
                return;
            }
            
            // Find submit button
            const submitButton = this.querySelector('button[type="submit"]');
            
            if (submitButton) {
                // Save original button content
                submitButton.setAttribute('data-original-content', submitButton.innerHTML);
                
                // Replace with loading spinner
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
            }
            
            // Create full page loading overlay for transitions
            if (this.hasAttribute('data-loading-overlay')) {
                const overlay = document.createElement('div');
                overlay.className = 'loading-overlay';
                overlay.innerHTML = '<div class="spinner-border text-primary loading-spinner" role="status"><span class="visually-hidden">Loading...</span></div>';
                document.body.appendChild(overlay);
                
                // Store reference to overlay on form
                this.loadingOverlay = overlay;
            }
        });
    });
}

/**
 * Format currency values to include commas for thousands separators
 */
function formatCurrencyValues() {
    const currencyElements = document.querySelectorAll('.format-currency');
    
    currencyElements.forEach(element => {
        const value = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ''));
        
        if (!isNaN(value)) {
            element.textContent = '$' + value.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    });
}

/**
 * Convert newlines to <br> tags in elements with class 'nl2br'
 */
function applyNl2br() {
    const elements = document.querySelectorAll('.nl2br');
    
    elements.forEach(element => {
        element.innerHTML = element.textContent.replace(/\n/g, '<br>');
    });
}

/**
 * Show an alert message to the user
 * @param {string} message - The message to display
 * @param {string} type - The alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

/**
 * Create an alert container if it doesn't exist
 * @returns {HTMLElement} The alert container element
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    
    document.body.appendChild(container);
    return container;
}

/**
 * Format percentage values with the % symbol
 * @param {number} value - The percentage value to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value, decimals = 2) {
    return value.toFixed(decimals) + '%';
}

/**
 * Format a date string to a readable format
 * @param {string} dateStr - Date string in ISO format
 * @returns {string} Formatted date string
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
