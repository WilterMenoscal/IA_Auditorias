from flask import Flask, render_template, request, url_for, send_from_directory
from dotenv import load_dotenv
import os
from werkzeug.exceptions import RequestEntityTooLarge
from openai import BadRequestError
from werkzeug.utils import secure_filename

# Cargar variables de entorno
load_dotenv()

from codes_python.transcribir import transcribir_audio
from codes_python.sentimiento import analizar_sentimiento
from codes_python.resumen import resumir_texto
from codes_python.keywords import extraer_keywords
from codes_python.analitica import calcular_csat

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Crear ruta absoluta para uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    archivo = request.files.get("audio")

    if not archivo:
        return "No se envió ningún archivo", 400

    audio_filename = secure_filename(archivo.filename)
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

    # Guardar archivo subido
    archivo.save(ruta)

    # 1. Transcripción (devuelve texto y ruta reproducible)
    try:
        texto, recodificado = transcribir_audio(ruta)
    except ValueError as e:
        return str(e), 400
    except BadRequestError as e:
        return "El audio no pudo procesarse (posible formato/archivo dañado).", 400

    # 2. Análisis Sentimiento
    print("Analizando sentimiento...\n", texto)
    sentimiento = analizar_sentimiento(texto)
    print(sentimiento)
    # 3. Resumen
    resumen = resumir_texto(texto)

    # 4. Keywords
    keywords = extraer_keywords(texto)

    # 5. CSAT 
    csat_result = calcular_csat(texto, sentimiento)
    csat_total = csat_result.get("total")
    csat_criterios = csat_result.get("criterios", {})

    # Servir el recodificado/reproducible si existe, de lo contrario el original
    audio_servir = os.path.basename(recodificado) if recodificado else audio_filename
    audio_url = url_for('uploaded_file', filename=audio_servir)

    return render_template(
        "resultado.html",
        texto=texto,
        sentimiento=sentimiento,
        resumen=resumen,
        keywords=keywords,
        csat=csat_total,
        csat_criterios=csat_criterios,
        audio_url=audio_url
    )


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return (
        "El archivo excede el límite permitido (50 MB). "
        "Reduce el tamaño del audio o aumenta el límite en MAX_CONTENT_LENGTH.",
        413,
    )

if __name__ == "__main__":
    app.run(debug=True)
