// Pitää sovelluksen pohjan tallessa, jotta se aukeaa heti myös huonolla yhteydellä.
// Sijainteja ei koskaan tallenneta välimuistiin, ne haetaan aina palvelimelta.
const CACHE = "perhekartta-v1";
const SHELL = ["/", "/static/icon-192.png"];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api/")) {
    return;
  }
  // ensin verkosta, vasta jos se ei onnistu, välimuistista
  event.respondWith(
    fetch(event.request)
      .then(res => {
        if (res.ok && !res.redirected) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(event.request, copy));
        }
        return res;
      })
      .catch(() => caches.match(event.request))
  );
});
