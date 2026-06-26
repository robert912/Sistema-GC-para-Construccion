# GCIA — Sistema de Gestión de Conocimiento para Construcción

Sistema interno de **Lecciones Aprendidas con IA 100% local** para empresas constructoras. Permite registrar, clasificar automáticamente y consultar el conocimiento generado en cada proyecto de obra. No se envía ningún dato a internet.

---

## Funcionalidades

| # | Función | Descripción |
|---|---|---|
| 1 | **Clasificación automática** | La IA asigna categoría, severidad y fase de obra al registrar una lección |
| 2 | **Búsqueda por palabras clave** | Consulta en lenguaje natural sobre el historial de lecciones |
| 3 | **Informe ejecutivo** | La IA genera un resumen con riesgos y recomendaciones antes de iniciar un proyecto |

**Categorías:** Plazo / Costo / Seguridad / Calidad / Proveedores / Diseño  
**Severidades:** Alta / Media / Baja  
**Fases:** Planificación / Fundaciones / Estructura / Instalaciones / Terminaciones / Cierre

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python 3.10+ + FastAPI |
| Base de datos | SQLite |
| Motor de IA | llama-cpp-python + modelo GGUF local |
| Frontend | HTML + CSS + JavaScript (sin frameworks) |

---

## Instalación (primera vez)

### 1. Verificar Python

```cmd
python --version
```

Se requiere Python 3.10 o superior. Descarga desde python.org marcando "Add to PATH".

---

### 2. Instalar dependencias base

```cmd
setup.bat
```

Instala `fastapi`, `uvicorn`, `numpy`, `pydantic` y el resto de librerías.

---

### 3. Instalar llama-cpp-python

**En Windows** la forma más simple es descargar el wheel precompilado:

1. Ve a: https://github.com/abetlen/llama-cpp-python/releases
2. Descarga el archivo `llama_cpp_python-X.X.X-**py3-none-win_amd64**.whl` (funciona con cualquier versión de Python 3)
3. Colócalo en la carpeta `wheels/` del proyecto
4. Ejecuta `setup.bat` — lo detecta e instala automáticamente

> Si durante la instalación aparece un error de ruta demasiado larga, ejecuta primero:
> ```cmd
> mkdir C:\t && set TEMP=C:\t && set TMP=C:\t
> pip install llama-cpp-python
> ```

---

### 4. Colocar el modelo GGUF

Copia tu archivo `.gguf` en la carpeta `modelo/`:

```
GCIA/
└── modelo/
    └── Llama-3.2-3B-Instruct-Q4_K_M.gguf
```

El sistema detecta automáticamente cualquier archivo `.gguf` en esa carpeta.

---

### 5. Iniciar el sistema

```cmd
start.bat
```

Abre automáticamente el navegador en `http://localhost:8000`. El badge mostrará **IA activa** cuando el modelo esté listo.

> La primera clasificación tarda unos segundos mientras el modelo carga en memoria. Las siguientes son inmediatas.

---

## Uso diario

Solo ejecutar `start.bat`. No hace falta repetir la instalación.

```
http://localhost:8000           → Dashboard
http://localhost:8000/register  → Registrar lección
http://localhost:8000/search    → Buscar
http://localhost:8000/report    → Informe ejecutivo
```

---

## Cambiar el modelo

No es necesario modificar ningún archivo de código. El sistema carga automáticamente el primer `.gguf` que encuentre en `modelo/` (orden alfabético).

**Para cambiar de modelo:**
1. Copia el nuevo `.gguf` en la carpeta `modelo/`
2. Elimina o renombra el anterior (opcional)
3. Reinicia `start.bat`

**Para elegir un modelo específico sin borrar los demás:**
```cmd
set LLAMA_MODEL_PATH=e:\Proyecto_Universidad\GCIA\modelo\OtroModelo.gguf
start.bat
```

### Modelos recomendados

Descarga modelos GGUF desde [Hugging Face](https://huggingface.co/models?library=gguf).

| Modelo | Tamaño archivo | RAM necesaria |
|---|---|---|
| Llama 3.2 3B Instruct Q4_K_M *(actual)* | ~2 GB | ~3 GB |
| Llama 3.2 3B Instruct Q8_0 | ~3.4 GB | ~4.5 GB |
| Mistral 7B Instruct Q4_K_M | ~4.1 GB | ~5 GB |

---

## Estructura del proyecto

```
GCIA/
├── backend/
│   ├── main.py           # API REST + servidor frontend
│   ├── database.py       # Base de datos SQLite
│   ├── ai_service.py     # Motor de IA (carga el modelo GGUF)
│   ├── models.py         # Esquemas de datos
│   └── requirements.txt
├── frontend/
│   ├── index.html        # Dashboard
│   ├── register.html     # Registro de lecciones
│   ├── search.html       # Búsqueda
│   ├── report.html       # Informe ejecutivo
│   └── static/style.css
├── modelo/               # Archivos .gguf (modelo de IA)
├── wheels/               # Wheel precompilada de llama-cpp-python
├── setup.bat             # Instalación de dependencias
├── start.bat             # Inicio del sistema
└── README.md
```

---

## Sin modelo disponible

Si el archivo `.gguf` no está o `llama-cpp-python` no está instalado, el sistema funciona con capacidades reducidas:

- Registro de lecciones sin clasificación automática
- Búsqueda por palabras clave
- Informes muestran lista de lecciones sin resumen narrativo

---

## Modelo de gestión del conocimiento (Probst)

| Bloque | Implementación en GCIA |
|---|---|
| **Identificar** | Perfil de lecciones por tipo de obra y fase |
| **Adquirir** | Formulario de registro durante y post-proyecto |
| **Desarrollar** | La IA clasifica y enriquece cada lección |
| **Distribuir** | Portal de búsqueda accesible para todo el equipo |
| **Utilizar** | El jefe consulta antes de planificar y durante ejecución |
| **Retener** | Base de datos que no depende de personas |

---

## Licencia

Proyecto académico — Universidad de Santiago de Chile (USACH).