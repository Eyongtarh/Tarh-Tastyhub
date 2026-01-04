/* jshint esversion: 11 */
/* global bootstrap */
/*
   CSRF cookie getter
*/
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
/* 
   Unified Toast Handler
*/
window.showToast = function(message, variant = 'info', timeout = 5000) {
    const variants = {
        success: { bg: '#4e62df', color: '#ffffff' },
        info:    { bg: '#0dcaf0', color: '#000000' },
        warning: { bg: '#ffc107', color: '#000000' },
        danger:  { bg: '#dc3545', color: '#ffffff' }
    };
    const v = variants[variant] || variants.info;

    try {
        const container = document.getElementById('toast-container');

        if (container && window.bootstrap?.Toast) {
            const el = document.createElement('div');
            el.className = `toast border-0 mb-2`;
            el.role = 'alert';
            el.style.backgroundColor = v.bg;
            el.style.color = v.color;

            el.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>`;
            container.appendChild(el);

            const bsToast = new bootstrap.Toast(el);
            bsToast.show();

            if (timeout > 0) setTimeout(() => bsToast.hide(), timeout);
            return;
        }
    } catch (e) {
        console.warn('Bootstrap toast failed, using fallback', e);
    }
    simpleToast(message, variant);
};
/*
   Fallback Toast
*/
function simpleToast(message, variant = 'success') {
    const variants = {
        success: { bg: '#4e62df', color: '#ffffff' },
        info:    { bg: '#0dcaf0', color: '#000000' },
        warning: { bg: '#ffc107', color: '#000000' },
        danger:  { bg: '#dc3545', color: '#ffffff' }
    };
    const v = variants[variant] || variants.info;

    let toast = document.getElementById('notification-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'notification-toast';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.className = 'show';
    toast.style.backgroundColor = v.bg;
    toast.style.color = v.color;

    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
    }, 3000);
}