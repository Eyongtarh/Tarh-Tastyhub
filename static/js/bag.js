if (window.dishBagJSLoaded) {
    console.log("dish_bag.js already loaded — skipping.");
} else {
    window.dishBagJSLoaded = true;
    document.addEventListener('DOMContentLoaded', () => {
        const MAX_PER_DISH = 20;
        const csrftoken = window.getCSRFToken ? window.getCSRFToken() : null;
        const toast = (msg, type = 'info') => {
            if (window.showToast) window.showToast(msg, type);
        };
        const validateQuantity = (value) => {
            const qty = parseInt(value);
            if (isNaN(qty) || qty < 0) return 0;
            return qty;
        };
        const postData = async (url, data) => {
            const headers = { 'X-Requested-With': 'XMLHttpRequest' };
            if (csrftoken) headers['X-CSRFToken'] = csrftoken;
            const body = data instanceof URLSearchParams
                ? data
                : new URLSearchParams(data || {});
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body,
            });
            let json = {};
            try {
                json = await response.json();
            } catch (_) {}
            if (response.status === 401 || json?.error === 'AUTH_REQUIRED') {
                toast(
                    json.message || 'Please log in or sign up to add items to your bag.',
                    'warning'
                );
                return null;
            }
            return json;
        };
        /*
           Update Bag UI
        */
        const updateBagUI = (data, input = null) => {
            if (!data || data.success === false) return;
            document.querySelectorAll('.bag-count')
                .forEach(el => el.textContent = data.bag_count);
            const subtotalEl = document.querySelector('#bag-subtotal');
            if (subtotalEl) subtotalEl.textContent = `$${parseFloat(data.subtotal).toFixed(2)}`;
            const deliveryEl = document.querySelector('#bag-delivery');
            if (deliveryEl) {
                deliveryEl.textContent =
                    data.delivery_fee_display || `$${parseFloat(data.delivery_fee).toFixed(2)}`;
            }
            const grandTotalEl = document.querySelector('#grand-total');
            if (grandTotalEl) {
                grandTotalEl.textContent = `$${parseFloat(data.grand_total).toFixed(2)}`;
            }
            if (input && data.line_total !== undefined) {
                const card = input.closest('.card-body, .bag-item, .col-md-6');
                const lineTotalEl = card?.querySelector('.line-total');
                if (lineTotalEl) {
                    lineTotalEl.innerHTML =
                        `Total: <strong>$${parseFloat(data.line_total).toFixed(2)}</strong>`;
                }
            }
        };
        /* 
           Quantity Change
        */
        const handleQuantityChange = async (input, increment = 0) => {
            const previousQty = parseInt(input.value) || 0;
            let qty = validateQuantity(previousQty + increment);
            if (qty > MAX_PER_DISH) {
                toast(
                    `You can only order up to ${MAX_PER_DISH} of this dish per day.`,
                    'warning'
                );
                input.value = previousQty;
                return;
            }
            input.value = qty;
            const card = input.closest('.dish-card, .card, .col-md-6');
            const portionSelect = card?.querySelector('.portion-select');
            const portionId = portionSelect ? portionSelect.value : input.dataset.portionId;
            if (!portionId) {
                input.value = previousQty;
                return;
            }
            const url = qty === 0
                ? `/bag/remove/${portionId}/`
                : `/bag/adjust/${portionId}/`;
            const data = await postData(url, { quantity: qty });
            if (!data) {
                input.value = previousQty;
                return;
            }
            if (data.success === false) {
                toast(data.message, 'warning');
                input.value = previousQty;
                return;
            }
            updateBagUI(data, input);
            if (qty === 0) {
                input.closest('.col, .bag-item')?.remove();
                toast('Item removed from bag.', 'warning');
            }
        };
        /* 
           Increment / Decrement buttons
        */
        document.querySelectorAll('.dish-qty-increment, .bag-qty-increment')
            .forEach(btn => {
                btn.addEventListener('click', () => {
                    const input = btn.closest('.card-body, .bag-item, .col-md-6')
                        ?.querySelector('.dish-qty');
                    if (input) handleQuantityChange(input, 1);
                });
            });
        document.querySelectorAll('.dish-qty-decrement, .bag-qty-decrement')
            .forEach(btn => {
                btn.addEventListener('click', () => {
                    const input = btn.closest('.card-body, .bag-item, .col-md-6')
                        ?.querySelector('.dish-qty');
                    if (input) handleQuantityChange(input, -1);
                });
            });
        /* 
           Add to Bag 
        */
        document.querySelectorAll('.add-to-bag, #add-dish-to-bag')
            .forEach(btn => {
                btn.addEventListener('click', async () => {
                    const card = btn.closest('.dish-card, .card, .col-md-6');
                    const input = card?.querySelector('.dish-qty') || { value: 1 };
                    const quantity = validateQuantity(input.value);
                    if (quantity > MAX_PER_DISH) {
                        toast(
                            `You can only order up to ${MAX_PER_DISH} of this dish per day.`,
                            'warning'
                        );
                        return;
                    }
                    const portionSelect = card?.querySelector('.portion-select');
                    const portionId = portionSelect
                        ? portionSelect.value
                        : (btn.dataset.portionId || btn.dataset.id);
                    if (!portionId) return;
                    const data = await postData(
                        `/bag/add/${portionId}/`,
                        { quantity }
                    );
                    if (!data) return;
                    if (data.success === false) {
                        toast(data.message, 'warning');
                        return;
                    }
                    updateBagUI(data, input);
                    toast('Added to bag!', 'success');
                });
            });
        /* 
           Remove from Bag
        */
        document.querySelectorAll('.remove-from-bag')
            .forEach(btn => {
                btn.addEventListener('click', async () => {
                    const portionId = btn.dataset.portionId || btn.dataset.id;
                    if (!portionId) return;
                    const data = await postData(`/bag/remove/${portionId}/`);
                    if (!data) return;
                    updateBagUI(data);
                    btn.closest('.col, .bag-item')?.remove();
                    toast('Removed from bag!', 'warning');
                });
            });
    });
}
