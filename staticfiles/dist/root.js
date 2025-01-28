function route() {
    const hash = window.location.hash.substring(1);

    switch (hash) {
        case 'home':
            fetch('/admin/')
                .then(response => {
                    if (!response.ok) throw new Error('Page not found');
                    return response.text();
                })
                .then(html => {
                    document.body.innerHTML = html;
                })
                .catch(error => {
                    document.body.innerHTML = `<h1>Error</h1><p>${error.message}</p>`;
                });
            break;
        case 'menus':
            fetch('/admin/menus/')
                .then(response => {
                    if (!response.ok) throw new Error('Page not found');
                    return response.text();
                })
                .then(html => {
                    document.body.innerHTML = html;
                })
                .catch(error => {
                    document.body.innerHTML = `<h1>Error</h1><p>${error.message}</p>`;
                });
            break;
        default:
            document.body.innerHTML = '<h1>404 Not Found</h1><p>Page not found.</p>';
    }
}

// Exécuter la fonction de routage au chargement initial et lors des changements d'URL
window.addEventListener('load', route);
window.addEventListener('hashchange', route);
