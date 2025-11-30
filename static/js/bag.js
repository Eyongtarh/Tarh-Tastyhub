document.addEventListener('DOMContentLoaded', () => {

    // --- CSRF Helper ---
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

    // --- Update Bag Count ---
    const updateBagCountUI = (count) => {
        document.querySelectorAll('.bag-count').forEach(el => el.textContent = count);
        const desktop = document.getElementById('bag-count');
        if (desktop) desktop.textContent = count;
        const mobile = document.getElementById('bag-count-mobile');
        if (mobile) mobile.textContent = count;
    };

    // --- Animate image to bag ---
    const animateToBag = (imgEl) => {
        if (!imgEl) return;
        const clone = imgEl.cloneNode(true);
        clone.style.position = 'fixed';
        clone.style.zIndex = 9999;
        clone.style.pointerEvents = 'none';
        clone.style.transition = 'transform 0.8s cubic-bezier(0.65,0,0.35,1), opacity 0.6s';
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

        setTimeout(() => clone.remove(), 1000);
    };

    // --- Generic Add to Bag Handler ---
    const addToBag = async (portionId, quantity = 1, imgEl = null) => {
        try {
            const res = await fetch(`/bag/add/${portionId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                body: new URLSearchParams({ quantity: quantity })
            });

            const data = await res.json();
            if (data && data.success) {
                updateBagCountUI(data.bag_count);
                if (imgEl) animateToBag(imgEl);
            } else {
                console.error('Failed to add to bag', data);
            }
        } catch (err) {
            console.error('Error adding to bag:', err);
        }
    };

    // --- Dish List / Dish Detail Add to Bag ---
    document.querySelectorAll('.add-to-bag, #add-dish-to-bag').forEach(btn => {
        if (btn.dataset._bag_init) return;
        btn.dataset._bag_init = '1';

        btn.addEventListener('click', (e) => {
            e.preventDefault();

            let portionId = btn.dataset.portionId || btn.dataset.id;
            if (!portionId) return;

            // Quantity (for dish_detail)
            let qtyInput = document.querySelector('#dish-qty');
            let quantity = qtyInput ? parseInt(qtyInput.value) : 1;

            let card = btn.closest('.card') || document.querySelector('.dish-card');
            let imgEl = card ? card.querySelector('img') : null;

            addToBag(portionId, quantity, imgEl);
        });
    });

    // --- Dish List / Detail Quantity Controls ---
    const incrementBtns = document.querySelectorAll('.dish-qty-increment, #dish-qty-increment');
    const decrementBtns = document.querySelectorAll('.dish-qty-decrement, #dish-qty-decrement');

    incrementBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            let input = btn.closest('.d-flex').querySelector('input[type="number"]');
            input.value = parseInt(input.value) + 1;
        });
    });

    decrementBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            let input = btn.closest('.d-flex').querySelector('input[type="number"]');
            input.value = Math.max(1, parseInt(input.value) - 1);
        });
    });

    // --- Bag Page Quantity Adjustments ---
    document.querySelectorAll('.bag-qty-decrement, .bag-qty-increment').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();

            const cardBody = btn.closest('.card-body');
            const input = cardBody.querySelector('input[name="quantity"]');
            let quantity = parseInt(input.value);

            if (btn.classList.contains('bag-qty-decrement')) quantity = Math.max(0, quantity - 1);
            if (btn.classList.contains('bag-qty-increment')) quantity += 1;
            input.value = quantity;

            const portionBtn = cardBody.querySelector('.add-to-bag') || cardBody.querySelector('form');
            const portionId = portionBtn.dataset.portionId || portionBtn.dataset.id;
            if (!portionId) return;

            const url = quantity === 0 ? `/bag/remove/${portionId}/` : `/bag/adjust/${portionId}/`;

            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    },
                    body: new URLSearchParams({ quantity: quantity })
                });

                const data = await res.json();
                if (!data || !data.success) return;

                updateBagCountUI(data.bag_count);

                // Update line total
                const lineTotalEl = cardBody.querySelector('.line-total');
                if (lineTotalEl && data.line_total !== undefined) {
                    lineTotalEl.textContent = `₦${data.line_total}`;
                }

                // Update grand total
                const grandTotalEl = document.querySelector('#grand-total');
                if (grandTotalEl && data.grand_total !== undefined) {
                    grandTotalEl.textContent = `₦${data.grand_total}`;
                }

            } catch (err) {
                console.error('Error updating bag:', err);
            }
        });
    });

    // --- Bag Remove Buttons ---
    document.querySelectorAll('.remove-from-bag').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const portionId = btn.dataset.portionId;
            if (!portionId) return;

            try {
                const res = await fetch(`/bag/remove/${portionId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    }
                });
                const data = await res.json();
                if (!data || !data.success) return;

                updateBagCountUI(data.bag_count);
                btn.closest('.col').remove();

                // Update grand total
                const grandTotalEl = document.querySelector('#grand-total');
                if (grandTotalEl && data.grand_total !== undefined) {
                    grandTotalEl.textContent = `₦${data.grand_total}`;
                }

            } catch (err) {
                console.error('Error removing from bag:', err);
            }
        });
    });

});
