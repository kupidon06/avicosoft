// service-worker.js

// Cache name
const CACHE_NAME = 'tasteflow-cache-v1';

// Files to cache
const URLS_TO_CACHE = [
  '/',
  '/static/assets/img/tasteflow.png',
  '/static/styles.css',
  // Ajoutez ici d'autres fichiers que vous souhaitez mettre en cache
];

// Install event
// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Cache opened');
      return Promise.all(
        URLS_TO_CACHE.map(url => {
          console.log('Caching URL:', url);
          return cache.add(url).catch(error => {
            console.error('Failed to cache:', url, error);
          });
        })
      );
    })
  );
});
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Cache opened');
      return cache.addAll(URLS_TO_CACHE);
    })
  );
});


self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(URLS_TO_CACHE);
      })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
