// static/js/base.js
// Global helpers used across other scripts

// CSRF cookie getter (standard Django cookie name)
window.getCSRFToken = function(name = 'csrftoken') {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const c = cookies[i].trim();
            if (c.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// Simple toast helper that accepts message and bootstrap variant e.g. 'success', 'warning'
window.showToast = function(message, variant = 'info', timeout = 5000) {
    try {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const el = document.createElement('div');
        el.className = `toast text-bg-${variant} border-0 mb-2`;
        el.role = 'alert';
        el.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>`;
        container.appendChild(el);
        const bsToast = new bootstrap.Toast(el);
        bsToast.show();
        if (timeout > 0) setTimeout(() => bsToast.hide(), timeout);
    } catch (e) {
        console.warn('showToast error', e);
    }
};
