"""Skills por rol: cada agente declara sus capacidades y su system prompt.

El set de skills se inyecta en el system prompt del modelo de Mistral para que
cada especialista responda dentro de su rol, además de su formato obligatorio.
"""

from __future__ import annotations

from .agents import AGENTS

SKILLS: dict[str, list[str]] = {
    "dev_expert": [
        "arquitectura de software y patrones de diseño",
        "backend y APIs REST/GraphQL",
        "depuración de bugs y análisis de causa raíz",
        "seguridad (OWASP, validación de entradas, gestión de secretos)",
        "optimización de rendimiento y cuellos de botella",
        "tests y calidad de código",
    ],
    "copywriter": [
        "copywriting persuasivo y psicología del consumidor",
        "voz de marca y tono adaptable",
        "emails, artículos, landing pages y guiones",
        "titulares (headlines) y pruebas A/B",
        "llamadas a la acción (CTA) efectivas",
    ],
    "data_analyst": [
        "modelado cuantitativo y métricas de negocio (KPIs)",
        "finanzas, presupuestos y rentabilidad",
        "proyecciones y forecast",
        "detección de patrones y anomalías",
        "hojas de cálculo y dashboards",
    ],
    "designer_ux": [
        "usabilidad y leyes de UX (Gestalt, Ley de Fitts, Hick)",
        "accesibilidad WCAG 2.1",
        "wireframes y sistemas de diseño",
        "jerarquía visual, paletas y tipografía",
        "psicología de la interfaz",
    ],
}

OUTPUT_FORMATS: dict[str, str] = {
    "dev_expert": (
        "Responde en 3 partes: 1) breve explicación de la arquitectura o lógica de solución, "
        "2) bloques de código completos, comentados y listos para producción, "
        "3) advertencias sobre fallos de seguridad o cuellos de botella."
    ),
    "copywriter": (
        "Responde con: 1) tono de voz definido, 2) texto estructurado con títulos, subtítulos, "
        "viñetas y CTA, 3) al menos 3 alternativas de titulares para pruebas A/B."
    ),
    "data_analyst": (
        "Responde con: 1) datos organizados en tablas Markdown, 2) explicación paso a paso de "
        "las fórmulas o lógica aplicada, 3) sección final 'Riesgos u Oportunidades Identificadas'."
    ),
    "designer_ux": (
        "Responde con: 1) justificación del diseño según leyes de UX, 2) paleta en hexadecimales, "
        "tipografías y jerarquía visual, 3) descripción del wireframe paso a paso."
    ),
}


def skills_for(agent_key: str) -> list[str]:
    return SKILLS.get(agent_key, [])


def system_prompt_for(agent_key: str) -> str:
    """System prompt del agente: identidad + skills del rol + formato obligatorio."""
    spec = AGENTS[agent_key]
    skills = "\n".join(f"- {s}" for s in SKILLS.get(agent_key, []))
    return (
        f"Eres {spec.name}, {spec.role} de la Oficina Virtual IA.\n"
        f"Tus skills son:\n{skills}\n\n"
        f"{OUTPUT_FORMATS[agent_key]}\n"
        "Responde siempre en español, de forma clara y accionable."
    )
