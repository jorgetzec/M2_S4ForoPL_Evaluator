# Retroalimentación - {{ alumno }}

**Actividad:** Foro de integración

**Fecha:** {{ fecha }}

---

{% for bloque in bloques %}
**{{ bloque.nombre }}:** {{ bloque.puntos }}/{{ bloque.max }}

{{ bloque.frase }}

Sugerencia: {{ bloque.sugerencia }}

---
{% endfor %}

**Originalidad / Deducción aplicada:** {{ originalidad_label }} ({{ originalidad_deduction }})

**Puntaje final:** {{ total }} / 100


**Recursos recomendados:**
{% for r in recursos %}
- {{ r.etiqueta }}: {{ r.link }} — {{ r.descripcion }}
{% endfor %}


---

{{ cierre }}

Firma: {{ firma }}
