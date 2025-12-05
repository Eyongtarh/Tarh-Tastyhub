/**
 * Handle search form submission and dish quantity/portion updates.
 */
document.addEventListener('DOMContentLoaded', () => {

    // Submit search form on Enter key
    const searchForms = [
        { inputId: 'search-input', formId: 'search-form' },
        { inputId: 'mobile-search-input', formId: 'mobile-search-form' }
    ];

    searchForms.forEach(({ inputId, formId }) => {
        const input = document.getElementById(inputId);
        const form = document.getElementById(formId);
        if (!input || !form) return;

        input.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                e.preventDefault();
                form.submit();
            }
        });
    });

    // Dish portion selector and price updater
    document.querySelectorAll('.portion-select').forEach(select => {
        select.addEventListener('change', () => {
            const card = select.closest('.card-body');
            const qtyInput = card.querySelector('.dish-qty');
            const priceEl = card.querySelector('.dish-price');
            const price = parseFloat(select.options[select.selectedIndex].textContent.split('- $')[1]) || 0;
            const qty = parseInt(qtyInput.value) || 1;
            priceEl.textContent = `$${(price * qty).toFixed(2)}`;
            qtyInput.dataset.portionId = select.value;
        });
    });

    // Quantity increment/decrement buttons
    const updateQty = (btn, increment = true) => {
        const input = btn.parentElement.querySelector('.dish-qty');
        const card = btn.closest('.card-body');
        const priceEl = card.querySelector('.dish-price');
        const select = card.querySelector('.portion-select');
        let qty = parseInt(input.value) || 1;
        qty = increment ? qty + 1 : Math.max(1, qty - 1);
        input.value = qty;

        let price = select ? parseFloat(select.options[select.selectedIndex].textContent.split('- $')[1]) : parseFloat(priceEl.textContent.replace('$',''));
        priceEl.textContent = `$${(price * qty).toFixed(2)}`;
    };

    document.querySelectorAll('.dish-qty-increment').forEach(btn => btn.addEventListener('click', () => updateQty(btn, true)));
    document.querySelectorAll('.dish-qty-decrement').forEach(btn => btn.addEventListener('click', () => updateQty(btn, false)));
});
