# Sitio web de Creax

Sitio estático (HTML, CSS y JS) generado a partir de archivos de contenido.
No usa base de datos ni servidor de aplicaciones: se sube a cualquier hosting.

## Estructura

```
content/          ← TEXTOS Y DATOS (lo único que hay que tocar para cambiar contenido)
  sitio.json      ← SEO, marca, contacto, menú, footer
  inicio.json     ← secciones de la página de inicio
assets/
  images/         ← fotos originales (el build crea las versiones optimizadas)
  css/styles.css  ← diseño
  js/main.js      ← menú móvil y formulario a WhatsApp
templates/
  index.html      ← estructura HTML de la página
build.py          ← genera el sitio en dist/
dist/             ← SITIO LISTO PARA SUBIR (se regenera en cada build)
```

## Generar el sitio

Requiere Python 3.9+:

```
pip install jinja2 pillow
python build.py
```

El resultado queda en `dist/`. Para verlo localmente:

```
cd dist
python -m http.server 8000
```

y abrir http://localhost:8000

## Cambiar contenido

- **Textos**: editar `content/inicio.json` o `content/sitio.json` y volver a correr `python build.py`.
- **Fotos**: copiar la foto nueva a `assets/images/` y poner su nombre en el campo `imagen` correspondiente del JSON.
  El build genera automáticamente versiones de 640, 1200 y 1800 px en WebP.
- **Contacto / WhatsApp**: `content/sitio.json` → `contacto`.

## Vista previa para el cliente (GitHub Pages)

Cada `git push` a `main` ejecuta `.github/workflows/pages.yml`, que corre
`python build.py --staging` y publica en https://celishd.github.io/creax-web/
(tarda ~1 minuto). Esta versión lleva `noindex` y `robots.txt` con `Disallow`
para que Google no la indexe; el sitio definitivo se genera con `python build.py`.

Flujo de cambios: editar `content/*.json` o `assets/` → `git commit` → `git push`.

## Publicar en el servidor propio (Docker + Cloudflare Tunnel)

El servidor solo necesita Docker. La imagen genera el sitio y lo sirve con Caddy
(con cabeceras de seguridad y CSP estricta); `cloudflared` conecta el sitio a
internet sin abrir puertos en el router.

1. En Cloudflare: agregar `creax.cl` (cambiar nameservers en el registrador).
2. Zero Trust → Networks → Tunnels → crear túnel, copiar el token y añadir un
   *Public hostname* `creax.cl` (y `www`) → servicio `http://web:8080`.
3. En el servidor:

```
git clone <repo> && cd creax-web
cp .env.example .env   # pegar TUNNEL_TOKEN
docker compose up -d --build
```

Actualizar contenido: `git pull && docker compose up -d --build`.
`restart: unless-stopped` + `systemctl enable docker` lo levanta solo tras cortes de luz.

La tipografía Archivo (variable, licencia OFL) está autoalojada en `assets/fonts/`:
el sitio no carga recursos de terceros.

El resultado de `python build.py` (`dist/`) también sirve para subir a cualquier hosting.
Incluye `robots.txt`, `sitemap.xml`, favicon, imagen para redes sociales (`og.jpg`)
y datos estructurados de negocio local para Google.

## Fase 2: edición sin código

Como todo el contenido vive en `content/*.json` y las fotos en `assets/images/`,
se puede conectar un editor visual sobre esos mismos archivos (por ejemplo TinaCMS,
Pages CMS o Decap CMS) sin cambiar el diseño.
