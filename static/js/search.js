document.addEventListener('DOMContentLoaded', () => {

    const searchInput = document.getElementById('search-input');
    const searchForm = document.getElementById('search-form');

    if (searchInput && searchForm) {
        searchInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchForm.submit();
            }
        });
    }

    document.querySelectorAll('.portion-select').forEach(select => {
        select.addEventListener('change', () => {
            const card = select.closest('.card-body');
            if (!card) return;

            const qtyInput = card.querySelector('.dish-qty');
            const priceEl = card.querySelector('.dish-price');

            if (!qtyInput || !priceEl) return;

            const price = parseFloat(
                select.options[select.selectedIndex].dataset.price || 0
            );

            const qty = parseInt(qtyInput.value, 10) || 1;
            priceEl.textContent = `$${(price * qty).toFixed(2)}`;

            qtyInput.dataset.portionId = select.value;
        });
    });

});
