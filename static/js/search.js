// Socket.io search functionality
document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const searchInput = document.getElementById('search');
    const resultsList = document.getElementById('results');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            socket.emit('search', { query: this.value });
        });

        socket.on('search_results', function(data) {
            resultsList.innerHTML = '';
            
            if (data.length === 0 && searchInput.value.trim() !== '') {
                const li = document.createElement('li');
                li.classList.add('list-group-item', 'text-muted');
                li.textContent = 'Nincs találat';
                resultsList.appendChild(li);
                return;
            }
            
            data.forEach(recipe => {
                const li = document.createElement('li');
                li.classList.add('list-group-item');
                li.innerHTML = `<a href="/recipe/${recipe.id}" class="text-decoration-none">${recipe.name}</a>`;
                resultsList.appendChild(li);
            });
        });

        socket.on('error', function(data) {
            alert(data.message);
        });
    }
});
