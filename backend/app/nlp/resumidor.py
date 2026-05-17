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
    instrucciones = """INSTRUCCIONES ESTRICTAS:
- Resume en 2-3 oraciones en español.
- SOLO usa información que aparece explícitamente en el texto.
- NUNCA inventes fechas, nombres, edades o lugares que no estén en el texto.
- Si no sabes un dato, simplemente no lo menciones.
- Menciona: qué pasó y dónde ocurrió.
- Responde SOLO con el resumen, nada más."""

    if len(noticias_texto) == 1:
        prompt = f"""{instrucciones}

Noticia:
{noticias_texto[0][:2000]}

Resumen:"""
    else:
        noticias_unidas = ""
        for i, texto in enumerate(noticias_texto, 1):
            noticias_unidas += f"\n--- Noticia {i} ---\n{texto[:1200]}\n"

        prompt = f"""{instrucciones}
Estas {len(noticias_texto)} noticias hablan del mismo evento. Genera UN resumen unificado.

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
                    "temperature": 0.1,
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