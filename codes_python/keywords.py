from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extraer_keywords(texto):
    prompt = f"Extrae 5 palabras clave del siguiente texto y respóndelas separadas por comas:\n{texto}"
    result = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return [k.strip() for k in result.output_text.split(",")]
