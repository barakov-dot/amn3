# Nginx Proxy Manager для web-панели

Короткая памятка для доступа к web-панели через HTTPS reverse proxy.

## Proxy Host

- Domain Names: домен панели, например `admin.example.ru`.
- Scheme: `http`.
- Forward Hostname / IP: `127.0.0.1` или LAN IP VPS/контейнера с приложением.
- Forward Port: `3030`.
- Cache Assets: выключить на первом тесте.
- Block Common Exploits: включить.
- Websockets Support: можно оставить выключенным.

## SSL

- Request a new SSL Certificate.
- Force SSL: включить после успешной проверки HTTP.
- HTTP/2 Support: включить.

## Проверка CSS

Если страница открывается, но выглядит без CSS:

```bash
curl -I https://DOMAIN/static/admin.css
```

Ожидается:

```text
HTTP/1.1 200 OK
content-type: text/css
```

В Nginx Proxy Manager должен проксироваться весь путь `/`, а не только `/login`.
