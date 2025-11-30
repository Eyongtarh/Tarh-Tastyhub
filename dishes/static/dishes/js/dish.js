
document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".dish-card").forEach(card => {
    const decrementBtn = card.querySelector(".dish-qty-decrement");
    const incrementBtn = card.querySelector(".dish-qty-increment");
    const qtyInput = card.querySelector(".dish-qty");
    const addBtn = card.querySelector(".add-to-bag");

    // Increment
    incrementBtn.addEventListener("click", () => {
      qtyInput.value = parseInt(qtyInput.value) + 1;
    });

    // Decrement
    decrementBtn.addEventListener("click", () => {
      if (parseInt(qtyInput.value) > 1) {
        qtyInput.value = parseInt(qtyInput.value) - 1;
      }
    });

    // Add to Bag
    addBtn.addEventListener("click", () => {
      const portionId = addBtn.dataset.portionId;
      const quantity = parseInt(qtyInput.value);

      fetch(`/bag/add/${portionId}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": "{{ csrf_token }}",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: `quantity=${quantity}`
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert(data.message); // Replace with nicer UI if needed
        } else {
          alert("Error adding to bag");
        }
      });
    });
  });
});
