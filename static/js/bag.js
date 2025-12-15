if (!window.showToast) {
    // Safe global toast function
    window.showToast = (message, type = 'success') => {
        let toast = document.querySelector('#notification-toast');

        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'notification-toast';
            toast.style.position = 'fixed';
            toast.style.top = '20px';
            toast.style.right = '20px';
            toast.style.padding = '12px 16px';
            toast.style.borderRadius = '6px';
            toast.style.fontSize = '0.95rem';
            toast.style.zIndex = '9999';
            toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            document.body.appendChild(toast);
        }

        toast.textContent = message;
        toast.className = '';
        toast.classList.add(type);
        toast.classList.add('show');
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';

        setTimeout(() => {
            toast.classList.remove('show');
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-20px)';
        }, 3000);
    };
}

if (window.dishBagJSLoaded) {
    console.log("dish_bag.js already loaded — skipping.");
} else {
    window.dishBagJSLoaded = true;

    document.addEventListener('DOMContentLoaded', () => {
        const csrftoken = window.getCSRFToken ? window.getCSRFToken() : null;

        // Update bag UI
        const updateBagUI = (data, input = null) => {
            if (!data) return;

            const subtotalEl = document.querySelector('#bag-subtotal');
            if (subtotalEl) subtotalEl.textContent = `$${parseFloat(data.subtotal).toFixed(2)}`;

            const deliveryEl = document.querySelector('#bag-delivery');
            if (deliveryEl) deliveryEl.textContent = data.delivery_fee_display || `$${parseFloat(data.delivery_fee).toFixed(2)}`;

            const grandTotalEl = document.querySelector('#grand-total');
            if (grandTotalEl) grandTotalEl.textContent = `$${parseFloat(data.grand_total).toFixed(2)}`;

            document.querySelectorAll('.bag-count').forEach(el => el.textContent = data.bag_count);

            if (input) {
                const card = input.closest('.card-body, .bag-item, .col-md-6');
                if (!card) return;
                const lineTotalEl = card.querySelector('.line-total');
                if (lineTotalEl) lineTotalEl.innerHTML = `Total: <strong>$${parseFloat(data.line_total).toFixed(2)}</strong>`;
            }
        };

        // POST helper
        const postData = async (url, data) => {
            const headers = { 'X-Requested-With': 'XMLHttpRequest' };
            if (csrftoken) headers['X-CSRFToken'] = csrftoken;
            const body = data instanceof URLSearchParams ? data : new URLSearchParams(data || {});
            const res = await fetch(url, { method: 'POST', headers, body });
            return res.json();
        };

        // Handle quantity change
        const handleQuantityChange = async (input, increment = 0) => {
            if (!input) return;

            const card = input.closest('.dish-card, .card, .col-md-6');
            const portionSelect = card?.querySelector('.portion-select');
            const portionId = portionSelect ? portionSelect.value : input.dataset.portionId;
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
                    window.showToast && window.showToast('Item removed!', 'warning');
                }
            } catch (err) {
                console.error('Bag update error:', err);
                window.showToast && window.showToast('Failed to update item!', 'danger');
            }
        };

        // Quantity buttons
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

        // Add to bag
        document.querySelectorAll('.add-to-bag, #add-dish-to-bag').forEach(btn => {
            btn.addEventListener('click', async () => {
                const card = btn.closest('.dish-card, .card, .col-md-6');
                const input = card?.querySelector('.dish-qty') || { value: 1 };
                const quantity = parseInt(input.value) || 1;

                const portionSelect = card?.querySelector('.portion-select');
                const portionId = portionSelect ? portionSelect.value : (btn.dataset.portionId || btn.dataset.id);
                if (!portionId) return;

                try {
                    const data = await postData(`/bag/add/${portionId}/`, new URLSearchParams({ quantity }));
                    if (!data || !data.success) return;

                    updateBagUI(data, input);

                    if (card) document.dispatchEvent(new CustomEvent('dishAdded', { detail: { card } }));

                    window.showToast && window.showToast('Added to bag!', 'success');
                } catch (err) {
                    console.error('Add to bag error:', err);
                    window.showToast && window.showToast('Failed to add to bag!', 'danger');
                }
            });
        });

        // Remove from bag
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
                    window.showToast && window.showToast('Removed from bag!', 'warning');
                } catch (err) {
                    console.error('Remove from bag error:', err);
                    window.showToast && window.showToast('Failed to remove item!', 'danger');
                }
            });
        });
    });
}
