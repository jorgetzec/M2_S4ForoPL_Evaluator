import streamlit as st
import json
from datetime import datetime
import os

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, 'data.csv')
RESOURCES_FILE = os.path.join(BASE_DIR, 'resources.json')

st.set_page_config(page_title='Evaluador de Foro', layout='wide')

# Load resources
if os.path.exists(RESOURCES_FILE):
    with open(RESOURCES_FILE, 'r', encoding='utf-8') as f:
        RESOURCES = json.load(f)
else:
    RESOURCES = []


def suggest_resources(scores):
    """Pick 1-2 resources from the weakest criteria areas."""
    # Sort criteria by score ascending to find weakest
    sorted_criteria = sorted(scores.items(), key=lambda x: x[1])
    selected = []
    seen_ids = set()
    for criterio, _pts in sorted_criteria:
        matches = [r for r in RESOURCES if r.get('criterio') == criterio]
        for r in matches:
            if r['id'] not in seen_ids:
                selected.append(r)
                seen_ids.add(r['id'])
                if len(selected) >= 2:
                    return selected
    return selected


def save_evaluation(row):
    import csv
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ============== INTERFAZ STREAMLIT ==============

st.title('Evaluador de Foro — Prototipo Streamlit (v4)')

with st.form('header_form', clear_on_submit=False):
    alumno = st.text_input('Nombre del alumno', key='alumno_input')
    fecha = st.date_input('Fecha', value=datetime.today(), key='fecha_input')
    firma = st.text_area('Firma del asesor (formato multilínea)',
                         value='Pedro P.\nAsesor Virtual\nM2C1G82-021.',
                         height=100,
                         key='firma_input',
                         placeholder='Pedro P.\nAsesor Virtual\nM2C1G82-021.')
    submitted = st.form_submit_button('Iniciar evaluación')

