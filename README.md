# IA Auditorías – App de transcripción y análisis

DEMO de auditorías de audios de call centers: aplicación Flask que recibe un audio, lo transcribe con OpenAI, separa turnos Usuario/Agente, resume, extrae keywords, calcula sentimiento y CSAT, y muestra todo en la vista de resultado.

## Requisitos
- Python 3.10+
- `ffmpeg` disponible en el sistema (`FFMPEG_BIN` opcional para ruta personalizada).
- Clave de OpenAI en `.env`

## Configuración rápida
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "OPENAI_API_KEY=tu_clave_aqui" > .env   # no la subas al repo
# opcional: echo "FFMPEG_BIN=/ruta/a/ffmpeg" >> .env
```

## Ejecutar
```bash
source venv/bin/activate
export FLASK_APP=app.py
flask run
```
La app levanta en `http://127.0.0.1:5000/`.

## Producción con Gunicorn + Nginx (resumen)
- Instala Gunicorn en el entorno (`pip install gunicorn`).
- Arranca la app: `gunicorn -w 4 -b 0.0.0.0:8000 app:app`.
- Configura Nginx como reverse proxy en el puerto 80 que haga `proxy_pass http://127.0.0.1:8000;`.
- Asegura cabeceras de tamaño si aceptas audios grandes: `client_max_body_size 50M;`.
- Usa `systemd` para el servicio de Gunicorn (ej. `/etc/systemd/system/miapp.service`) y otro para Nginx. Recarga con `sudo systemctl daemon-reload` y `sudo systemctl restart miapp nginx`.
- Mantén `.env` con tu `OPENAI_API_KEY` solo en el servidor y usa `EnvironmentFile=/ruta/.env` en el servicio de systemd para no embutir secretos en el unit.

## Estructura
- `app.py`: rutas Flask y orquestación.
- `codes_python/`: lógica de transcripción, análisis de sentimiento, resumen, keywords y CSAT.
- `templates/`: formularios y resultado.
- `uploads/`: audios subidos (excluido por `.gitignore`).

## Notas de seguridad
- No subas `.env` ni audios de `uploads/`. El `.gitignore` ya los excluye. Mantén la clave de OpenAI solo en `.env`.
- Ajusta `MAX_CONTENT_LENGTH` en `app.py` si necesitas subir archivos más grandes.
