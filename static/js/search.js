document.addEventListener('DOMContentLoaded', () => {
    const fields = [
        { inputId: 'search-input', resultsId: 'search-results' },
        { inputId: 'mobile-search-input', resultsId: 'mobile-search-results' }
    ];

    const search = async (query, box) => {
        if (!query || query.length < 2) {
            box.style.display = 'none';
            box.innerHTML = '';
            return;
        }

        try {
            const res = await fetch(`/search-dishes/?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            box.innerHTML = '';

            if (Array.isArray(data.dishes) && data.dishes.length > 0) {
                data.dishes.forEach(d => {
                    const link = document.createElement('a');
                    link.className = 'dropdown-item';
                    link.href = d.url;
                    link.textContent = d.name;
                    box.appendChild(link);
                });
            } else {
                const span = document.createElement('span');
                span.className = 'dropdown-item text-muted';
                span.textContent = 'No dishes found';
                box.appendChild(span);
            }
            box.style.display = 'block';
        } catch (err) {
            console.error('Search error:', err);
            box.style.display = 'none';
        }
    };

    const debounce = (fn, delay = 300) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn(...args), delay);
        };
    };

    fields.forEach(({ inputId, resultsId }) => {
        const input = document.getElementById(inputId);
        const box = document.getElementById(resultsId);
        if (!input || !box) return;

        input.addEventListener('input', debounce(() => search(input.value, box)));

        document.addEventListener('click', e => {
            if (!input.contains(e.target) && !box.contains(e.target)) box.style.display = 'none';
        });
    });
});
