// Blog Site JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initializeImagePreview();
    initializeFormValidation();
    initializeAnimations();
    initializeTooltips();
    initializeAutoSave();
});

// Image Preview Functionality
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            previewImage(this);
        });
    });
}

function previewImage(input) {
    const preview = document.getElementById('preview');
    const previewDiv = document.getElementById('imagePreview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        const file = input.files[0];
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('File size must be less than 5MB');
            input.value = '';
            if (previewDiv) previewDiv.style.display = 'none';
            return;
        }
        
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            alert('Please select a valid image file (JPEG, PNG, GIF, WebP)');
            input.value = '';
            if (previewDiv) previewDiv.style.display = 'none';
            return;
        }
        
        reader.onload = function(e) {
            if (preview && previewDiv) {
                preview.src = e.target.result;
                previewDiv.style.display = 'block';
                previewDiv.classList.add('fade-in');
            }
        }
        
        reader.readAsDataURL(file);
    } else {
        if (previewDiv) {
            previewDiv.style.display = 'none';
        }
    }
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
                
                // Re-enable button after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validate title length
    const titleField = form.querySelector('input[name="title"]');
    if (titleField && titleField.value.length > 200) {
        showFieldError(titleField, 'Title must be less than 200 characters');
        isValid = false;
    }
    
    // Validate content length
    const contentField = form.querySelector('textarea[name="content"]');
    if (contentField && contentField.value.length < 10) {
        showFieldError(contentField, 'Content must be at least 10 characters long');
        isValid = false;
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Animation Effects
function initializeAnimations() {
    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize Bootstrap Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-save functionality for admin forms
function initializeAutoSave() {
    const adminForms = document.querySelectorAll('form[action*="admin"]');
    
    adminForms.forEach(form => {
        const titleField = form.querySelector('input[name="title"]');
        const contentField = form.querySelector('textarea[name="content"]');
        
        if (titleField && contentField) {
            const autoSaveKey = `blog_autosave_${window.location.pathname}`;
            
            // Load saved data
            loadAutoSaveData(titleField, contentField, autoSaveKey);
            
            // Save data on input
            let saveTimeout;
            [titleField, contentField].forEach(field => {
                field.addEventListener('input', function() {
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(() => {
                        saveAutoSaveData(titleField, contentField, autoSaveKey);
                    }, 1000);
                });
            });
            
            // Clear auto-save on successful submission
            form.addEventListener('submit', function() {
                clearAutoSaveData(autoSaveKey);
            });
        }
    });
}

function saveAutoSaveData(titleField, contentField, key) {
    const data = {
        title: titleField.value,
        content: contentField.value,
        timestamp: Date.now()
    };
    
    try {
        localStorage.setItem(key, JSON.stringify(data));
        showAutoSaveIndicator('saved');
    } catch (e) {
        console.warn('Auto-save failed:', e);
    }
}

function loadAutoSaveData(titleField, contentField, key) {
    try {
        const saved = localStorage.getItem(key);
        if (saved) {
            const data = JSON.parse(saved);
            
            // Only load if data is less than 24 hours old
            if (Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
                if (!titleField.value && data.title) {
                    titleField.value = data.title;
                }
                if (!contentField.value && data.content) {
                    contentField.value = data.content;
                }
                
                if (data.title || data.content) {
                    showAutoSaveIndicator('loaded');
                }
            } else {
                localStorage.removeItem(key);
            }
        }
    } catch (e) {
        console.warn('Auto-save load failed:', e);
    }
}

function clearAutoSaveData(key) {
    try {
        localStorage.removeItem(key);
    } catch (e) {
        console.warn('Auto-save clear failed:', e);
    }
}

function showAutoSaveIndicator(type) {
    const indicator = document.getElementById('autosave-indicator') || createAutoSaveIndicator();
    
    if (type === 'saved') {
        indicator.innerHTML = '<i class="fas fa-check text-success"></i> Auto-saved';
        indicator.className = 'alert alert-success py-1 px-2 small position-fixed';
    } else if (type === 'loaded') {
        indicator.innerHTML = '<i class="fas fa-info-circle text-info"></i> Draft restored';
        indicator.className = 'alert alert-info py-1 px-2 small position-fixed';
    }
    
    indicator.style.top = '20px';
    indicator.style.right = '20px';
    indicator.style.zIndex = '9999';
    indicator.style.display = 'block';
    
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 3000);
}

function createAutoSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'autosave-indicator';
    indicator.style.display = 'none';
    document.body.appendChild(indicator);
    return indicator;
}

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function truncateText(text, maxLength = 150) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// Keyboard Shortcuts for Admin
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save forms
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        const form = document.querySelector('form[method="POST"]');
        if (form && window.location.pathname.includes('admin')) {
            e.preventDefault();
            form.submit();
        }
    }
    
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.querySelector('form[method="POST"]');
        if (form && window.location.pathname.includes('admin')) {
            e.preventDefault();
            form.submit();
        }
    }
});

// Dark Mode Toggle (Optional)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
}

// Load dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Error handling for images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBmb3VuZDwvdGV4dD48L3N2Zz4=';
        e.target.alt = 'Image not found';
    }
}, true);