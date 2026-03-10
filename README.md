# Evaluador de FI — M2

Aplicación web para evaluar participaciones en el **FI** del M2 de **PLS**. Genera retroalimentación personalizada en prosa, calcula puntajes según la rúbrica institucional y sugiere recursos de apoyo según las áreas de mejora de cada estudiante.

---

## Características principales

| Característica | Descripción |
|---|---|
| **Evaluación por criterios** | Cognitivo (40 pts), Actitudinal (15 pts), Comunicativo (15 pts), Colaborativo (15 pts), Pensamiento Crítico (15 pts) + Originalidad (deducción). |
| **Radio buttons descriptivos** | Cada métrica muestra las opciones directamente con sus descriptores de rúbrica, sin dropdowns numéricos. |
| **Retroalimentación en prosa** | Genera texto personalizado, cálido y empático que ensambla frases según las métricas seleccionadas. |
| **Sugerencia inteligente de recursos** | Selecciona automáticamente 1-2 recursos de apoyo de las áreas más débiles del estudiante, integrados en la prosa. |
| **Resumen con niveles** | Muestra puntajes y niveles de desempeño (Experto, Capacitado, Aceptable, etc.) con etiquetas visuales. |
| **Exportación** | Descarga la retroalimentación como archivo `.md` con el nombre del alumno. |
| **Persistencia** | Guarda cada evaluación en `data.csv` para seguimiento histórico. |
| **Feedback editable** | El texto generado es editable antes de guardar o exportar. |

---

## Arquitectura del proyecto

```
M2_S4ForoPL_Evaluator/
├── app.py                  # Aplicación principal Streamlit (~840 líneas)
├── resources.json          # Banco de recursos de apoyo (6 recursos, JSON)
├── data.csv                # Almacenamiento de evaluaciones (generado automáticamente)
├── requirements.txt        # Dependencias de Python
├── metricas_criterios.md   # Documentación de métricas y criterios
├── templates/
│   └── feedback_template.md  # Plantilla base de retroalimentación
│
└── UV/                     # Entorno virtual (no versionado)
```

---

## Tecnología

| Componente | Tecnología | Versión |
|---|---|---|
| **Lenguaje** | Python | 3.9+ |
| **Framework web** | Streamlit | ≥ 1.0 |
| **Entorno virtual** | uv | — |
| **Almacenamiento** | Archivos locales (CSV, JSON) | — |
| **Dependencias** | `streamlit`, `pandas`, `Jinja2`, `python-dotenv` | — |

> **Nota:** La aplicación no utiliza base de datos ni servicios externos. Todo se ejecuta localmente.

---

## Instalación y ejecución

### 1. Clonar el repositorio

```powershell
git clone https://github.com/jorgetzec/M2_S4ForoPL_Evaluator.git
cd M2_S4ForoPL_Evaluator
```

### 2. Crear entorno virtual con `uv`

```powershell
uv venv UV
UV\Scripts\activate
uv pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```powershell
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

---

## Flujo de uso

### Paso 1 — Datos del alumno
Ingresa el **nombre del alumno**, la **fecha** y la **firma del asesor** (multilínea). Presiona **Iniciar evaluación**.

### Paso 2 — Evaluación por criterios
Para cada uno de los 5 criterios, selecciona las métricas usando los radio buttons con descriptores de la rúbrica:

1. **Cognitivo** (40 pts) — Aportaciones, respuestas a preguntas detonadoras, opiniones a compañeros, conclusión.
2. **Actitudinal** (15 pts) — Cumplimiento de instrucciones del foro (checklist).
3. **Comunicativo** (15 pts) — Claridad, extensión, reflexión, netiqueta, errores de redacción.
4. **Colaborativo** (15 pts) — Días de participación, promoción de diálogo.
5. **Pensamiento Crítico** (15 pts) — Argumentación, retroalimentación a compañeros, análisis de ideas.

Adicionalmente, selecciona el nivel de **Originalidad** (deducción de 0 a -25 pts).

### Paso 3 — Resumen y retroalimentación
- El **resumen** muestra los puntajes y niveles de cada criterio con etiquetas 🏷️.
- Presiona **Generar retroalimentación** para obtener el texto en prosa.
- El texto generado es empático, usa conectores naturales y sugiere 1-2 recursos de apoyo basados en las áreas más débiles.
- Puedes **editar** el texto antes de guardarlo.

### Paso 4 — Guardar y exportar
- **Guardar evaluación** → almacena los datos en `data.csv`.
- **Descargar .md** → descarga la retroalimentación como archivo Markdown.
- **Reiniciar evaluación** → limpia el formulario para evaluar a otro alumno.

---

## Archivos de datos

### `data.csv`
Almacena cada evaluación con las columnas:

```
alumno, fecha, firma, cognitivo, cog_level, actitudinal, act_level,
comunicativo, com_level, colaborativo, colab_level, pensamiento_critico,
critico_level, originalidad_deduccion, orig_level, total, feedback
```

---

## Licencia

Proyecto interno para uso educativo en **PLS**. No destinado a distribución comercial.
