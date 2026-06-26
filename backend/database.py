import sqlite3
import json
import os
from typing import List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "lessons.db")

SEED_LESSONS = [
    {
        "title": "Proveedor de acero incumplió plazos de entrega",
        "description": "El proveedor Aceros del Sur retrasó la entrega de barras corrugadas 3 semanas, paralizando la estructura. El área crítica de columnas quedó sin material en plena faena.",
        "cause": "Contrato sin cláusulas de penalización por retraso y sin proveedor alternativo identificado en el plan de compras.",
        "solution": "Se consiguió proveedor alternativo con precio 12% mayor. Se perdieron 3 semanas críticas del cronograma.",
        "project_name": "Torre Andes",
        "project_type": "Edificación",
        "created_by": "R. González (Jefe de Obra)",
        "category": "Proveedores",
        "severity": "Alta",
        "phase": "Estructura",
        "tags": json.dumps(["acero", "proveedor", "plazo", "estructura"]),
    },
    {
        "title": "Error de diseño en fundaciones por suelo blando no detectado",
        "description": "El estudio de suelos no identificó una zona de relleno en el sector norte. Se requirió pilotaje adicional no contemplado en presupuesto.",
        "cause": "Estudio de suelos insuficiente con pocos puntos de muestreo. El profesional contratado realizó solo 4 calicatas para un terreno de 2000 m².",
        "solution": "Pilotaje de emergencia con aumento del 8% en costo de fundaciones. Nueva política exige mínimo 1 calicata por 200 m².",
        "project_name": "Edificio Balmaceda",
        "project_type": "Habitacional",
        "created_by": "C. Morales (Ing. Estructural)",
        "category": "Diseño",
        "severity": "Alta",
        "phase": "Fundaciones",
        "tags": json.dumps(["fundaciones", "suelo", "diseño", "pilotaje", "estudio de suelos"]),
    },
    {
        "title": "Accidente en trabajo en altura por EPP inadecuado",
        "description": "Trabajador sufrió caída de 1.5 metros desde andamio por no usar arnés correctamente. Lesión leve pero con detención de faena por fiscalización.",
        "cause": "Falta de supervisión en turno tarde y capacitación insuficiente en uso de arnés tipo Y. El capataz de turno no verificó el EPP antes del turno.",
        "solution": "Protocolo de doble verificación de EPP antes de subir. Check-list obligatorio firmado por capataz. Capacitación semanal de 15 minutos en seguridad.",
        "project_name": "Centro Comercial Norte",
        "project_type": "Industrial",
        "created_by": "P. Sánchez (Prev. de Riesgos)",
        "category": "Seguridad",
        "severity": "Alta",
        "phase": "Estructura",
        "tags": json.dumps(["seguridad", "altura", "EPP", "arnés", "accidente"]),
    },
    {
        "title": "Paralización por lluvias invernales sin plan de contingencia",
        "description": "Las lluvias de julio detuvieron las excavaciones 2 semanas al inundarse el sector de excavación. No se contaba con bombas de achique ni cubierta temporal.",
        "cause": "El cronograma no consideró el período de lluvias de la zona ni se incluyó sistema de drenaje provisional en el plan de faenas.",
        "solution": "Instalación de bombas de achique de emergencia. Replanificación para ejecutar trabajos interiores durante período de lluvias.",
        "project_name": "Planta Industrial Maipú",
        "project_type": "Industrial",
        "created_by": "A. Torres (Jefe de Obra)",
        "category": "Plazo",
        "severity": "Media",
        "phase": "Fundaciones",
        "tags": json.dumps(["lluvia", "plazo", "excavación", "contingencia", "drenaje"]),
    },
    {
        "title": "Hormigón H40 exitoso con aditivo superplastificante en zona sísmica",
        "description": "Uso de aditivo superplastificante permitió alcanzar resistencia H40 manteniendo trabajabilidad óptima en condiciones de alta temperatura (30°C).",
        "cause": "Investigación previa y pruebas de laboratorio realizadas durante la etapa de diseño de mezcla.",
        "solution": "Protocolo de mezcla documentado y replicable. Se redujo la relación agua/cemento de 0.45 a 0.38 sin perder asentamiento.",
        "project_name": "Torre Costanera II",
        "project_type": "Edificación",
        "created_by": "M. Vargas (Ing. de Hormigón)",
        "category": "Calidad",
        "severity": "Baja",
        "phase": "Estructura",
        "tags": json.dumps(["hormigón", "calidad", "sismo", "aditivo", "resistencia"]),
    },
    {
        "title": "Sobrecosto por cambios de proyecto durante ejecución",
        "description": "El cliente solicitó 23 modificaciones al diseño original durante la ejecución, generando un sobrecosto del 15% y retraso de 6 semanas.",
        "cause": "Diseño no estaba finalizado al iniciar la obra. El cliente no validó formalmente los planos definitivos antes del inicio.",
        "solution": "Cláusula de órdenes de cambio en el contrato con valorización y extensión de plazo acordados antes de ejecutar cualquier modificación.",
        "project_name": "Hotel Los Leones",
        "project_type": "Edificación",
        "created_by": "F. Reyes (Administrador de Contrato)",
        "category": "Costo",
        "severity": "Alta",
        "phase": "Planificación",
        "tags": json.dumps(["costo", "contrato", "cambios", "planificación", "cliente"]),
    },
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            cause TEXT DEFAULT '',
            solution TEXT DEFAULT '',
            project_name TEXT DEFAULT '',
            project_type TEXT DEFAULT 'Otro',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            created_by TEXT DEFAULT '',
            category TEXT DEFAULT 'Sin clasificar',
            severity TEXT DEFAULT 'Sin clasificar',
            phase TEXT DEFAULT 'Sin clasificar',
            tags TEXT DEFAULT '[]',
            embedding TEXT DEFAULT NULL,
            ai_processed INTEGER DEFAULT 0
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    if count == 0:
        for lesson in SEED_LESSONS:
            conn.execute("""
                INSERT INTO lessons (title, description, cause, solution, project_name, project_type, created_by,
                                     category, severity, phase, tags, ai_processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                lesson["title"], lesson["description"], lesson["cause"], lesson["solution"],
                lesson["project_name"], lesson["project_type"], lesson["created_by"],
                lesson["category"], lesson["severity"], lesson["phase"], lesson["tags"]
            ))
        conn.commit()
    conn.close()


def insert_lesson(data: dict) -> int:
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO lessons (title, description, cause, solution, project_name, project_type, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"], data["description"], data.get("cause", ""),
        data.get("solution", ""), data.get("project_name", ""),
        data.get("project_type", "Otro"), data.get("created_by", "")
    ))
    lesson_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lesson_id


def update_lesson_ai(lesson_id: int, category: str, severity: str, phase: str,
                     tags: List[str], embedding: List[float]):
    conn = get_connection()
    conn.execute("""
        UPDATE lessons
        SET category = ?, severity = ?, phase = ?, tags = ?, embedding = ?, ai_processed = 1
        WHERE id = ?
    """, (category, severity, phase, json.dumps(tags), json.dumps(embedding) if embedding else None, lesson_id))
    conn.commit()
    conn.close()


def update_lesson_embedding(lesson_id: int, embedding: List[float]):
    conn = get_connection()
    conn.execute("UPDATE lessons SET embedding = ? WHERE id = ?",
                 (json.dumps(embedding), lesson_id))
    conn.commit()
    conn.close()


def get_all_lessons(category: Optional[str] = None, severity: Optional[str] = None) -> List[dict]:
    conn = get_connection()
    query = "SELECT * FROM lessons WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_lesson_by_id(lesson_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_lesson(lesson_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    conn.commit()
    conn.close()


def get_lessons_with_embeddings() -> List[Tuple[dict, List[float]]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM lessons WHERE embedding IS NOT NULL AND embedding != 'null'").fetchall()
    conn.close()
    result = []
    for row in rows:
        lesson = dict(row)
        try:
            embedding = json.loads(lesson["embedding"])
            if embedding:
                result.append((lesson, embedding))
        except Exception:
            pass
    return result


def get_lessons_without_embeddings() -> List[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM lessons WHERE embedding IS NULL OR embedding = 'null'").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    ai_done = conn.execute("SELECT COUNT(*) FROM lessons WHERE ai_processed = 1").fetchone()[0]
    by_category = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM lessons GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    by_severity = conn.execute(
        "SELECT severity, COUNT(*) as cnt FROM lessons GROUP BY severity ORDER BY cnt DESC"
    ).fetchall()
    by_type = conn.execute(
        "SELECT project_type, COUNT(*) as cnt FROM lessons GROUP BY project_type ORDER BY cnt DESC"
    ).fetchall()
    recent = conn.execute(
        "SELECT title, category, severity, created_at FROM lessons ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "ai_processed": ai_done,
        "by_category": {row[0]: row[1] for row in by_category},
        "by_severity": {row[0]: row[1] for row in by_severity},
        "by_type": {row[0]: row[1] for row in by_type},
        "recent": [dict(r) for r in recent],
    }
