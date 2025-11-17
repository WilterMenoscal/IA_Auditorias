from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def resumir_texto(texto):
    prompt = f"Resume el siguiente texto en menos de 5 líneas:\n{texto}"
    result = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return result.output_text
