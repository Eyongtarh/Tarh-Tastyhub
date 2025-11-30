// static/js/flying_image.js
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('dishAdded', (e) => {
        const card = e.detail.card;
        const img = card.querySelector('img');
        if (!img) return;

        const clone = img.cloneNode(true);
        clone.style.position = 'fixed';
        clone.style.zIndex = 1000;
        clone.style.pointerEvents = 'none';
        clone.style.transition = 'transform 0.8s cubic-bezier(0.65,0,0.35,1), opacity 0.6s';

        const rect = img.getBoundingClientRect();
        const startTop = rect.top + window.scrollY;
        const startLeft = rect.left + window.scrollX;
        clone.style.top = `${startTop}px`;
        clone.style.left = `${startLeft}px`;
        clone.style.width = `${rect.width}px`;
        clone.style.height = `${rect.height}px`;

        document.body.appendChild(clone);

        const targetEl = document.querySelector('#bag-count') || document.querySelector('.bag-count');
        if (!targetEl) {
            setTimeout(() => clone.remove(), 900);
            return;
        }

        const target = targetEl.getBoundingClientRect();
        const targetTop = target.top + window.scrollY;
        const targetLeft = target.left + window.scrollX;

        requestAnimationFrame(() => {
            const translateX = (targetLeft + target.width/2) - (startLeft + rect.width/2);
            const translateY = (targetTop + target.height/2) - (startTop + rect.height/2);
            clone.style.transform = `translate(${translateX}px, ${translateY}px) scale(0.15)`;
            clone.style.opacity = '0';
        });

        clone.addEventListener('transitionend', () => clone.remove());
    });
});