if submitted or 'started' in st.session_state:
    st.session_state['started'] = True

    if not alumno:
        st.warning('Por favor ingresa el nombre del alumno.')
        st.stop()

    # ===================================================================
    # ===== 1. COGNITIVO (máx 40 puntos) ================================
    # ===================================================================
    st.header('1. Cognitivo (máx 40 puntos)')
    st.info('Base: máximo 5 aportaciones (pregunta 1, pregunta 2, 2 opiniones de compañeros, 1 conclusión)')

    with st.expander('Métricas Cognitivas', expanded=True):
        st.markdown('**Total de aportaciones**')
        cog_aportaciones = st.radio(
            'Número de aportaciones',
            options=[0, 1, 2, 3, 4, 5],
            horizontal=True,
            key='cog_aport',
            label_visibility='collapsed'
        )

        st.markdown('---')
        st.markdown('**Responde Pregunta 1:** _¿Para qué me sirve saber las diferencias entre relato, resumen y reseña?_')
        cog_responde_pd1 = st.radio(
            'Responde PD1',
            options=['No responde', 'Vagamente', 'Superficialmente', 'De manera general', 'Con fundamentos claros'],
            horizontal=True,
            key='cog_pd1',
            label_visibility='collapsed'
        )

        st.markdown('**Responde Pregunta 2:** _¿Cómo las puedo aplicar en mi contexto de vida?_')
        cog_responde_pd2 = st.radio(
            'Responde PD2',
            options=['No responde', 'Vagamente', 'Superficialmente', 'De manera general', 'Con fundamentos claros'],
            horizontal=True,
            key='cog_pd2',
            label_visibility='collapsed'
        )

        st.markdown('---')
        st.markdown('**Opiniones a compañeros**')
        cog_opiniones = st.radio(
            'Número de opiniones',
            options=[0, 1, 2],
            horizontal=True,
            key='cog_opiniones',
            label_visibility='collapsed'
        )

        st.markdown('**Calidad de las opiniones**')
        cog_opinion_fund = st.radio(
            'Fundamentación de opiniones',
            options=['No aplica', 'Sin fundamento', 'Opinión general', 'Opinión fundamentada y objetiva'],
            horizontal=True,
            key='cog_fund',
            label_visibility='collapsed'
        )

        st.markdown('---')
        st.markdown('**Conclusión sobre la temática**')
        cog_conclusion = st.radio(
            'Tipo de conclusión',
            options=['No incluye', 'Comentario sin conclusión clara', 'Conclusión vaga', 'Conclusión general', 'Conclusión clara y completa'],
            horizontal=True,
            key='cog_conclusion',
            label_visibility='collapsed'
        )

        # ------------------------------------------------------------------
        # Determine Cognitivo level — Rubric cascade (top-down, flexible)
        # ------------------------------------------------------------------
        # Map text values to ordinal scores for flexible matching
        _pd_score = {
            'No responde': 0, 'Vagamente': 1, 'Superficialmente': 2,
            'De manera general': 3, 'Con fundamentos claros': 4
        }
        _op_score = {
            'No aplica': 0, 'Sin fundamento': 1, 'Opinión general': 2,
            'Opinión fundamentada y objetiva': 3
        }
        _conc_score = {
            'No incluye': 0, 'Comentario sin conclusión clara': 1,
            'Conclusión vaga': 2, 'Conclusión general': 3,
            'Conclusión clara y completa': 4
        }

        pd1_s = _pd_score[cog_responde_pd1]
        pd2_s = _pd_score[cog_responde_pd2]
        op_s = _op_score[cog_opinion_fund]
        conc_s = _conc_score[cog_conclusion]

        # Experto (40): 5 aportaciones, PD1≥4, PD2≥4, 2 opiniones fundadas≥3, conclusión≥4
        # Capacitado (34): 4 aport, PD1≥3, PD2≥3, 2 opiniones≥2, conclusión≥3
        # Aceptable (32): 3 aport, PD1≥2, PD2≥2, 1 opinión≥1, conclusión≥2
        # Aprendiz (28): 3 aport, PD1≥1, PD2≥1, opinión≥1, conclusión≥1
        # Requiere apoyo (24): 1 aport
        # No evaluable (0): 0 aport

        cog_level = 'No evaluable'
        cog_pts = 0

        if cog_aportaciones == 0:
            cog_level = 'No evaluable'
            cog_pts = 0
        elif (cog_aportaciones >= 5 and pd1_s >= 4 and pd2_s >= 4 and
              cog_opiniones >= 2 and op_s >= 3 and conc_s >= 4):
            cog_level = 'Experto'
            cog_pts = 40
        elif (cog_aportaciones >= 4 and pd1_s >= 3 and pd2_s >= 3 and
              cog_opiniones >= 2 and op_s >= 2 and conc_s >= 3):
            cog_level = 'Capacitado'
            cog_pts = 34
        elif (cog_aportaciones >= 3 and pd1_s >= 2 and pd2_s >= 2 and
              cog_opiniones >= 1 and conc_s >= 2):
            cog_level = 'Aceptable'
            cog_pts = 32
        elif (cog_aportaciones >= 3 and pd1_s >= 1 and pd2_s >= 1 and
              cog_opiniones >= 1 and conc_s >= 1):
            cog_level = 'Aprendiz'
            cog_pts = 28
        elif cog_aportaciones >= 1:
            cog_level = 'Requiere apoyo'
            cog_pts = 24

        st.success(f'**Nivel Cognitivo:** {cog_level} → {cog_pts} / 40 puntos')

    # ===================================================================
    # ===== 2. ACTITUDINAL (máx 15 puntos) ==============================
    # ===================================================================
    st.header('2. Actitudinal (máx 15 puntos)')
    st.info('Cumplimiento de instrucciones del foro')

    ACTITUDINAL_INSTRUCTIONS = [
        'Usa creatividad y originalidad',
        'Intervenciones generan diversidad',
        'Evita subir documentos (usa enlaces)',
        'Respeta netiqueta',
        'Opiniones breves (1-3 párrafos)',
        'Redacción previa (sin errores plataforma)'
    ]

    with st.expander('Instrucciones a verificar', expanded=True):
        instructions_check = {}
        cols = st.columns(2)
        for i, instr in enumerate(ACTITUDINAL_INSTRUCTIONS):
            col = cols[i % 2]
            with col:
                instructions_check[instr] = st.checkbox(instr, key=f'act_{i}')

        cumplidas = sum(1 for v in instructions_check.values() if v)
        total_instr = len(ACTITUDINAL_INSTRUCTIONS)
        porcentaje = (cumplidas / total_instr) * 100

        if cumplidas == 0:
            act_level = 'No evaluable'
            act_pts = 0
        elif porcentaje == 100:
            act_level = 'Excelente'
            act_pts = 15
        elif porcentaje >= 85:
            act_level = 'Bien'
            act_pts = 14
        elif porcentaje >= 71:
            act_level = 'Regular'
            act_pts = 12
        elif porcentaje >= 57:
            act_level = 'Suficiente'
            act_pts = 10
        else:
            act_level = 'Insuficiente'
            act_pts = 9

        st.write(f'Instrucciones cumplidas: {cumplidas}/{total_instr} ({porcentaje:.0f}%)')
        st.success(f'**Nivel Actitudinal:** {act_level} → {act_pts} / 15 puntos')

    # ===================================================================
    # ===== 3. COMUNICATIVO (máx 15 puntos) =============================
    # ===================================================================
    st.header('3. Comunicativo (máx 15 puntos)')

    with st.expander('Métricas Comunicativas', expanded=True):
        st.markdown('**Claridad y coherencia de la exposición**')
        com_claridad = st.radio(
            'Claridad',
            options=['No clara', 'Falta claridad', 'Clara pero incompleta', 'Clara y coherente'],
            horizontal=True,
            key='com_claridad',
            label_visibility='collapsed'
        )

        st.markdown('**Extensión solicitada**')
        com_extension = st.radio(
            'Extensión',
            options=['No cubre', 'Extensión incompleta', 'Cubre extensión'],
            horizontal=True,
            key='com_extension',
            label_visibility='collapsed'
        )

        st.markdown('**Aportaciones reflexivas y relevantes**')
        com_reflexiva = st.radio(
            'Reflexiva',
            options=['Sin reflexión', 'Poco reflexiva / ambigua', 'Reflexiva y relevante'],
            horizontal=True,
            key='com_reflexiva',
            label_visibility='collapsed'
        )

        st.markdown('**Netiqueta**')
        com_netiqueta = st.radio(
            'Netiqueta',
            options=['Faltas graves', 'Incumple netiqueta', 'Respeta netiqueta'],
            horizontal=True,
            key='com_netiqueta',
            label_visibility='collapsed'
        )

        st.markdown('**Errores de redacción (sintaxis, ortografía, puntuación)**')
        com_errores = st.radio(
            'Errores',
            options=['0 errores', '1–3 errores', '4–5 errores', '6–8 errores', '>8 errores'],
            horizontal=True,
            key='com_errores',
            label_visibility='collapsed'
        )

        # Scoring approach for Comunicativo
        _clar_s = {'No clara': 0, 'Falta claridad': 1, 'Clara pero incompleta': 2, 'Clara y coherente': 3}
        _ext_s = {'No cubre': 0, 'Extensión incompleta': 1, 'Cubre extensión': 2}
        _ref_s = {'Sin reflexión': 0, 'Poco reflexiva / ambigua': 1, 'Reflexiva y relevante': 2}
        _net_s = {'Faltas graves': 0, 'Incumple netiqueta': 1, 'Respeta netiqueta': 2}
        _err_s = {'0 errores': 4, '1–3 errores': 3, '4–5 errores': 2, '6–8 errores': 1, '>8 errores': 0}

        com_score = (_clar_s[com_claridad] + _ext_s[com_extension] +
                     _ref_s[com_reflexiva] + _net_s[com_netiqueta] + _err_s[com_errores])

        # Excelente (15): max score = 3+2+2+2+4 = 13
        # Bien (14): ~11-12
        # Regular (12): ~8-10
        # Suficiente (11): ~5-7
        # Insuficiente (9): <5
        if com_score >= 13:
            com_level = 'Excelente'
            com_pts = 15
        elif com_score >= 11:
            com_level = 'Bien'
            com_pts = 14
        elif com_score >= 8:
            com_level = 'Regular'
            com_pts = 12
        elif com_score >= 5:
            com_level = 'Suficiente'
            com_pts = 11
        elif com_score > 0:
            com_level = 'Insuficiente'
            com_pts = 9
        else:
            com_level = 'No evaluable'
            com_pts = 0

        st.success(f'**Nivel Comunicativo:** {com_level} → {com_pts} / 15 puntos')

    # ===================================================================
    # ===== 4. COLABORATIVO (máx 15 puntos) =============================
    # ===================================================================
    st.header('4. Colaborativo (máx 15 puntos)')

    with st.expander('Métricas Colaborativas', expanded=True):
        st.markdown('**Días de participación durante la semana**')
        colab_dias = st.radio(
            'Días',
            options=['No participó', '1 día (final de semana)', '1 día (todo el mismo día)', '2 días', '3 días', '4 días', '5 días'],
            horizontal=True,
            key='colab_dias',
            label_visibility='collapsed'
        )

        st.markdown('**Calidad de aportaciones para el diálogo**')
        colab_dialogo = st.radio(
            'Diálogo',
            options=['No genera diálogo', 'Aportaciones vagas / sin conclusiones', 'Generalmente promueve diálogo', 'Promueve diálogo y conclusiones'],
            horizontal=True,
            key='colab_dialogo',
            label_visibility='collapsed'
        )

        # Scoring
        _dias_s = {'No participó': 0, '1 día (final de semana)': 1, '1 día (todo el mismo día)': 2,
                   '2 días': 3, '3 días': 4, '4 días': 4, '5 días': 5}
        _dial_s = {'No genera diálogo': 0, 'Aportaciones vagas / sin conclusiones': 1,
                   'Generalmente promueve diálogo': 2, 'Promueve diálogo y conclusiones': 3}

        colab_score = _dias_s[colab_dias] + _dial_s[colab_dialogo]

        if colab_dias == 'No participó':
            colab_level = 'No evaluable'
            colab_pts = 0
        elif colab_score >= 8:
            colab_level = 'Excelente'
            colab_pts = 15
        elif colab_score >= 6:
            colab_level = 'Bien'
            colab_pts = 14
        elif colab_score >= 5:
            colab_level = 'Regular'
            colab_pts = 12
        elif colab_score >= 3:
            colab_level = 'Suficiente'
            colab_pts = 10
        else:
            colab_level = 'Insuficiente'
            colab_pts = 9

        st.success(f'**Nivel Colaborativo:** {colab_level} → {colab_pts} / 15 puntos')

    # ===================================================================
    # ===== 5. PENSAMIENTO CRÍTICO (máx 15 puntos) ======================
    # ===================================================================
    st.header('5. Pensamiento Crítico (máx 15 puntos)')

    with st.expander('Métricas de Pensamiento Crítico', expanded=True):
        st.markdown('**Argumentación y fundamentos**')
        pc_argum = st.radio(
            'Argumentación',
            options=['Argumentos desviados del tema', 'Argumentos no sólidos ni fundamentados',
                     'Fundamentos poco sólidos, sin coherencia', 'Fundamentos sólidos, poca coherencia',
                     'Argumenta coherentemente con fundamentos sólidos'],
            horizontal=False,
            key='pc_argum',
            label_visibility='collapsed'
        )

        st.markdown('**Retroalimentación a compañeros**')
        pc_retro = st.radio(
            'Retroalimentación',
            options=['No retroalimenta', 'Retroalimentación ambigua', 'Retroalimentación pertinente'],
            horizontal=True,
            key='pc_retro',
            label_visibility='collapsed'
        )

        st.markdown('**Análisis de aportaciones e ideas relevantes**')
        pc_analisis = st.radio(
            'Análisis',
            options=['No identifica ideas relevantes', 'Identifica algunas ideas relevantes',
                     'Analiza aportaciones e identifica ideas relevantes',
                     'Analiza y hace nuevas aportaciones con base en análisis'],
            horizontal=False,
            key='pc_analisis',
            label_visibility='collapsed'
        )

        # Scoring
        _arg_s = {
            'Argumentos desviados del tema': 0,
            'Argumentos no sólidos ni fundamentados': 1,
            'Fundamentos poco sólidos, sin coherencia': 2,
            'Fundamentos sólidos, poca coherencia': 3,
            'Argumenta coherentemente con fundamentos sólidos': 4
        }
        _ret_s = {'No retroalimenta': 0, 'Retroalimentación ambigua': 1, 'Retroalimentación pertinente': 2}
        _ana_s = {
            'No identifica ideas relevantes': 0,
            'Identifica algunas ideas relevantes': 1,
            'Analiza aportaciones e identifica ideas relevantes': 2,
            'Analiza y hace nuevas aportaciones con base en análisis': 3
        }

        pc_score = _arg_s[pc_argum] + _ret_s[pc_retro] + _ana_s[pc_analisis]

        # Max = 4+2+3 = 9
        if pc_score >= 8:
            critico_level = 'Excelente'
            critico_pts = 15
        elif pc_score >= 6:
            critico_level = 'Bien'
            critico_pts = 14
        elif pc_score >= 4:
            critico_level = 'Regular'
            critico_pts = 12
        elif pc_score >= 2:
            critico_level = 'Suficiente'
            critico_pts = 11
        elif pc_score > 0:
            critico_level = 'Insuficiente'
            critico_pts = 9
        else:
            critico_level = 'No evaluable'
            critico_pts = 0

        st.success(f'**Nivel Pensamiento Crítico:** {critico_level} → {critico_pts} / 15 puntos')

    # ===================================================================
    # ===== 6. ORIGINALIDAD (deducción) =================================
    # ===================================================================
    st.header('6. Originalidad (deducción)')

    ORIGINALIDAD_DEDUCTION = {
        'Excelente': 0,
        'Bien': 0,
        'Regular': -6.25,
        'Suficiente': -12.50,
        'Insuficiente': -25,
        'No aplica': 0
    }

    ORIGINALIDAD_DESCRIPCIONES = {
        'Excelente': 'Desarrolla ideas propias y sustenta con fuentes confiables con crédito según manual PL-SEP.',
        'Bien': 'Desarrolla ideas propias; sustenta algunas con fuentes confiables; puede omitir elementos de citas.',
        'Regular': 'Ideas propias pero fuentes poco confiables o formatos distintos al manual.',
        'Suficiente': 'Ideas propias sin sustento confiable; omite citas/referencias correctas.',
        'Insuficiente': 'Omite ideas propias; reproduce material sin crédito; evidencia plagio.',
        'No aplica': 'La actividad no requiere citas ni referencias explícitas.'
    }

    with st.expander('Nivel de originalidad', expanded=True):
        orig_level = st.radio(
            'Selecciona el nivel',
            options=list(ORIGINALIDAD_DEDUCTION.keys()),
            horizontal=True,
            key='orig_level',
            label_visibility='collapsed'
        )
        st.caption(ORIGINALIDAD_DESCRIPCIONES[orig_level])
        orig_deduction = ORIGINALIDAD_DEDUCTION[orig_level]
        st.write(f'**Deducción:** {orig_deduction} puntos')

    # ===================================================================
    # ===== CÁLCULO Y RESUMEN ==========================================
    # ===================================================================
    st.header('Resumen de calificación')

    subtotal = cog_pts + act_pts + com_pts + colab_pts + critico_pts
    total = subtotal + orig_deduction
    total = max(0, min(100, total))

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric('Cognitivo', f'{cog_pts} / 40')
        st.caption(f'🏷️ {cog_level}')
    with col2:
        st.metric('Actitudinal', f'{act_pts} / 15')
        st.caption(f'🏷️ {act_level}')
    with col3:
        st.metric('Comunicativo', f'{com_pts} / 15')
        st.caption(f'🏷️ {com_level}')
    with col4:
        st.metric('Colaborativo', f'{colab_pts} / 15')
        st.caption(f'🏷️ {colab_level}')
    with col5:
        st.metric('P. Crítico', f'{critico_pts} / 15')
        st.caption(f'🏷️ {critico_level}')
    with col6:
        st.metric('Originalidad', orig_deduction)
        st.caption(f'🏷️ {orig_level}')

    st.write(f'**Subtotal:** {subtotal} | **Deducción:** {orig_deduction} | **TOTAL:** {total} / 100')

    # ===================================================================
    # ===== GENERAR RETROALIMENTACIÓN EN PROSA ==========================
    # ===================================================================
    if st.button('Generar retroalimentación'):
        nombre_pila = alumno.split()[0] if alumno else 'Estudiante'

        fb = []

        # --- Saludo ---
        fb.append(f'Hola {nombre_pila}:\n\n')
        fb.append('Esta actividad tenía como propósito que reflexionaras acerca de las estrategias de aprendizaje; ')
        fb.append('las características, similitudes y diferencias del relato, el resumen y la reseña, ')
        fb.append('con la finalidad de identificar su uso efectivo para comunicarte de forma oral y escrita. ')
        fb.append('De antemano quiero reconocer tu esfuerzo por tu participación en el foro ')
        fb.append('y atender a las normas para la comunicación en entornos virtuales de aprendizaje (netiqueta).\n\n')

        # ---------------------------------------------------------------
        # COGNITIVO — warm prose assembled from selected metrics
        # ---------------------------------------------------------------
        if cog_aportaciones == 0:
            fb.append('Noté que en esta ocasión no registraste aportaciones en el foro. ')
            fb.append('Tampoco respondiste a la primera pregunta: ¿Para qué me sirve saber las diferencias entre relato, resumen y reseña?, ')
            fb.append('ni a la segunda pregunta detonadora sobre cómo aplicar estos conocimientos en tu vida cotidiana. ')
            fb.append('Además, no compartiste tu opinión sobre las participaciones de tus compañeros ')
            fb.append('ni elaboraste una conclusión sobre la temática trabajada. ')
            fb.append('Me gustaría animarte a que en la próxima participación intentes responder las preguntas detonadoras ')
            fb.append('y aportar tu perspectiva personal. Tus ideas enriquecen mucho el intercambio ')
            fb.append('y ayudan a construir un aprendizaje más significativo para todos.\n\n')
        else:
            # Aportaciones
            if cog_aportaciones == 1:
                fb.append(f'En tu participación realizaste {cog_aportaciones} aportación. ')
            else:
                fb.append(f'En tu participación realizaste {cog_aportaciones} aportaciones. ')

            # PD1
            _pd1_txt = {
                'No responde': 'Sin embargo, no respondiste a la primera pregunta detonadora: ¿Para qué me sirve saber las diferencias entre relato, resumen y reseña? Te invito a que en futuras actividades no dejes de responder las preguntas planteadas, ya que son fundamentales para la reflexión',
                'Vagamente': 'En cuanto a la primera pregunta detonadora, respondiste de manera vaga; sería muy valioso que desarrollaras un poco más tus ideas para que tu reflexión sea más completa',
                'Superficialmente': 'En tu primera aportación has respondido a la pregunta: ¿Para qué me sirve saber las diferencias entre relato, resumen y reseña?, usando argumentos superficiales para sustentar tu respuesta; hace falta desarrollar un poco más tus ideas en los foros',
                'De manera general': 'Respondiste de manera general a la primera pregunta detonadora, cubriendo los puntos principales. Te animo a que profundices un poco más en tus argumentos para enriquecer aún más tu participación',
                'Con fundamentos claros': 'En tu primera aportación respondiste con fundamentos claros y concisos a la pregunta: ¿Para qué me sirve saber las diferencias entre relato, resumen y reseña?, usando argumentos sólidos para sustentar tu respuesta'
            }
            fb.append(f'{_pd1_txt[cog_responde_pd1]}. ')

            # PD2
            _pd2_txt = {
                'No responde': 'Por otra parte, no respondiste la segunda pregunta detonadora sobre cómo aplicar estos conocimientos en tu contexto de vida; recuerda que esta reflexión es muy importante para conectar lo aprendido con tu realidad',
                'Vagamente': 'En tu segunda aportación, has respondido vagamente a la pregunta ¿Cómo las puedo aplicar en mi contexto de vida?; te invito a que reflexiones con más detalle sobre cómo estos conocimientos se conectan con tu día a día',
                'Superficialmente': 'En tu segunda aportación, has respondido superficialmente a la pregunta ¿Cómo las puedo aplicar en mi contexto de vida?; hace falta desarrollar un poco más tus respuestas en los foros',
                'De manera general': 'En cuanto a la segunda pregunta sobre cómo aplicar estos conocimientos en tu contexto de vida, respondiste de manera general, abordando los aspectos centrales',
                'Con fundamentos claros': 'Asimismo, respondiste con claridad y fundamentos sólidos a la segunda pregunta sobre cómo aplicar estos conocimientos en tu contexto de vida'
            }
            fb.append(f'{_pd2_txt[cog_responde_pd2]}. ')

            # Opinions
            if cog_opiniones == 0:
                fb.append('Además, no compartiste tu opinión sobre las participaciones de tus compañeros; ')
                fb.append('recuerda que el intercambio de ideas fortalece el aprendizaje colectivo. ')
            elif cog_opiniones == 1:
                if cog_opinion_fund == 'Opinión fundamentada y objetiva':
                    fb.append('Diste tu opinión fundamentada y objetiva sobre la participación de un compañero, lo cual enriquece el diálogo. ')
                elif cog_opinion_fund == 'Opinión general':
                    fb.append('Diste tu opinión sobre la participación de un compañero de manera general; te animo a profundizar un poco más en tus argumentos para que la retroalimentación sea más valiosa. ')
                else:
                    fb.append('Diste tu opinión sobre la participación de un compañero, aunque careció de fundamento; te invito a respaldar tus comentarios con argumentos más sólidos. ')
            else:
                if cog_opinion_fund == 'Opinión fundamentada y objetiva':
                    fb.append(f'Proporcionaste opiniones fundamentadas y objetivas sobre la participación de {cog_opiniones} compañeros, lo cual es muy valioso para la comunidad de aprendizaje. ')
                elif cog_opinion_fund == 'Opinión general':
                    fb.append(f'Proporcionaste opiniones generales sobre la participación de {cog_opiniones} compañeros; te animo a profundizar en tus argumentos para hacer más enriquecedora la retroalimentación. ')
                else:
                    fb.append(f'Comentaste sobre la participación de {cog_opiniones} compañeros, aunque tus opiniones carecieron de fundamento; recuerda que una opinión bien sustentada aporta mucho más al aprendizaje. ')

            # Conclusion
            _conc_txt = {
                'No incluye': 'Por último, no incluiste una conclusión sobre la temática del foro; te animo a que en próximas actividades elabores una reflexión final que cierre tus ideas.',
                'Comentario sin conclusión clara': 'Incluiste un comentario final, aunque no llegó a ser una conclusión clara sobre la temática; te invito a que trabajes en cerrar tus ideas de forma más contundente.',
                'Conclusión vaga': 'Incluiste una conclusión sobre la temática, aunque fue un tanto breve; te animo a desarrollar más tus reflexiones finales para darles mayor profundidad.',
                'Conclusión general': 'Elaboraste una conclusión general sobre la importancia de las estrategias de comunicación, lo cual refleja tu comprensión del tema.',
                'Conclusión clara y completa': 'Elaboraste una conclusión bastante completa sobre la importancia de escribir y hablar correctamente y de qué forma diferentes estrategias te pueden ayudar para hacerlo mejor. ¡Muy buen trabajo!'
            }
            fb.append(f'{_conc_txt[cog_conclusion]}\n\n')

        # ---------------------------------------------------------------
        # ACTITUDINAL — warm prose with detail
        # ---------------------------------------------------------------
        no_cumplidas = [instr for instr, val in instructions_check.items() if not val]

        _act_mapping = {
            'Usa creatividad y originalidad': 'procurar usar mayor creatividad y originalidad en tus aportaciones',
            'Intervenciones generan diversidad': 'asegurarte de que tus intervenciones generen diversidad de opiniones y debate',
            'Evita subir documentos (usa enlaces)': 'evitar subir documentos directamente al foro (es mejor utilizar enlaces para compartir información)',
            'Respeta netiqueta': 'seguir puntualmente las normas de netiqueta en todas tus participaciones',
            'Opiniones breves (1-3 párrafos)': 'procurar que tus opiniones sean breves y concisas, idealmente de uno a tres párrafos',
            'Redacción previa (sin errores plataforma)': 'revisar la redacción para evitar errores de ortografía, gramaticales o de redacción, para que tus aportaciones puedan entenderse con mayor claridad'
        }

        if act_level == 'Excelente':
            fb.append('En el aspecto actitudinal, lograste atender todas las instrucciones de la actividad. ')
            fb.append('Quiero destacar que te has manejado con cortesía y mostraste apertura a las aportaciones de tus compañeros, ')
            fb.append('lo cual es fundamental para el aprendizaje colaborativo.\n\n')
        else:
            if act_level == 'Bien':
                fb.append('Respecto a las instrucciones, atendiste la mayoría de ellas. ')
            elif act_level == 'Regular':
                fb.append('En cuanto a las instrucciones para la participación, atendiste gran parte de las indicaciones. ')
            elif act_level == 'Suficiente':
                fb.append('Respecto a las instrucciones del foro, lograste atender algunas de las indicaciones señaladas. ')
            else:
                fb.append('En esta ocasión, noté que atendiste pocas instrucciones para la participación en el foro. ')

            if no_cumplidas:
                fb.append('Para mejorar tu desempeño, te sugiero que en las próximas actividades intentes ')
                # Join with grammar logic
                phrases = [_act_mapping[nc] for nc in no_cumplidas]
                if len(phrases) == 1:
                    fb.append(f'{phrases[0]}. ')
                else:
                    fb.append(f'{", ".join(phrases[:-1])} y {phrases[-1]}. ')

            # Reinforce participation frequency in Actitudinal
            if colab_dias == '5 días':
                fb.append('Es excelente que hayas mantenido una participación constante durante los cinco días de la semana, esto ayuda a que el diálogo sea continuo y fluido. ')
            else:
                fb.append('Recuerda que para un mejor aprovechamiento del foro, es sumamente importante que tus participaciones se realicen en diferentes días de la semana (lo ideal son al menos 5 días), ya que esto permite que interactúes con más compañeros y sigas el hilo de la discusión. ')
            
            fb.append('Te recomiendo revisar la rúbrica con detalle en futuras entregas, ya que te dará una idea más clara de lo que se evaluará. ')
            if act_level in ['Suficiente', 'Insuficiente', 'No evaluable']:
                fb.append('Si tuvieras dudas durante el proceso, te invito a escribirme por el mensajero para resolverlas y ayudarte a lograr una mejor evaluación.\n\n')
            else:
                fb.append('\n\n')

        # ---------------------------------------------------------------
        # COMUNICATIVO — warm prose assembled from metrics
        # ---------------------------------------------------------------
        fb.append('Respecto al criterio comunicativo, ')

        _com_clar_txt = {
            'Clara y coherente': 'has presentado la información de manera clara, coherente y precisa',
            'Clara pero incompleta': 'tu exposición fue clara aunque se presentó de manera general o parcial',
            'Falta claridad': 'hace falta trabajar un poco en la manera en cómo organizas la información para que puedas presentarla de manera más clara y coherente. Te recomiendo estructurar tus ideas previamente para que tu mensaje se transmita mejor',
            'No clara': 'noté que tus aportaciones pueden mejorar en claridad y estructura para expresar mayor coherencia. Te recomiendo hacer previamente una estructura de lo que te gustaría abordar, de modo que presentes las ideas de forma más organizada'
        }
        fb.append(f'{_com_clar_txt[com_claridad]}. ')

        if com_extension == 'Cubre extensión':
            fb.append('Cubriste adecuadamente la extensión solicitada. ')
        elif com_extension == 'Extensión incompleta':
            fb.append('Procura cuidar un poco más la extensión solicitada en tus aportaciones, ya que es un aspecto que ayuda a profundizar en tus ideas. ')
        else:
            fb.append('Te sugiero dedicar un espacio mayor al desarrollo de tus respuestas para poder alcanzar la extensión esperada en futuras participaciones. ')

        if com_reflexiva == 'Reflexiva y relevante':
            fb.append('Tus aportaciones fueron reflexivas y relevantes, lo cual se valora mucho. ')
        elif com_reflexiva == 'Poco reflexiva / ambigua':
            fb.append('Tus aportaciones muestran tus ideas iniciales; te invito a profundizar más en tus análisis para enriquecer la discusión grupal. ')
        else:
            fb.append('Sería muy enriquecedor para tu aprendizaje que procures profundizar más en la reflexión y análisis de tus próximas aportaciones. ')

        if com_netiqueta == 'Respeta netiqueta':
            fb.append('Te has manejado con cortesía y mostraste apertura, respetando las normas de netiqueta. ')
        elif com_netiqueta == 'Incumple netiqueta':
            fb.append('Te invito a integrar más las normas de netiqueta en tus participaciones, pues son parte esencial de nuestra convivencia virtual. ')
        else:
            fb.append('Recuerda que el respeto y la cortesía son pilares fundamentales en nuestro espacio de aprendizaje; es vital cuidar siempre nuestras formas de comunicación pública. ')

        _err_txt = {
            '0 errores': 'No presentas errores en sintaxis, ortografía o puntuación, y presentas las ideas de manera lógica y congruente. ¡Excelente trabajo en este aspecto!',
            '1–3 errores': 'Presentaste entre 1 y 3 errores de redacción menores; con una revisión rápida antes de publicar podrás eliminarlos fácilmente.',
            '4–5 errores': 'Presentaste entre 4 y 5 errores de redacción. Te recomiendo revisar previamente lo que escribes; una lectura antes de publicar puede hacer una gran diferencia.',
            '6–8 errores': 'Presentaste entre 6 y 8 errores de redacción. Es importante que cuides la ortografía y la sintaxis; te sugiero redactar previamente en un procesador de texto y revisar antes de publicar.',
            '>8 errores': 'Presentaste más de 8 errores de redacción. Te recomiendo hacer una revisión previa cuidadosa antes de publicar; redactar primero en un procesador de texto con corrector ortográfico puede ayudarte mucho.'
        }
        fb.append(f'{_err_txt[com_errores]}\n\n')

        # ---------------------------------------------------------------
        # COLABORATIVO — warm prose from metrics
        # ---------------------------------------------------------------
        fb.append('Con relación al criterio colaborativo, ')

        _dias_txt = {
            'No participó': 'noté que no registraste participación en el foro durante la semana. Es importante que participes de manera constante para que puedas intercambiar ideas con tus compañeros y enriquecer el aprendizaje colectivo',
            '1 día (final de semana)': 'participaste una sola vez al final de la semana. Te invito a ingresar con mayor frecuencia para que puedas dialogar con tus compañeros a lo largo de la semana',
            '1 día (todo el mismo día)': 'ingresaste al foro pero realizaste todas tus aportaciones en un solo día. Te invito a distribuir tus participaciones durante la semana para que puedas generar un intercambio más rico con tus compañeros',
            '2 días': 'ingresaste y participaste en el foro ocasionalmente durante la semana (2 días), lo cual permitió cierto intercambio de ideas',
            '3 días': 'participaste activamente durante 3 días de la semana, lo cual favoreció el diálogo con tus compañeros',
            '4 días': 'participaste activamente durante 4 días de la semana, lo cual favoreció el diálogo con tus compañeros',
            '5 días': 'ingresaste y participaste continuamente durante la semana (5 días), mostrando gran compromiso con la actividad'
        }
        fb.append(f'{_dias_txt[colab_dias]}. ')

        _dial_txt = {
            'No genera diálogo': 'Te animo a que en futuras actividades tus aportaciones busquen detonar una mayor interacción y diálogo constructivo con las ideas de tus compañeros.',
            'Aportaciones vagas / sin conclusiones': 'Para futuras ocasiones, te invito a ser más descriptivo en tus comentarios para favorecer un diálogo más profundo y una mejor generación de conclusiones.',
            'Generalmente promueve diálogo': 'Proporcionaste tu opinión sobre las aportaciones de tus compañeros y promoviste el diálogo y la generación de conclusiones sobre el tema mediante tus aportaciones.',
            'Promueve diálogo y conclusiones': 'Tus aportaciones promovieron activamente el diálogo y la generación de conclusiones sobre el tema, contribuyendo de manera significativa al aprendizaje de todos.'
        }
        fb.append(f'{_dial_txt[colab_dialogo]}\n\n')

        # ---------------------------------------------------------------
        # PENSAMIENTO CRÍTICO — warm prose from metrics
        # ---------------------------------------------------------------
        fb.append('Referente al criterio de pensamiento crítico, ')

        _arg_txt = {
            'Argumentos desviados del tema': 'Sería de gran ayuda para tu evaluación que procures centrar tus reflexiones directamente en los planteamientos centrales del foro',
            'Argumentos no sólidos ni fundamentados': 'Es importante que intentes fortalecer el sustento de tus opiniones; esto permitirá que tus aportaciones tengan mayor peso y contribuyan mejor al debate',
            'Fundamentos poco sólidos, sin coherencia': 'Para mejorar este aspecto, te sugiero buscar que tus argumentos cuenten con un sustento más constante y guarden una relación clara entre sí',
            'Fundamentos sólidos, poca coherencia': 'argumentaste con fundamentos sólidos, aunque con poca coherencia entre tus ideas. Te animo a organizar mejor tus argumentos para que la lectura sea más fluida',
            'Argumenta coherentemente con fundamentos sólidos': 'argumentaste coherentemente con fundamentos sólidos, mostrando un análisis profundo del tema. ¡Se nota tu dedicación!'
        }
        fb.append(f'{_arg_txt[pc_argum]}. ')

        _retro_txt = {
            'No retroalimenta': 'Asimismo, no olvides compartir tu perspectiva sobre las ideas de tus compañeros, ya que esta interacción es esencial para el aprendizaje mutuo.',
            'Retroalimentación ambigua': 'En tu retroalimentación a compañeros, te invito a brindar comentarios más puntuales y constructivos que faciliten el intercambio de ideas.',
            'Retroalimentación pertinente': 'Además, proporcionaste retroalimentación pertinente y constructiva a tus compañeros, lo cual es muy valioso para la dinámica del foro.'
        }
        fb.append(f'{_retro_txt[pc_retro]} ')

        _anal_txt = {
            'No identifica ideas relevantes': 'De igual modo, te motivo a identificar y retomar las ideas más significativas del foro para generar aportaciones que sigan enriqueciendo la discusión.',
            'Identifica algunas ideas relevantes': 'Identificaste algunas ideas relevantes; te animo a profundizar en ellas para que tus nuevas aportaciones logren fortalecer aún más el debate grupal.',
            'Analiza aportaciones e identifica ideas relevantes': 'Analizaste las aportaciones de la semana e identificaste ideas relevantes para enriquecer la discusión, lo cual muestra compromiso con el aprendizaje colectivo.',
            'Analiza y hace nuevas aportaciones con base en análisis': 'Analizaste las aportaciones de tus compañeros e hiciste nuevas aportaciones con base en ese análisis, enriqueciendo significativamente la discusión. ¡Excelente trabajo!'
        }
        fb.append(f'{_anal_txt[pc_analisis]}\n\n')

        # ---------------------------------------------------------------
        # ORIGINALIDAD — warm tone
        # ---------------------------------------------------------------
        if orig_deduction != 0:
            fb.append('En cuanto a la originalidad, ')
            if orig_level == 'Regular':
                fb.append('noté que aunque desarrollaste ideas propias, las fuentes utilizadas fueron poco confiables o utilizaste formatos distintos al manual PL-SEP. ')
                fb.append('Te invito a consultar fuentes más sólidas y a utilizar el formato de citación indicado.\n\n')
            elif orig_level == 'Suficiente':
                fb.append('tus ideas fueron propias pero carecieron de sustento confiable y omitiste la integración correcta de citas y referencias. ')
                fb.append('Te recomiendo revisar el manual PL-SEP para mejorar en este aspecto.\n\n')
            else:
                fb.append('es fundamental que desarrolles ideas propias y des crédito a las fuentes que consultes. ')
                fb.append('Recuerda que el plagio es una falta grave; te invito a revisar el manual PL-SEP para aprender a citar correctamente.\n\n')
        else:
            if orig_level not in ['No aplica', 'Excelente', 'Bien']:
                pass
            elif orig_level in ['Excelente', 'Bien']:
                fb.append('Has presentado opiniones originales que denotan un análisis y reflexión de diferentes materiales. ¡Sigue así!\n\n')

        # ---------------------------------------------------------------
        # RECURSOS SUGERIDOS (en prosa, basados en áreas más débiles)
        # ---------------------------------------------------------------
        _scores = {
            'Cognitivo': cog_pts / 40,
            'Comunicativo': com_pts / 15,
            'Colaborativo': colab_pts / 15
        }
        recommended = suggest_resources(_scores)
        if len(recommended) == 1:
            r = recommended[0]
            fb.append(f'Finalmente, me gustaría compartirte un recurso que te puede ser útil para seguir mejorando: ')
            fb.append(f'{r["etiqueta"]} ({r["descripcion"].rstrip(".")}), ')
            fb.append(f'que puedes consultar en {r["link"]}\n\n')
        elif len(recommended) >= 2:
            r1, r2 = recommended[0], recommended[1]
            fb.append(f'Finalmente, me gustaría compartirte un par de recursos que te pueden ser útiles para seguir mejorando: ')
            fb.append(f'{r1["etiqueta"]} ({r1["descripcion"].rstrip(".")}), ')
            fb.append(f'disponible en {r1["link"]}; ')
            fb.append(f'y {r2["etiqueta"]} ({r2["descripcion"].rstrip(".")}), ')
            fb.append(f'que puedes consultar en {r2["link"]}\n\n')

        # ---------------------------------------------------------------
        # CIERRE
        # ---------------------------------------------------------------
        fb.append('Me despido, agradeciendo el tiempo y esfuerzo que dedicaste a lo largo de estas cuatro semanas, ')
        fb.append('así como tu invaluable colaboración con todos los que formamos parte de esta comunidad.\n')
        fb.append('Mucho éxito en tu camino por Prepa en Línea.\n')
        fb.append('Saludos,\n\n')

        # Firma
        if firma:
            fb.append(f'{firma}\n\n')

        fb.append(f'**PUNTAJE FINAL:** {total} / 100\n')

        st.session_state['feedback'] = ''.join(fb)
        # Force update of the editor if it already exists
        if 'feedback_editor' in st.session_state:
            st.session_state['feedback_editor'] = st.session_state['feedback']

    # ===== EDITOR DE RETROALIMENTACIÓN =====
    if 'feedback' in st.session_state:
        # Initialize feedback_editor if it doesn't exist
        if 'feedback_editor' not in st.session_state:
            st.session_state['feedback_editor'] = st.session_state['feedback']
            
        st.header('Retroalimentación (editable)')
        feedback_text = st.text_area('Editar retroalimentación', height=500, key='feedback_editor')

        col_save, col_export, col_reset = st.columns(3)

        with col_save:
            if st.button('Guardar evaluación'):
                row = {
                    'alumno': alumno,
                    'fecha': fecha.strftime("%Y-%m-%d"),
                    'firma': firma,
                    'cognitivo': cog_pts,
                    'cog_level': cog_level,
                    'actitudinal': act_pts,
                    'act_level': act_level,
                    'comunicativo': com_pts,
                    'com_level': com_level,
                    'colaborativo': colab_pts,
                    'colab_level': colab_level,
                    'pensamiento_critico': critico_pts,
                    'critico_level': critico_level,
                    'originalidad_deduccion': orig_deduction,
                    'orig_level': orig_level,
                    'total': total,
                    'feedback': feedback_text.replace('\n', ' | ')
                }
                save_evaluation(row)
                st.success('✓ Evaluación guardada en `data.csv`')

        with col_export:
            st.download_button(
                label='Descargar .md',
                data=feedback_text,
                file_name=f'{alumno.replace(" ", "_")}_retroalimentacion.md',
                mime='text/markdown'
            )

        with col_reset:
            if st.button('Reiniciar evaluación'):
                for k in list(st.session_state.keys()):
                    if k not in ['started']:
                        del st.session_state[k]
                st.rerun()


