from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analizar_sentimiento(texto):
    prompt = (
        "Analiza el siguiente diálogo etiquetado con Usuario: y Agente:. "
        "Evalúa el sentimiento del cliente respecto a la atención del agente considerando trato, claridad, cortesía y si el agente ayudó a resolver su problema. \n"
        "Responde con una sola palabra en minúsculas: positivo, negativo o neutral. \n"
        "No agregues texto extra, explicaciones, emojis ni puntuaciones; solo esa palabra.\n\n"
        f"Texto:\n{texto}"
    )

    result = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    # El output viene limpio en output_text
    return result.output_text.strip()
