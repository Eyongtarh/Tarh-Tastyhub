document.addEventListener('DOMContentLoaded', () => {
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

    document.querySelectorAll('.add-to-bag').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const portionId = btn.dataset.portionId || btn.dataset.id;
            if (!portionId) return;

            try {
                const res = await fetch(`/bag/add/${portionId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    },
                    body: new URLSearchParams({ quantity: 1 })
                });

                const data = await res.json();
                if (!data.success) return console.error('Failed to add to bag', data);

                document.querySelectorAll('.bag-count').forEach(el => el.textContent = data.bag_count);
            } catch (err) {
                console.error('Error adding to bag:', err);
            }
        });
    });
});
