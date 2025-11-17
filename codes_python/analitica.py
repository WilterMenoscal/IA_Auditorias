import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _clamp(valor, minimo=0, maximo=100):
    return max(min(valor, maximo), minimo)


def calcular_csat(texto, sentimiento=None):
    """Calcula CSAT con el modelo y devuelve detalle por criterio y total."""
    sentimiento = (sentimiento or "desconocido").lower()
    prompt = (
        "Evalúa la satisfacción del cliente (Usuario) en esta conversación con un agente.\n"
        "Asigna puntajes de 1 a 100 a estos criterios y calcula un CSAT global ponderado.\n"
        "Criterios y pesos (evaluando al AGENTE): resolucion (30%), tono (25%), cortesia (15%), cierre (15%), conformidad (15%).\n"
        "Devuelve un JSON con números enteros 0-100 en este formato exacto: \n"
        '{"resolucion":<int>,"tono":<int>,"cortesia":<int>,"cierre":<int>,"conformidad":<int>,"total":<int>}\n'
        "No incluyas texto extra ni comentarios.\n"
        "Si se percibe agradecimiento o conformidad → sube; queja o falta de resolución → baja.\n"
        f"Sentimiento previo detectado: {sentimiento}.\n\n"
        f"Conversación:\n{texto}"
    )

    resultado = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        datos = json.loads(resultado.output_text)
        criterios = {
            "resolucion": int(_clamp(float(datos.get("resolucion", 0)))),
            "tono": int(_clamp(float(datos.get("tono", 0)))),
            "cortesia": int(_clamp(float(datos.get("cortesia", 0)))),
            "cierre": int(_clamp(float(datos.get("cierre", 0)))),
            "conformidad": int(_clamp(float(datos.get("conformidad", 0)))),
        }
        total = int(_clamp(float(datos.get("total", sum(criterios.values()) / 5))))
        return {"criterios": criterios, "total": total}
    except Exception:
        # Fallback seguro en caso de mal formato
        return {
            "criterios": {
                "resolucion": None,
                "tono": None,
                "cortesia": None,
                "cierre": None,
                "conformidad": None,
            },
            "total": 50,
        }
