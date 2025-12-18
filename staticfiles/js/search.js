
document.addEventListener('DOMContentLoaded', () => {

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

    document.querySelectorAll('.portion-select').forEach(select => {
        select.addEventListener('change', () => {
            const card = select.closest('.card-body');
            const qtyInput = card.querySelector('.dish-qty');
            const priceEl = card.querySelector('.dish-price');

            const price = parseFloat(
                select.options[select.selectedIndex].textContent.split('- $')[1]
            ) || 0;

            const qty = parseInt(qtyInput.value) || 1;

            priceEl.textContent = `$${(price * qty).toFixed(2)}`;

            qtyInput.dataset.portionId = select.value;
        });
    });

});
