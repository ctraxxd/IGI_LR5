/**
 * Museum Form Validation
 * Client-side validation for forms
 */

document.addEventListener('DOMContentLoaded', function() {
    // Phone validation regex for +375 (XX) XXX-XX-XX format
    const phoneRegex = /^\+375\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}$/;
    
    // Initialize all forms
    initClientForm();
    initTicketForm();
    initReviewForm();
    initExhibitForm();
    initTourForm();
});

/**
 * Client/Registration Form Validation
 */
function initClientForm() {
    const forms = document.querySelectorAll('form[id*="client"], form[id*="register"]');
    
    forms.forEach(form => {
        const phoneInput = form.querySelector('input[name="phone"]');
        const emailInput = form.querySelector('input[name="email"]');
        const dobInput = form.querySelector('input[name="date_of_birth"]');
        
        if (phoneInput) {
            phoneInput.addEventListener('blur', function() {
                const value = this.value.trim();
                if (!phoneRegex.test(value)) {
                    showFieldError(this, 'Phone must be in format: +375 (XX) XXX-XX-XX');
                } else {
                    clearFieldError(this);
                }
            });
            
            // Auto-format phone as user types
            phoneInput.addEventListener('input', function(e) {
                let value = this.value.replace(/\D/g, '');
                if (value.startsWith('375')) {
                    value = value.substring(3);
                }
                if (value.length > 0) {
                    let formatted = '+375';
                    if (value.length >= 2) {
                        formatted += ` (${value.substring(0, 2)}`;
                    } else {
                        formatted += ` (${value}`;
                    }
                    if (value.length >= 5) {
                        formatted += `) ${value.substring(2, 5)}`;
                    } else if (value.length > 2) {
                        formatted += `) ${value.substring(2)}`;
                    }
                    if (value.length >= 7) {
                        formatted += `-${value.substring(5, 7)}`;
                    }
                    if (value.length >= 9) {
                        formatted += `-${value.substring(7, 9)}`;
                    }
                    this.value = formatted;
                } else {
                    this.value = '+375';
                }
            });
        }
        
        if (emailInput) {
            emailInput.addEventListener('blur', function() {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(this.value)) {
                    showFieldError(this, 'Please enter a valid email address');
                } else {
                    clearFieldError(this);
                }
            });
        }
        
        if (dobInput) {
            dobInput.addEventListener('blur', function() {
                const birthDate = new Date(this.value);
                const today = new Date();
                let age = today.getFullYear() - birthDate.getFullYear();
                const monthDiff = today.getMonth() - birthDate.getMonth();
                if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                    age--;
                }
                
                if (age < 18) {
                    showFieldError(this, 'You must be at least 18 years old');
                } else {
                    clearFieldError(this);
                }
            });
        }
    });
}

/**
 * Ticket Form Validation
 */
function initTicketForm() {
    const forms = document.querySelectorAll('form[id*="ticket"]');
    
    forms.forEach(form => {
        const visitDateInput = form.querySelector('input[name="visit_date"]');
        
        if (visitDateInput) {
            visitDateInput.addEventListener('blur', function() {
                const selectedDate = new Date(this.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate < today) {
                    showFieldError(this, 'Visit date cannot be in the past');
                } else {
                    clearFieldError(this);
                }
            });
            
            // Set minimum date to today
            const today = new Date().toISOString().split('T')[0];
            visitDateInput.setAttribute('min', today);
        }
    });
}

/**
 * Review Form Validation
 */
function initReviewForm() {
    const forms = document.querySelectorAll('form[id*="review"]');
    
    forms.forEach(form => {
        const ratingSelect = form.querySelector('select[name="rating"]');
        const textInput = form.querySelector('textarea[name="text"]');
        
        if (ratingSelect) {
            ratingSelect.addEventListener('change', function() {
                const rating = parseInt(this.value);
                if (rating < 1 || rating > 5) {
                    showFieldError(this, 'Rating must be between 1 and 5');
                } else {
                    clearFieldError(this);
                }
            });
        }
        
        if (textInput) {
            textInput.addEventListener('blur', function() {
                if (this.value.trim().length < 10) {
                    showFieldError(this, 'Review must be at least 10 characters');
                } else {
                    clearFieldError(this);
                }
            });
        }
    });
}

/**
 * Exhibit Form Validation
 */
function initExhibitForm() {
    const forms = document.querySelectorAll('form[id*="exhibit"]');
    
    forms.forEach(form => {
        const yearInput = form.querySelector('input[name="year_created"]');
        const nameInput = form.querySelector('input[name="name"]');
        
        if (yearInput) {
            yearInput.addEventListener('blur', function() {
                const year = parseInt(this.value);
                const currentYear = new Date().getFullYear();
                
                if (year < 0 || year > currentYear) {
                    showFieldError(this, 'Year must be between 0 and current year');
                } else {
                    clearFieldError(this);
                }
            });
        }
        
        if (nameInput) {
            nameInput.addEventListener('blur', function() {
                if (this.value.trim().length < 2) {
                    showFieldError(this, 'Name must be at least 2 characters');
                } else {
                    clearFieldError(this);
                }
            });
        }
    });
}

/**
 * Tour Form Validation
 */
function initTourForm() {
    const forms = document.querySelectorAll('form[id*="tour"]');
    
    forms.forEach(form => {
        const groupSizeInput = form.querySelector('input[name="group_size"]');
        const priceInput = form.querySelector('input[name="price"]');
        
        if (groupSizeInput) {
            groupSizeInput.addEventListener('blur', function() {
                const size = parseInt(this.value);
                if (size < 1 || size > 50) {
                    showFieldError(this, 'Group size must be between 1 and 50');
                } else {
                    clearFieldError(this);
                }
            });
        }
        
        if (priceInput) {
            priceInput.addEventListener('blur', function() {
                const price = parseFloat(this.value);
                if (price < 0) {
                    showFieldError(this, 'Price cannot be negative');
                } else {
                    clearFieldError(this);
                }
            });
        }
    });
}

/**
 * Helper Functions
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Form submission validation
 */
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Check all required fields
        form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        // Check phone fields
        form.querySelectorAll('input[name="phone"]').forEach(field => {
            const phoneRegex = /^\+375\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}$/;
            if (!phoneRegex.test(field.value)) {
                showFieldError(field, 'Phone must be in format: +375 (XX) XXX-XX-XX');
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
});
