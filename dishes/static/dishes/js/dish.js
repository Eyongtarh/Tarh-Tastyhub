// static/js/dish.js
document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = window.getCSRFToken ? window.getCSRFToken() : null;

    document.querySelectorAll('.dish-card').forEach(card => {
        const decrementBtn = card.querySelector('.dish-qty-decrement');
        const incrementBtn = card.querySelector('.dish-qty-increment');
        const qtyInput = card.querySelector('.dish-qty');
        const addBtn = card.querySelector('.add-to-bag');

        if (!decrementBtn || !incrementBtn || !qtyInput || !addBtn) return;

        // Increment / Decrement
        incrementBtn.addEventListener('click', () => qtyInput.value = parseInt(qtyInput.value) + 1);
        decrementBtn.addEventListener('click', () => {
            const val = parseInt(qtyInput.value);
            if (val > 1) qtyInput.value = val - 1;
        });

        // Add to Bag
        addBtn.addEventListener('click', () => {
            const portionId = addBtn.dataset.portionId;
            if (!portionId) return alert("This dish has no available portions!");
            const quantity = parseInt(qtyInput.value) || 1;

            fetch(`/bag/add/${portionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `quantity=${quantity}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.querySelectorAll('.bag-count').forEach(el => el.textContent = data.bag_count);
                    const event = new CustomEvent("dishAdded", { detail: { card } });
                    document.dispatchEvent(event);
                } else console.error("Failed to add to bag", data);
            })
            .catch(err => console.error("Fetch error:", err));
        });
    });
});
