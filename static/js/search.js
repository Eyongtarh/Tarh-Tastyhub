// static/js/search.js
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

        box.innerHTML = `<div class="dropdown-item text-muted">Searching...</div>`;
        box.style.display = 'block';

        try {
            const res = await fetch(`/dishes/search-dishes/?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            box.innerHTML = '';

            if (Array.isArray(data.dishes) && data.dishes.length) {
                data.dishes.forEach((d, idx) => {
                    const link = document.createElement('a');
                    link.className = 'dropdown-item';
                    link.href = d.url;
                    link.textContent = d.name;
                    link.setAttribute('role', 'option');
                    link.setAttribute('data-index', idx);
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

        box.setAttribute('role', 'listbox');

        input.addEventListener('input', debounce(() => search(input.value.trim(), box)));

        input.addEventListener('blur', () => setTimeout(() => { box.style.display = 'none'; }, 150));

        document.addEventListener('click', e => {
            if (e.target === input || box.contains(e.target)) return;
            box.style.display = 'none';
        });

        let currentIndex = -1;
        input.addEventListener('keydown', (e) => {
            const items = Array.from(box.querySelectorAll('.dropdown-item'));
            if (!items.length) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentIndex = Math.min(items.length - 1, currentIndex + 1);
                items.forEach(i => i.classList.remove('active'));
                items[currentIndex].classList.add('active');
                items[currentIndex].scrollIntoView({ block: 'nearest' });
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentIndex = Math.max(0, currentIndex - 1);
                items.forEach(i => i.classList.remove('active'));
                items[currentIndex].classList.add('active');
                items[currentIndex].scrollIntoView({ block: 'nearest' });
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (currentIndex >= 0 && items[currentIndex]) {
                    window.location = items[currentIndex].href;
                }
            }
        });
    });
});
