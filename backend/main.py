import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ai_service import classify_lesson, generate_report, get_embedding, check_ai
from database import (delete_lesson, get_all_lessons, get_lesson_by_id,
                      get_lessons_with_embeddings,
                      get_stats, init_db, insert_lesson, update_lesson_ai)
from models import LessonCreate, ReportRequest, SearchRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="GCIA - Gestión de Conocimiento en Construcción", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")


@app.on_event("startup")
async def startup():
    init_db()


# ----- Frontend pages -----

@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/register")
def serve_register():
    return FileResponse(FRONTEND_DIR / "register.html")

@app.get("/search")
def serve_search():
    return FileResponse(FRONTEND_DIR / "search.html")

@app.get("/report")
def serve_report():
    return FileResponse(FRONTEND_DIR / "report.html")


# ----- Helpers -----

def format_lesson(lesson: dict) -> dict:
    tags = lesson.get("tags", "[]")
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = []
    return {
        "id": lesson["id"],
        "title": lesson["title"],
        "description": lesson["description"],
        "cause": lesson.get("cause", ""),
        "solution": lesson.get("solution", ""),
        "project_name": lesson.get("project_name", ""),
        "project_type": lesson.get("project_type", ""),
        "created_at": lesson.get("created_at", ""),
        "created_by": lesson.get("created_by", ""),
        "category": lesson.get("category", "Sin clasificar"),
        "severity": lesson.get("severity", "Sin clasificar"),
        "phase": lesson.get("phase", "Sin clasificar"),
        "tags": tags,
        "ai_processed": bool(lesson.get("ai_processed", 0)),
    }


# ----- API Routes -----

@app.get("/api/status")
async def api_status():
    return {"ai": await check_ai()}


@app.get("/api/stats")
def api_stats():
    return get_stats()


@app.post("/api/lessons")
async def create_lesson(lesson: LessonCreate):
    lesson_id = insert_lesson(lesson.model_dump())
    asyncio.create_task(_process_lesson_ai(lesson_id, lesson))
    return {"id": lesson_id, "message": "Lección registrada. La IA está clasificando en segundo plano..."}


async def _process_lesson_ai(lesson_id: int, lesson: LessonCreate):
    try:
        classification = await classify_lesson(
            lesson.title, lesson.description, lesson.cause or "", lesson.solution or ""
        )
        update_lesson_ai(
            lesson_id,
            classification.get("category", "Sin clasificar"),
            classification.get("severity", "Sin clasificar"),
            classification.get("phase", "Sin clasificar"),
            classification.get("tags", []),
            [],
        )
        logger.info(f"Lección {lesson_id} clasificada: {classification.get('category')}")
    except Exception as e:
        logger.error(f"Error procesando lección {lesson_id}: {e}")


@app.get("/api/lessons")
def list_lessons(category: Optional[str] = None, severity: Optional[str] = None):
    lessons = get_all_lessons(category=category, severity=severity)
    return [format_lesson(l) for l in lessons]


@app.get("/api/lessons/{lesson_id}")
def get_lesson(lesson_id: int):
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    return format_lesson(lesson)


@app.delete("/api/lessons/{lesson_id}")
def remove_lesson(lesson_id: int):
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    delete_lesson(lesson_id)
    return {"message": "Lección eliminada correctamente"}


@app.post("/api/search")
async def search_lessons(request: SearchRequest):
    all_with_embeddings = get_lessons_with_embeddings()

    if all_with_embeddings:
        query_embedding = await get_embedding(request.query)
    else:
        query_embedding = None

    if query_embedding and all_with_embeddings:
        query_vec = np.array(query_embedding, dtype=np.float32)
        scored = []
        for lesson, embedding in all_with_embeddings:
            if request.category and lesson.get("category") != request.category:
                continue
            if request.severity and lesson.get("severity") != request.severity:
                continue
            lesson_vec = np.array(embedding, dtype=np.float32)
            norm = np.linalg.norm(query_vec) * np.linalg.norm(lesson_vec)
            score = float(np.dot(query_vec, lesson_vec) / (norm + 1e-10))
            scored.append((lesson, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {"lesson": format_lesson(l), "score": round(s, 4)}
            for l, s in scored[:request.top_k]
        ]

    # Fallback: keyword search over all lessons
    lessons = get_all_lessons(category=request.category, severity=request.severity)
    query_lower = request.query.lower()
    results = []
    for lesson in lessons:
        text = f"{lesson.get('title','')} {lesson.get('description','')} {lesson.get('cause','')} {lesson.get('solution','')}".lower()
        hits = sum(1 for word in query_lower.split() if word in text)
        if hits > 0:
            results.append({"lesson": format_lesson(lesson), "score": round(hits / len(query_lower.split()), 2)})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:request.top_k]


@app.post("/api/report")
async def generate_project_report(request: ReportRequest):
    search_results = await search_lessons(SearchRequest(query=request.query, top_k=request.top_k))
    lessons = [r["lesson"] for r in search_results]
    report_text = await generate_report(request.query, lessons, request.project_type)
    return {
        "query": request.query,
        "lessons_found": len(lessons),
        "report": report_text,
        "lessons": lessons,
    }
