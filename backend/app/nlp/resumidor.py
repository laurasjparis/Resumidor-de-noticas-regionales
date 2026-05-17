import httpx
import logging

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "llama3.2"


def generar_resumen(noticias_texto: list[str]) -> str:
    """
    Recibe una lista de textos de noticias del mismo evento
    y genera un resumen usando Ollama (llama3.2).
    """
    # Si es una sola noticia, el prompt es más simple
    if len(noticias_texto) == 1:
        prompt = f"""Resume la siguiente noticia en 2-3 oraciones en español. 
Sé conciso y objetivo. Solo devuelve el resumen, sin explicaciones adicionales.

Noticia:
{noticias_texto[0][:1500]}

Resumen:"""
    else:
        noticias_unidas = ""
        for i, texto in enumerate(noticias_texto, 1):
            # Limitar cada noticia a 1000 chars para no saturar el contexto
            noticias_unidas += f"\n--- Noticia {i} ---\n{texto[:1000]}\n"

        prompt = f"""Las siguientes {len(noticias_texto)} noticias hablan del mismo evento. 
Genera UN SOLO resumen unificado de 2-3 oraciones en español.
Sé conciso, objetivo y menciona los datos clave (qué pasó, dónde, cuándo).
Solo devuelve el resumen, sin explicaciones adicionales.

{noticias_unidas}

Resumen unificado:"""

    try:
        respuesta = httpx.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200,
                }
            },
            timeout=60.0,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        resumen = datos.get("response", "").strip()
        logger.info(f"Resumen generado ({len(resumen)} chars)")
        return resumen

    except httpx.ConnectError:
        logger.error("No se pudo conectar a Ollama. ¿Está corriendo? (ollama serve)")
        return "Error: Ollama no está disponible. Ejecute 'ollama serve' primero."
    except Exception as e:
        logger.error(f"Error generando resumen: {e}")
        return f"Error generando resumen: {str(e)}"