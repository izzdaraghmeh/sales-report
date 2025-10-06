// Sales Report App JavaScript Functions

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize print functionality
    initializePrint();
    
    // Initialize auto-save
    initializeAutoSave();
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize animations
function initializeAnimations() {
    // Fade in animation for cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
    
    // Intersection Observer for timeline items
    const timelineItems = document.querySelectorAll('.timeline-item');
    if (timelineItems.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        
        timelineItems.forEach(item => {
            observer.observe(item);
        });
    }
}

// Initialize form enhancements
function initializeFormEnhancements() {
    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', formatPhoneNumber);
        input.addEventListener('keypress', validatePhoneInput);
    });
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', autoResizeTextarea);
        // Initial resize
        autoResizeTextarea.call(textarea);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
}

// Phone number formatting function
function formatPhoneNumber() {
    let value = this.value.replace(/\D/g, '');
    
    // Limit length based on Palestinian phone format
    if (value.length > 10) {
        value = value.substring(0, 10);
    }
    
    this.value = value;
    
    // Add visual feedback
    if (value.length >= 9) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
    } else if (value.length > 0) {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
    } else {
        this.classList.remove('is-valid', 'is-invalid');
    }
}

// Validate phone input (only numbers)
function validatePhoneInput(e) {
    const char = String.fromCharCode(e.which);
    if (!/[0-9]/.test(char)) {
        e.preventDefault();
    }
}

// Auto-resize textarea
function autoResizeTextarea() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
}

// Form validation
function validateForm(e) {
    const form = e.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });
    
    if (!isValid) {
        e.preventDefault();
        showAlert('يرجى ملء جميع الحقول المطلوبة', 'danger');
        
        // Focus on first invalid field
        const firstInvalid = form.querySelector('.is-invalid');
        if (firstInvalid) {
            firstInvalid.focus();
        }
    }
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        // Add search suggestions (if needed)
        searchInput.addEventListener('input', debounce(handleSearchInput, 300));
        
        // Handle search form submission
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', handleSearchSubmit);
        }
    }
}

// Handle search input
function handleSearchInput() {
    const query = this.value.trim();
    if (query.length >= 2) {
        // Could implement live search suggestions here
        console.log('Searching for:', query);
    }
}

// Handle search form submission
function handleSearchSubmit(e) {
    const input = e.target.querySelector('input[name="q"]');
    if (!input.value.trim()) {
        e.preventDefault();
        showAlert('يرجى إدخال كلمة البحث', 'warning');
        input.focus();
    }
}

// Initialize print functionality
function initializePrint() {
    // Add print styles dynamically
    const printButtons = document.querySelectorAll('[onclick*="print"]');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            handlePrint();
        });
    });
}

// Handle print functionality
function handlePrint() {
    // Add print-specific classes
    document.body.classList.add('printing');
    
    // Print after a short delay to allow styles to apply
    setTimeout(() => {
        window.print();
        document.body.classList.remove('printing');
    }, 100);
}

// Initialize auto-save functionality
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[id]');
    forms.forEach(form => {
        const formId = form.id;
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                saveFormData(formId, form);
            });
        });
        
        // Load saved data on page load
        loadFormData(formId, form);
    });
}

// Save form data to localStorage
function saveFormData(formId, form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    localStorage.setItem(`formData_${formId}`, JSON.stringify(data));
}

// Load form data from localStorage
function loadFormData(formId, form) {
    const savedData = localStorage.getItem(`formData_${formId}`);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && data[key]) {
                    input.value = data[key];
                }
            });
        } catch (e) {
            console.log('Could not load saved form data');
        }
    }
}

// Clear saved form data
function clearFormData(formId) {
    localStorage.removeItem(`formData_${formId}`);
}

// Utility function: Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main container
    const mainContainer = document.querySelector('main.container-fluid');
    if (mainContainer) {
        mainContainer.insertBefore(alertContainer, mainContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
}

// Get alert icon based on type
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Confirm action
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'غير محدد';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-PS', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// Format datetime for display
function formatDateTime(dateString) {
    if (!dateString) return 'غير محدد';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-PS', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('تم نسخ النص', 'success');
    }).catch(() => {
        showAlert('فشل في نسخ النص', 'danger');
    });
}

// Export data as CSV (placeholder function)
function exportToCSV(data, filename) {
    // This would implement CSV export functionality
    console.log('Exporting to CSV:', filename);
    showAlert('ميزة التصدير ستكون متاحة قريباً', 'info');
}

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Loading state management
function showLoading(element) {
    if (element) {
        element.innerHTML = '<span class="loading"></span> جاري التحميل...';
        element.disabled = true;
    }
}

function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// Local storage helpers
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Could not save to localStorage:', e);
        }
    },
    
    get: function(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Could not read from localStorage:', e);
            return null;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Could not remove from localStorage:', e);
        }
    }
};

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showAlert('حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.', 'danger');
});

// Prevent form resubmission on page refresh
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

