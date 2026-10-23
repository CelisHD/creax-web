# Etapa 1: genera el sitio estático (dist/) desde content/, templates/ y assets/
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY build.py .
COPY content content
COPY templates templates
COPY assets assets
RUN python build.py

# Etapa 2: servidor web mínimo (solo archivos estáticos, sin runtime de aplicación)
FROM caddy:2-alpine
# Escucha en 8080: no necesita la capability para puertos <1024, y con cap_drop ALL impediría arrancar.
RUN setcap -r /usr/bin/caddy
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
EXPOSE 8080
