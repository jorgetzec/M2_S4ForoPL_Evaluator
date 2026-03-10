# Evaluador de Foro de Integración — Módulo 2

Aplicación web para evaluar participaciones en el **Foro de Integración** del Módulo 2 de **Prepa en Línea SEP**. Genera retroalimentación personalizada en prosa, calcula puntajes según la rúbrica institucional y sugiere recursos de apoyo según las áreas de mejora de cada estudiante.

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
20260211_m2_foro_prepaenlinea-evaluador/
├── app.py                  # Aplicación principal Streamlit (~840 líneas)
├── resources.json          # Banco de recursos de apoyo (6 recursos, JSON)
├── data.csv                # Almacenamiento de evaluaciones (generado automáticamente)
├── requirements.txt        # Dependencias de Python
├── metricas_criterios.md   # Documentación de métricas y criterios
│
├── docs/                   # Documentación de referencia
│   ├── M2_S4_foro_integracion_rubrica.md       # Rúbrica oficial del foro
│   ├── M2_S4_foro_integracion_instrucciones.md # Instrucciones de la actividad
│   ├── 20261802_retroalimentacion_ejemplo.md   # Ejemplo de retroalimentación ideal
│   ├── 20261802_Propuesta_mejorada.md          # Propuesta de diseño mejorada
│   ├── 20260218_Propuesta_inicial.md           # Propuesta de diseño inicial
│   ├── 20260218_caterogrias_rubrica_Excel.md   # Categorías de rúbrica (Excel)
│   ├── 20260218_info_evaluador_foro.md         # Información general del evaluador
│   └── Compilado M02_RED_DSAyDC.csv           # Compilado de recursos educativos M02
│
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
git clone <url-del-repositorio>
cd 20260211_m2_foro_prepaenlinea-evaluador
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

## Lógica de puntuación

### Cognitivo (40 pts)
Utiliza un sistema de **puntajes ordinales** para cada métrica (respuesta a PD1, PD2, opiniones, conclusión) y una cascada que evita caídas abruptas de puntos:

| Nivel | Puntos | Criterio principal |
|---|---|---|
| Experto | 40 | ≥5 aportaciones, fundamentos claros en PD1/PD2, ≥2 opiniones fundamentadas, conclusión clara |
| Capacitado | 34 | ≥4 aportaciones, respuestas generales, ≥2 opiniones generales |
| Aceptable | 32 | ≥3 aportaciones, respuestas superficiales, ≥1 opinión |
| Aprendiz | 28 | ≥3 aportaciones, respuestas vagas |
| Requiere apoyo | 24 | ≥1 aportación |
| No evaluable | 0 | Sin aportaciones |

### Otros criterios
Comunicativo, Colaborativo y Pensamiento Crítico usan un sistema de **puntuación compuesta** que suma puntajes ordinales de cada sub-métrica y los mapea a niveles (Excelente, Bien, Regular, Suficiente, Insuficiente).

### Actitudinal (15 pts)
Basado en el porcentaje de instrucciones cumplidas (checklist de 10 ítems).

### Originalidad (deducción)
Aplica deducciones de -6.25 a -25 puntos según el nivel de citas y referencias.

---

## Banco de recursos (`resources.json`)

El archivo `resources.json` contiene **6 recursos educativos** para el Foro de Integración del M02, organizados por criterio:

| Criterio | Recurso | Tipo |
|---|---|---|
| Cognitivo | El resumen | Artículo |
| Cognitivo | Características del relato, resumen y reseña | Infografía |
| Comunicativo | Comunicación asertiva | Infografía |
| Comunicativo | Escribir y hablar bien en la era digital | Artículo |
| Comunicativo | Habilidades de comunicación en la digitalidad | Artículo |
| Colaborativo | Participación en foros virtuales | Guía |

La función `suggest_resources()` selecciona automáticamente 1-2 recursos de las áreas con **menor puntaje relativo** y los integra en la retroalimentación en prosa (sin viñetas).

Para agregar más recursos, edita `resources.json` siguiendo el formato:

```json
{
  "id": "r7",
  "criterio": "Comunicativo",
  "etiqueta": "Nombre del recurso",
  "link": "https://ejemplo.com",
  "descripcion": "Breve descripción del recurso.",
  "tags": ["tag1", "tag2"],
  "referencia": "Cita APA del recurso."
}
```

---

## Archivos de datos

### `data.csv`
Almacena cada evaluación con las columnas:

```
alumno, fecha, firma, cognitivo, cog_level, actitudinal, act_level,
comunicativo, com_level, colaborativo, colab_level, pensamiento_critico,
critico_level, originalidad_deduccion, orig_level, total, feedback
```

### `docs/Compilado M02_RED_DSAyDC.csv`
Compilado maestro de recursos educativos digitales del Módulo 2. Contiene los recursos originales de los que se seleccionaron los del Foro de Integración.

---

## Documentación de referencia

| Archivo | Contenido |
|---|---|
| `docs/M2_S4_foro_integracion_rubrica.md` | Rúbrica oficial con niveles, puntajes y descriptores |
| `docs/M2_S4_foro_integracion_instrucciones.md` | Instrucciones de la actividad para el alumno |
| `docs/20261802_retroalimentacion_ejemplo.md` | Ejemplo de retroalimentación ideal en prosa |
| `metricas_criterios.md` | Documentación técnica de métricas y criterios |

---

## Personalización

### Modificar la rúbrica
Los puntajes y niveles están definidos directamente en `app.py` dentro de cada sección de criterio. Busca los diccionarios `_pd_score`, `_arg_s`, `_ret_s`, etc., para ajustar la ponderación.

### Modificar la prosa de retroalimentación
Las frases se ensamblan en la sección `# GENERAR RETROALIMENTACIÓN EN PROSA` de `app.py`. Cada métrica tiene un diccionario que mapea la opción seleccionada a una frase específica (ej. `_pd1_txt`, `_conc_txt`, `_arg_txt`).

### Agregar nuevos criterios
1. Agrega la sección con `st.header()` y los radio buttons.
2. Define la lógica de puntuación.
3. Agrega la generación de prosa en la sección de retroalimentación.
4. Incluye el criterio en el diccionario `_scores` para que los recursos se sugieran correctamente.

---

## Licencia

Proyecto interno para uso educativo en **Prepa en Línea SEP**. No destinado a distribución comercial.
