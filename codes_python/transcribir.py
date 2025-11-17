from openai import OpenAI
from openai import BadRequestError
import os
import subprocess
import tempfile
import shutil


FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _formatear_transcripcion(contenido):
    """Separa los turnos etiquetando a usuario y agente."""
    prompt = (
        "Eres un formateador de diálogos. Deja la transcripción en turnos limpios entre "
        "'Usuario:' y 'Agente:'.\n\n"
        "Reglas:\n"
        "- Respeta el orden exacto de aparición.\n"
        "- Conserva el texto original sin resumir ni añadir información.\n"
        "- Agrupa frases consecutivas del mismo hablante en un solo turno para que no se mezclen voces.\n"
        "- Distingue al hablante: preguntas/peticiones suelen ser del Usuario; respuestas/explicaciones del Agente.\n"
        "- Si sigue siendo ambiguo, elige la etiqueta que mejor encaje pero nunca inventes contenido.\n"
        "- Entrega solo los turnos, un renglón por turno, sin comentarios adicionales.\n\n"
        "Transcripción sin procesar:\n"
        f"{contenido}"
    )
    resultado = client.responses.create(
        model="gpt-5",
        input=prompt
    )
    return resultado.output_text.strip()


def _recodificar_a_wav(origen, destino=None):
    """Recodifica a WAV mono 16k para máxima compatibilidad."""
    # Resolver ruta de ffmpeg: variable de entorno, PATH, o fallback común
    ffmpeg_bin = shutil.which(FFMPEG_BIN) or shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
    if not ffmpeg_bin:
        raise ValueError(
            "ffmpeg no está instalado o no está en PATH. "
            "Instálalo o define FFMPEG_BIN con la ruta absoluta (ej. /usr/bin/ffmpeg)."
        )
    if destino is None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        destino = tmp.name
        tmp.close()
    cmd = [
        ffmpeg_bin, "-y",
        "-i", origen,
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        destino,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise ValueError("No se pudo recodificar el audio. Verifica el archivo o formato.")
    return destino


def _transcribir(path_audio):
    with open(path_audio, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="gpt-4o-transcribe"
        )
    return transcription.text


def transcribir_audio(path_audio):
    recodificado = None
    try:
        texto_transcrito = _transcribir(path_audio)
    except BadRequestError:
        # Reintenta recodificando a WAV seguro y lo deja persistente
        base, _ = os.path.splitext(path_audio)
        recodificado = f"{base}.wav"
        texto_transcrito = _transcribir(_recodificar_a_wav(path_audio, recodificado))
    except Exception as e:
        raise ValueError("El audio no pudo procesarse. Asegura un formato válido (mp3/wav/webm/mp4).") from e

    # Generar un WAV reproducible (PCM 16k) para el reproductor si no existe recodificado
    reproducible = recodificado
    if reproducible is None:
        base, _ = os.path.splitext(path_audio)
        reproducible = f"{base}_playback.wav"
        try:
            _recodificar_a_wav(path_audio, reproducible)
        except Exception:
            reproducible = path_audio  # cae al original si falla recodificación

    return _formatear_transcripcion(texto_transcrito), reproducible
