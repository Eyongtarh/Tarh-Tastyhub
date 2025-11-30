if (window.dishBagJSLoaded) {
    console.log("dish_bag.js already loaded — skipping.");
} else {
    window.dishBagJSLoaded = true;

    document.addEventListener('DOMContentLoaded', () => {
        const csrftoken = window.getCSRFToken ? window.getCSRFToken() : null;

        const updateBagUI = (data, input=null) => {
            if (!data) return;

            // Update subtotal, delivery, grand total
            const subtotalEl = document.querySelector('#bag-subtotal');
            if (subtotalEl) subtotalEl.textContent = `₦${data.subtotal}`;

            const deliveryEl = document.querySelector('#bag-delivery');
            if (deliveryEl) deliveryEl.textContent = `₦${data.delivery_fee}`;

            const grandTotalEl = document.querySelector('#grand-total');
            if (grandTotalEl) grandTotalEl.textContent = `₦${data.grand_total}`;

            // Update bag count
            document.querySelectorAll('.bag-count').forEach(el => el.textContent = data.bag_count);

            // Update line total if input provided
            if (input) {
                const card = input.closest('.card-body, .bag-item, .col-md-6');
                if (!card) return;
                const lineTotalEl = card.querySelector('.line-total');
                if (lineTotalEl) lineTotalEl.innerHTML = `Total: <strong>₦${data.line_total}</strong>`;
            }
        };

        const postData = async (url, data) => {
            const headers = { 'X-Requested-With': 'XMLHttpRequest' };
            if (csrftoken) headers['X-CSRFToken'] = csrftoken;
            const body = data instanceof URLSearchParams ? data : new URLSearchParams(data || {});
            const res = await fetch(url, { method: 'POST', headers, body });
            return res.json();
        };

        const handleQuantityChange = async (input, increment=0) => {
            if (!input) return;
            const portionId = input.dataset.portionId || input.dataset.id;
            if (!portionId) return;

            let qty = parseInt(input.value) || 1;
            qty += increment;
            if (qty < 0) qty = 0;
            input.value = qty;

            const url = qty === 0 ? `/bag/remove/${portionId}/` : `/bag/adjust/${portionId}/`;

            try {
                const data = await postData(url, new URLSearchParams({ quantity: qty }));
                if (!data || !data.success) return;

                updateBagUI(data, input);

                if (qty === 0) {
                    const cardCol = input.closest('.col, .bag-item');
                    if (cardCol) cardCol.remove();
                }
            } catch (err) {
                console.error('Bag update error:', err);
            }
        };

        // --- Quantity buttons ---
        document.querySelectorAll('.dish-qty-increment, .bag-qty-increment').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = btn.closest('.card-body, .bag-item, .col-md-6')?.querySelector('.dish-qty');
                handleQuantityChange(input, 1);
            });
        });

        document.querySelectorAll('.dish-qty-decrement, .bag-qty-decrement').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = btn.closest('.card-body, .bag-item, .col-md-6')?.querySelector('.dish-qty');
                handleQuantityChange(input, -1);
            });
        });

        document.querySelectorAll('.dish-qty').forEach(input => {
            input.addEventListener('change', () => handleQuantityChange(input, 0));
        });

        // --- Add to Bag ---
        document.querySelectorAll('.add-to-bag, #add-dish-to-bag').forEach(btn => {
            btn.addEventListener('click', async () => {
                const card = btn.closest('.dish-card, .card, .col-md-6');
                const input = card?.querySelector('.dish-qty') || { value: 1 };
                const quantity = parseInt(input.value) || 1;
                const portionId = btn.dataset.portionId || btn.dataset.id;
                if (!portionId) return;

                try {
                    const data = await postData(`/bag/add/${portionId}/`, new URLSearchParams({ quantity }));
                    if (!data || !data.success) return;

                    updateBagUI(data, input);

                    if (card) document.dispatchEvent(new CustomEvent('dishAdded', { detail: { card } }));
                    if (window.showToast) window.showToast('Added to bag!', 'success');
                } catch (err) {
                    console.error('Add to bag error:', err);
                }
            });
        });

        // --- Remove from Bag ---
        document.querySelectorAll('.remove-from-bag').forEach(btn => {
            btn.addEventListener('click', async () => {
                const portionId = btn.dataset.portionId || btn.dataset.id;
                if (!portionId) return;

                try {
                    const data = await postData(`/bag/remove/${portionId}/`);
                    if (!data || !data.success) return;

                    updateBagUI(data);

                    const cardCol = btn.closest('.col, .bag-item');
                    if (cardCol) cardCol.remove();
                } catch (err) {
                    console.error('Remove from bag error:', err);
                }
            });
        });
    });
}
