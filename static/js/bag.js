if (window.dishBagJSLoaded) {
    console.log("dish_bag.js already loaded — skipping.");
} else {
    window.dishBagJSLoaded = true;

    document.addEventListener('DOMContentLoaded', () => {
        const csrftoken = window.getCSRFToken ? window.getCSRFToken() : null;

        // Update bag UI
        const updateBagUI = (data, input = null) => {
            if (!data) {
                window.showToast && window.showToast('No bag data available.', 'warning');
                return;
            }

            const subtotalEl = document.querySelector('#bag-subtotal');
            if (subtotalEl) subtotalEl.textContent = `$${parseFloat(data.subtotal).toFixed(2)}`;

            const deliveryEl = document.querySelector('#bag-delivery');
            if (deliveryEl) deliveryEl.textContent = data.delivery_fee_display || `$${parseFloat(data.delivery_fee).toFixed(2)}`;

            const grandTotalEl = document.querySelector('#grand-total');
            if (grandTotalEl) grandTotalEl.textContent = `$${parseFloat(data.grand_total).toFixed(2)}`;

            document.querySelectorAll('.bag-count').forEach(el => el.textContent = data.bag_count);

            if (data.bag_count === 0) {
                window.showToast && window.showToast('Your bag is empty.', 'info');
            }

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
            if (!res.ok) throw new Error(`Server responded with status ${res.status}`);
            return res.json();
        };

        // Validate quantity input
        const validateQuantity = (value) => {
            const qty = parseInt(value);
            if (isNaN(qty) || qty < 0) return 0;
            if (qty > 99) return 99; // maximum allowed
            return qty;
        };

        // Handle quantity change
        const handleQuantityChange = async (input, increment = 0) => {
            if (!input) {
                window.showToast && window.showToast('Quantity input not found!', 'danger');
                return;
            }

            const card = input.closest('.dish-card, .card, .col-md-6');
            const portionSelect = card?.querySelector('.portion-select');
            const portionId = portionSelect ? portionSelect.value : input.dataset.portionId;
            if (!portionId) {
                window.showToast && window.showToast('Item not found in bag.', 'warning');
                return;
            }

            let qty = validateQuantity(parseInt(input.value) || 1);
            qty += increment;
            qty = validateQuantity(qty);
            input.value = qty;

            if (qty === 0 && !window.confirm('Are you sure you want to remove this item?')) return;

            const url = qty === 0 ? `/bag/remove/${portionId}/` : `/bag/adjust/${portionId}/`;

            try {
                const data = await postData(url, new URLSearchParams({ quantity: qty }));
                if (!data || !data.success) {
                    window.showToast && window.showToast('Unable to update bag. Try again!', 'danger');
                    return;
                }

                updateBagUI(data, input);

                if (qty === 0) {
                    const cardCol = input.closest('.col, .bag-item');
                    if (cardCol) cardCol.remove();
                    window.showToast && window.showToast('Item removed from bag.', 'warning');
                } else if (increment !== 0) {
                    window.showToast && window.showToast('Quantity updated.', 'info');
                }
            } catch (err) {
                console.error('Bag update error:', err);
                window.showToast && window.showToast('Failed to update item!', 'danger');
            }
        };

        // Quantity buttons with messages
        document.querySelectorAll('.dish-qty-increment, .bag-qty-increment').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = btn.closest('.card-body, .bag-item, .col-md-6')?.querySelector('.dish-qty');
                if (!input) {
                    window.showToast && window.showToast('No quantity input found!', 'danger');
                    return;
                }
                const currentQty = parseInt(input.value) || 0;
                if (currentQty >= 99) {
                    window.showToast && window.showToast('Maximum quantity reached.', 'warning');
                    return;
                }
                handleQuantityChange(input, 1);
            });
        });

        document.querySelectorAll('.dish-qty-decrement, .bag-qty-decrement').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = btn.closest('.card-body, .bag-item, .col-md-6')?.querySelector('.dish-qty');
                if (!input) {
                    window.showToast && window.showToast('No quantity input found!', 'danger');
                    return;
                }
                const currentQty = parseInt(input.value) || 0;
                if (currentQty <= 0) {
                    window.showToast && window.showToast('Quantity cannot be less than zero.', 'warning');
                    return;
                }
                handleQuantityChange(input, -1);
            });
        });

        document.querySelectorAll('.dish-qty').forEach(input => {
            input.addEventListener('change', () => {
                const newQty = validateQuantity(input.value);
                if (newQty === 0) {
                    window.showToast && window.showToast('Quantity cannot be zero. Use remove button instead.', 'info');
                }
                input.value = newQty;
                handleQuantityChange(input, 0);
            });
        });

        // Add to bag
        document.querySelectorAll('.add-to-bag, #add-dish-to-bag').forEach(btn => {
            btn.addEventListener('click', async () => {
                const card = btn.closest('.dish-card, .card, .col-md-6');
                const input = card?.querySelector('.dish-qty') || { value: 1 };
                const quantity = validateQuantity(input.value);

                const portionSelect = card?.querySelector('.portion-select');
                const portionId = portionSelect ? portionSelect.value : (btn.dataset.portionId || btn.dataset.id);
                if (!portionId) {
                    window.showToast && window.showToast('Invalid item selection!', 'danger');
                    return;
                }

                try {
                    const data = await postData(`/bag/add/${portionId}/`, new URLSearchParams({ quantity }));
                    if (!data || !data.success) {
                        window.showToast && window.showToast('Item is already in the bag or cannot be added.', 'warning');
                        return;
                    }

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
                if (!portionId) {
                    window.showToast && window.showToast('Invalid item selection!', 'danger');
                    return;
                }

                try {
                    const data = await postData(`/bag/remove/${portionId}/`);
                    if (!data || !data.success) {
                        window.showToast && window.showToast('Unable to remove item.', 'danger');
                        return;
                    }

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
