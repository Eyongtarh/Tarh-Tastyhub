

document.addEventListener('DOMContentLoaded', () => {

    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(cookie => {
                const c = cookie.trim();
                if (c.startsWith(`${name}=`)) {
                    cookieValue = decodeURIComponent(c.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    };
    const csrftoken = getCookie('csrftoken');

    const updateBagCountUI = (count) => {
        document.querySelectorAll('.bag-count').forEach(el => {
            el.textContent = count;
        });
        const desktop = document.getElementById('bag-count');
        if (desktop) desktop.textContent = count;
        const mobile = document.getElementById('bag-count-mobile');
        if (mobile) mobile.textContent = count;
    };

    const animateToBag = (imgEl) => {
        if (!imgEl) return;
        const clone = imgEl.cloneNode(true);
        clone.id = 'flying-image';
        clone.style.position = 'fixed';
        clone.style.zIndex = 9999;
        clone.style.pointerEvents = 'none';
        clone.style.transition = 'transform 0.8s cubic-bezier(0.65, 0, 0.35, 1), opacity 0.6s';
        const rect = imgEl.getBoundingClientRect();
        clone.style.top = `${rect.top}px`;
        clone.style.left = `${rect.left}px`;
        clone.style.width = `${rect.width}px`;
        clone.style.height = `${rect.height}px`;
        clone.style.borderRadius = window.getComputedStyle(imgEl).borderRadius || '8px';
        document.body.appendChild(clone);

        const targetEl = document.querySelector('#bag-count') || document.querySelector('.bag-count') || document.querySelector('#bag-count-mobile');
        if (!targetEl) {
            setTimeout(() => clone.remove(), 900);
            return;
        }
        const target = targetEl.getBoundingClientRect();

        requestAnimationFrame(() => {
            const translateX = (target.left + target.width / 2) - (rect.left + rect.width / 2);
            const translateY = (target.top + target.height / 2) - (rect.top + rect.height / 2);
            clone.style.transform = `translate(${translateX}px, ${translateY}px) scale(0.15)`;
            clone.style.opacity = '0.9';
        });

        const cleanup = () => { if (clone && clone.parentNode) clone.parentNode.removeChild(clone); };
        clone.addEventListener('transitionend', cleanup);
        setTimeout(cleanup, 1000);
    };

    document.querySelectorAll('.add-to-bag').forEach(btn => {
        if (btn.dataset._bag_init) return;
        btn.dataset._bag_init = '1';

        btn.addEventListener('click', async (e) => {
            e.preventDefault();

            const portionId = btn.dataset.portionId || btn.dataset.id || btn.dataset.pk || btn.dataset['id'];
            if (!portionId) {
                console.warn('No portion id found on add-to-bag button');
                return;
            }

            const originalDisabled = btn.disabled;
            btn.disabled = true;
            const card = btn.closest('.card');
            const img = card ? (card.querySelector('img') || card.querySelector('img.card-img-top')) : null;
            try {
                const res = await fetch(`/bag/add/${portionId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    },
                    body: new URLSearchParams({ quantity: 1 })
                });

                const data = await res.json();
                if (!data || !data.success) {
                    console.error('Failed to add to bag', data);
                    btn.disabled = originalDisabled;
                    return;
                }

                updateBagCountUI(data.bag_count);

                if (img) animateToBag(img);

            } catch (err) {
                console.error('Error adding to bag:', err);
            } finally {
                setTimeout(() => { btn.disabled = originalDisabled; }, 400);
            }
        });
    });
});
