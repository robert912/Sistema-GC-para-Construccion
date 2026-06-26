import os
import asyncio
import json
import re
import logging
from functools import partial
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_MODEL_DIR = Path(__file__).parent.parent / "modelo"
_llm_instance = None
_llm_loaded = False


def _find_model_path() -> Optional[str]:
    env_path = os.environ.get("LLAMA_MODEL_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    if _DEFAULT_MODEL_DIR.exists():
        gguf_files = sorted(_DEFAULT_MODEL_DIR.glob("*.gguf"))
        if gguf_files:
            return str(gguf_files[0])
    return None


def _load_llm_sync():
    global _llm_instance, _llm_loaded
    if _llm_loaded:
        return _llm_instance
    model_path = _find_model_path()
    if not model_path:
        _llm_loaded = True
        return None
    try:
        from llama_cpp import Llama
        logger.info(f"Cargando modelo: {Path(model_path).name} ...")
        _llm_instance = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=max(1, (os.cpu_count() or 2) - 1),
            n_gpu_layers=0,
            verbose=False,
        )
        logger.info("Modelo local cargado correctamente.")
    except Exception as e:
        logger.warning(f"No se pudo cargar el modelo llama.cpp: {e}")
    _llm_loaded = True
    return _llm_instance


async def _chat(messages: list, max_tokens: int = 512) -> Optional[str]:
    loop = asyncio.get_event_loop()
    llm = await loop.run_in_executor(None, _load_llm_sync)
    if not llm:
        return None
    try:
        result = await loop.run_in_executor(
            None,
            partial(llm.create_chat_completion, messages=messages, max_tokens=max_tokens, temperature=0.1),
        )
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Chat failed: {e}")
        return None


CATEGORIES = ["Plazo", "Costo", "Seguridad", "Calidad", "Proveedores", "Diseño"]
SEVERITIES = ["Alta", "Media", "Baja"]
PHASES = ["Planificación", "Fundaciones", "Estructura", "Instalaciones", "Terminaciones", "Cierre"]


async def check_ai() -> dict:
    model_path = _find_model_path()
    if not model_path:
        return {"available": False, "reason": "No se encontró archivo .gguf en la carpeta modelo/"}
    try:
        import llama_cpp  # noqa: F401
        return {"available": True, "model": Path(model_path).name}
    except ImportError:
        return {"available": False, "reason": "llama-cpp-python no instalado. Ejecuta: pip install llama-cpp-python"}
    except Exception as e:
        return {"available": False, "reason": f"llama-cpp-python instalado pero no funciona: {e}"}


async def get_embedding(text: str) -> Optional[List[float]]:
    return None  # Sin Ollama no hay embeddings — la búsqueda usa palabras clave


def _build_classify_prompt(title: str, description: str, cause: str, solution: str) -> str:
    text = f"Título: {title}\nDescripción: {description}\nCausa: {cause}\nSolución: {solution}"
    return f"""Eres un clasificador de lecciones aprendidas para proyectos de construcción.
Analiza el siguiente texto y clasifícalo. Responde ÚNICAMENTE con un objeto JSON válido.

{text}

Reglas estrictas:
- "category" debe ser exactamente uno de: {CATEGORIES}
- "severity" debe ser exactamente uno de: {SEVERITIES}
- "phase" debe ser exactamente uno de: {PHASES}
- "tags" debe ser una lista de 3 a 5 palabras clave en español

Responde solo con el JSON, sin texto adicional ni comillas de código:
{{"category": "...", "severity": "...", "phase": "...", "tags": ["...", "...", "..."]}}"""


def _parse_classification(response_text: str) -> Optional[dict]:
    match = re.search(r'\{[^{}]+\}', response_text, re.DOTALL)
    if not match:
        return None
    try:
        result = json.loads(match.group())
        if result.get("category") not in CATEGORIES:
            result["category"] = "Calidad"
        if result.get("severity") not in SEVERITIES:
            result["severity"] = "Media"
        if result.get("phase") not in PHASES:
            result["phase"] = "Planificación"
        if not isinstance(result.get("tags"), list):
            result["tags"] = []
        return result
    except Exception:
        return None


async def classify_lesson(title: str, description: str, cause: str, solution: str) -> dict:
    prompt = _build_classify_prompt(title, description, cause, solution)
    text = await _chat([{"role": "user", "content": prompt}], max_tokens=200)
    if text:
        result = _parse_classification(text)
        if result:
            return result
    return {"category": "Sin clasificar", "severity": "Sin clasificar", "phase": "Sin clasificar", "tags": []}


def _build_report_prompt(query: str, lessons: List[dict], project_type: Optional[str]) -> str:
    lessons_text = "\n\n".join([
        f"[{i+1}] Categoría: {l.get('category','?')} | Severidad: {l.get('severity','?')} | Fase: {l.get('phase','?')}\n"
        f"Título: {l['title']}\n"
        f"Descripción: {l['description']}\n"
        f"Causa: {l.get('cause', 'No especificada')}\n"
        f"Solución aplicada: {l.get('solution', 'No especificada')}"
        for i, l in enumerate(lessons[:10])
    ])
    tipo_str = f"Tipo de proyecto: {project_type}" if project_type else ""
    return f"""Eres un experto en gestión del conocimiento para empresas constructoras chilenas.
Analiza las siguientes lecciones aprendidas y genera un informe ejecutivo en español.

Consulta del proyecto: {query}
{tipo_str}

Lecciones relevantes encontradas ({len(lessons)}):
{lessons_text}

Genera un informe ejecutivo en Markdown con estas secciones:
## Resumen Ejecutivo
(2-3 oraciones que sinteticen el panorama general)

## Principales Riesgos Identificados
(máximo 3, con bullet points)

## Recomendaciones Clave
(máximo 5 puntos accionables y concretos)

## Situaciones o Proveedores a Evitar
(solo si aplica, bullet points)

## Mejores Prácticas Identificadas
(solo si aplica, bullet points)

Sé directo, práctico y orientado a la acción. Máximo 400 palabras."""


async def generate_report(query: str, lessons: List[dict], project_type: Optional[str] = None) -> str:
    if not lessons:
        return "No se encontraron lecciones relevantes para esta consulta."

    prompt = _build_report_prompt(query, lessons, project_type)

    text = await _chat([{"role": "user", "content": prompt}], max_tokens=600)
    if text:
        return text

    summaries = "\n".join([
        f"• [{l.get('category','?')} | {l.get('severity','?')}] {l['title']}"
        for l in lessons
    ])
    return (
        f"**Lecciones encontradas para: {query}**\n\n"
        f"*(IA no disponible — reinstala llama-cpp-python con un wheel compatible)*\n\n"
        f"{summaries}"
    )
