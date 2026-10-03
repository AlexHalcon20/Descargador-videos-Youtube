# Descargador de videos de YouTube / YouTube Video Downloader

[🇪🇸 Español](#-español) · [🇬🇧 English](#-english)

---

## 🇪🇸 Español

Programa de consola escrito en Python para descargar videos de YouTube usando [`pytubefix`](https://github.com/JuanBindez/pytubefix). Te muestra las calidades disponibles, te deja elegir una y guarda el video en la carpeta `descargas/`.

### Características

- Muestra título, autor y duración del video antes de descargar.
- Lista las calidades disponibles en dos grupos:
  - **Descargas directas** (video + audio en un solo archivo, calidad básica).
  - **Alta calidad** (video y audio por separado; se combinan automáticamente con `ffmpeg`).
- Prueba primero **sin iniciar sesión** y solo pide iniciar sesión con Google (OAuth) si el video tiene restricción de edad.
- Mensajes de error claros cuando un video no está disponible.

### Requisitos

- **Python 3.9 o superior**
- **pytubefix**
- **ffmpeg** (opcional, pero necesario para las opciones de alta calidad)

### Instalación

1. Clona o descarga este proyecto.
2. Instala la dependencia:

   ```bash
   pip install --upgrade pytubefix
   ```

3. (Opcional) Instala [ffmpeg](https://ffmpeg.org/) y asegúrate de que esté en tu `PATH`. Puedes comprobarlo con:

   ```bash
   ffmpeg -version
   ```

   Sin ffmpeg el programa sigue funcionando, pero solo podrás descargar las calidades directas (progresivas).

### Uso

Ejecuta el programa desde la carpeta del proyecto:

```bash
python descargadoryt.py
```

1. Pega la URL del video de YouTube.
2. El programa muestra título, autor, duración y las opciones disponibles.
3. Escribe el número de la opción que quieras.
4. El archivo se guarda en la carpeta `descargas/` (se crea si no existe).

> **Nota:** la carpeta `descargas/` se crea dentro del directorio desde el que ejecutes el comando, así que conviene ejecutarlo siempre desde la carpeta del proyecto.

### Cómo funciona

- Primero intenta cargar el video **sin sesión**, que funciona para la gran mayoría de videos.
- Si YouTube indica que el video requiere iniciar sesión (restricción de edad), reintenta con OAuth. La primera vez se muestra un enlace y un código para autorizar tu cuenta en `https://www.google.com/device`; el token queda guardado en caché para próximas ejecuciones.
- Para las opciones de alta calidad descarga el video y el audio por separado en archivos temporales y los une con `ffmpeg` (`-c copy`, sin recodificar), borrando después los temporales.

### Solución de problemas

**`VideoUnavailable: <id> is unavailable` en todos los videos**

Es un bug conocido de pytubefix ([issue #674](https://github.com/JuanBindez/pytubefix/issues/674)): con `use_oauth=True`, YouTube responde con un falso `UNPLAYABLE — The page needs to be reloaded` para *cualquier* video, aunque los datos básicos (título, autor) sí carguen. Por eso el programa **no usa OAuth por defecto**, solo como último recurso.

Si aun así ves el error:

1. Actualiza la librería: `pip install --upgrade pytubefix`.
2. Si el video es realmente de edad restringida, el inicio de sesión (OAuth) puede seguir afectado por ese bug hasta que se corrija en pytubefix.
3. Si el video fue eliminado, es privado o está bloqueado en tu región, el error es legítimo.

**No aparece el código de autorización de Google**

Borra la caché del token para forzar una nueva autorización:

```python
from pytubefix.helpers import reset_cache
reset_cache()
```

**"ffmpeg no está instalado"**

Instala ffmpeg y verifica que `ffmpeg -version` funcione en tu terminal. Sin él solo se ofrecen las descargas directas.

**Scripts de diagnóstico**

El proyecto incluye tres scripts auxiliares usados para encontrar la causa del error anterior:

| Archivo | Qué hace |
|---|---|
| `diagnostico.py` | Muestra la versión de pytubefix, resetea la caché de OAuth y prueba la carga con y sin sesión. |
| `diagnostico2.py` | Imprime el `playabilityStatus` exacto que envía YouTube para un video. |
| `diagnostico3.py` | Prueba varios clientes internos de pytubefix (WEB, ANDROID, IOS, etc.) con y sin OAuth. |

Cambia la URL dentro de cada script para probar otro video. Son opcionales y puedes borrarlos si no los necesitas.

### Estructura del proyecto

```
.
├── descargadoryt.py   # Programa principal
├── diagnostico*.py    # Scripts de diagnóstico (opcionales)
├── descargas/         # Videos descargados (se crea automáticamente)
└── README.md
```

### Aviso legal

Úsalo solo para contenido que tengas derecho a descargar (tus propios videos, contenido con licencia libre o con permiso del autor). Descargar videos puede ir en contra de los Términos de Servicio de YouTube y de los derechos de autor; la responsabilidad del uso es tuya.

---

## 🇬🇧 English

A Python command-line tool to download YouTube videos using [`pytubefix`](https://github.com/JuanBindez/pytubefix). It shows the available qualities, lets you pick one, and saves the video to the `descargas/` folder.

### Features

- Shows the title, author and duration before downloading.
- Lists available qualities in two groups:
  - **Direct downloads** (video + audio in a single file, basic quality).
  - **High quality** (separate video and audio streams, merged automatically with `ffmpeg`).
- Tries **without signing in** first, and only asks for a Google sign-in (OAuth) if the video is age-restricted.
- Clear error messages when a video is unavailable.

### Requirements

- **Python 3.9 or newer**
- **pytubefix**
- **ffmpeg** (optional, but required for the high-quality options)

### Installation

1. Clone or download this project.
2. Install the dependency:

   ```bash
   pip install --upgrade pytubefix
   ```

3. (Optional) Install [ffmpeg](https://ffmpeg.org/) and make sure it is on your `PATH`. Check with:

   ```bash
   ffmpeg -version
   ```

   Without ffmpeg the program still works, but only the direct (progressive) qualities are available.

### Usage

Run the program from the project folder:

```bash
python descargadoryt.py
```

1. Paste the YouTube video URL.
2. The program shows the title, author, duration and the available options.
3. Type the number of the option you want.
4. The file is saved in the `descargas/` folder (created if it doesn't exist).

> **Note:** the `descargas/` folder is created in the directory you run the command from, so it's best to always run it from the project folder.

### How it works

- It first tries to load the video **without signing in**, which works for the vast majority of videos.
- If YouTube says the video requires sign-in (age restriction), it retries with OAuth. The first time, a link and a code are shown to authorize your account at `https://www.google.com/device`; the token is cached for future runs.
- For the high-quality options it downloads video and audio separately into temporary files and merges them with `ffmpeg` (`-c copy`, no re-encoding), then deletes the temporary files.

### Troubleshooting

**`VideoUnavailable: <id> is unavailable` on every video**

This is a known pytubefix bug ([issue #674](https://github.com/JuanBindez/pytubefix/issues/674)): with `use_oauth=True`, YouTube returns a bogus `UNPLAYABLE — The page needs to be reloaded` for *any* video, even though basic metadata (title, author) loads fine. That's why this program **does not use OAuth by default**, only as a last resort.

If you still see the error:

1. Update the library: `pip install --upgrade pytubefix`.
2. If the video is genuinely age-restricted, OAuth sign-in may remain affected by that bug until it is fixed upstream.
3. If the video was deleted, is private, or is blocked in your region, the error is legitimate.

**The Google authorization code doesn't appear**

Clear the cached token to force a new authorization:

```python
from pytubefix.helpers import reset_cache
reset_cache()
```

**"ffmpeg is not installed"**

Install ffmpeg and make sure `ffmpeg -version` works in your terminal. Without it only direct downloads are offered.

**Diagnostic scripts**

The project includes three helper scripts that were used to track down the error above:

| File | What it does |
|---|---|
| `diagnostico.py` | Prints the pytubefix version, resets the OAuth cache, and tests loading with and without sign-in. |
| `diagnostico2.py` | Prints the exact `playabilityStatus` YouTube returns for a video. |
| `diagnostico3.py` | Tries several internal pytubefix clients (WEB, ANDROID, IOS, etc.) with and without OAuth. |

Edit the URL inside each script to test a different video. They are optional and can be deleted.

### Project structure

```
.
├── descargadoryt.py   # Main program
├── diagnostico*.py    # Diagnostic scripts (optional)
├── descargas/         # Downloaded videos (created automatically)
└── README.md
```

### Disclaimer

Use it only for content you have the right to download (your own videos, freely licensed content, or content with the author's permission). Downloading videos may violate YouTube's Terms of Service and copyright law; you are responsible for how you use it.
