document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.add-to-bag').forEach(btn => {
        btn.addEventListener('click', () => {
            const card = btn.closest('.card');
            if (!card) return;

            const img = card.querySelector('img');
            if (!img) return;

            const clone = img.cloneNode(true);
            clone.id = 'flying-image';
            clone.style.position = 'fixed';
            clone.style.zIndex = 1000;
            clone.style.pointerEvents = 'none';

            const rect = img.getBoundingClientRect();
            clone.style.top = `${rect.top}px`;
            clone.style.left = `${rect.left}px`;
            clone.style.width = `${rect.width}px`;
            clone.style.height = `${rect.height}px`;
            clone.style.transition = 'transform 0.8s cubic-bezier(0.65, 0, 0.35, 1), opacity 0.6s';

            document.body.appendChild(clone);

            const targetEl = document.querySelector('#bag-count') || document.querySelector('.bag-count');
            if (!targetEl) return setTimeout(() => clone.remove(), 900);

            const target = targetEl.getBoundingClientRect();

            setTimeout(() => {
                const translateX = (target.left + target.width / 2) - (rect.left + rect.width / 2);
                const translateY = (target.top + target.height / 2) - (rect.top + rect.height / 2);
                clone.style.transform = `translate(${translateX}px, ${translateY}px) scale(0.15)`;
                clone.style.opacity = '0.8';
            }, 20);

            clone.addEventListener('transitionend', () => clone.remove());
        });
    });
});
