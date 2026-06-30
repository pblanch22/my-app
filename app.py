import os
import tempfile
import json
import urllib.request
import urllib.error
from io import BytesIO
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SCOUT PRO",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚽"
)

# =========================================================
# IDIOMAS
# =========================================================

LANG = {
    "es": {
        "app_title": "SCOUT PRO",
        "app_sub": "SISTEMA DE ANÁLISIS Y SEGUIMIENTO DE TALENTO",
        "active": "SISTEMA ACTIVO",
        "players": "Jugadores",
        "team_avg": "Prom. Equipo",
        "formation": "Formación",
        "top_player": "Top Jugador",
        "tab_input": "✏️  INGRESAR",
        "tab_field": "⚽  CANCHA",
        "tab_stats": "📊  ESTADÍSTICAS",
        "tab_compare": "⚖️  COMPARAR",
        "tab_tactics": "🗂️  TÁCTICO",
        "skills_title": "HABILIDADES DEL JUGADOR",
        "skills_hint": "Ingresá los valores del 0 al 100 por categoría.",
        "avg_label": "PROMEDIO GENERAL",
        "level_label": "NIVEL",
        "lateral_hint": "← Completá los datos en el panel lateral y presioná REGISTRAR.",
        "tactics_title": "CONFIGURACIÓN TÁCTICA",
        "player_data": "DATOS DEL JUGADOR",
        "full_name": "Nombre completo",
        "name_placeholder": "Ej: Lionel García",
        "foot": "Pie",
        "right": "Derecho",
        "left": "Izquierdo",
        "both": "Ambidiestro",
        "height": "Altura (cm)",
        "weight": "Peso (kg)",
        "skills_section": "HABILIDADES — ver pestaña",
        "skills_note": "Los valores se ingresan en la pestaña",
        "tab_ref": "✏️ INGRESAR",
        "pos_detected": "POSICIÓN DETECTADA",
        "register_btn": "➕  REGISTRAR JUGADOR",
        "field_empty": "AGREGÁ JUGADORES DESDE EL PANEL LATERAL",
        "no_players": "Aún no hay jugadores registrados.",
        "radar": "RADAR",
        "download_pdf": "📄 Descargar Kárdex PDF",
        "delete": "🗑️ Eliminar",
        "compare_need": "NECESITÁS AL MENOS 2 JUGADORES PARA COMPARAR",
        "player1": "Jugador 1",
        "player2": "Jugador 2",
        "stats_title": "ESTADÍSTICAS COMPARADAS",
        "skill_col": "HABILIDAD",
        "ai_analysis": "🤖 ANÁLISIS IA",
        "ai_btn": "⚡ Generar Análisis con IA",
        "ai_loading": "Analizando con inteligencia artificial...",
        "ai_error": "No se pudo conectar con la IA. Verificá tu conexión.",
        "pdf_error": "Error al generar PDF",
        "nivel_elite": "ÉLITE",
        "nivel_comp": "COMPETITIVO",
        "nivel_dev": "DESARROLLO",
        "obs_elite": "Jugador de perfil elite. Capacidades tecnicas y tacticas por encima de la media. Alta proyeccion competitiva a nivel profesional. Se recomienda seguimiento inmediato.",
        "obs_comp": "Jugador competitivo con buenas condiciones fisicas y tecnicas. Posee atributos solidos y potencial de crecimiento en entorno de alto rendimiento.",
        "obs_dev": "Jugador en etapa de desarrollo. Presenta margen importante de mejora. Con trabajo dirigido puede alcanzar un nivel competitivo superior en los proximos ciclos.",
        "ai_prompt": lambda p, habs, scores: f"""Sos un scout de fútbol profesional de élite. Analizá este jugador y devolvé un JSON con el siguiente formato exacto, sin texto adicional, sin markdown:
{{
  "posicion_recomendada": "string (posición más precisa)",
  "posicion_alternativa": "string (segunda posición viable)",
  "perfil": "string (2-3 oraciones describiendo el perfil del jugador)",
  "fortalezas": ["string", "string", "string"],
  "debilidades": ["string", "string"],
  "recomendaciones": ["string", "string", "string"],
  "potencial": "ALTO|MEDIO|BAJO",
  "comparacion": "string (jugador profesional similar, breve)"
}}

DATOS DEL JUGADOR:
- Nombre: {p['name']}
- Pie dominante: {p['foot']}
- Altura: {p['h']} cm
- Peso: {p['w']} kg
- Promedio general: {p['avg']}

HABILIDADES (0-100):
{chr(10).join(f'- {h}: {s}' for h, s in zip(habs, scores))}

Analiza en detalle las habilidades y da una posición muy precisa (puede ser: Portero, Defensor Central, Lateral Derecho, Lateral Izquierdo, Carrilero Derecho, Carrilero Izquierdo, Mediocentro Defensivo, Mediocentro, Mediocentro Box-to-Box, Mediapunta, Extremo Derecho, Extremo Izquierdo, Delantero Centro, Segundo Delantero). Sé específico y útil.""",
    },
    "en": {
        "app_title": "SCOUT PRO",
        "app_sub": "TALENT ANALYSIS & TRACKING SYSTEM",
        "active": "SYSTEM ACTIVE",
        "players": "Players",
        "team_avg": "Team Avg",
        "formation": "Formation",
        "top_player": "Top Player",
        "tab_input": "✏️  INPUT",
        "tab_field": "⚽  FIELD",
        "tab_stats": "📊  STATISTICS",
        "tab_compare": "⚖️  COMPARE",
        "tab_tactics": "🗂️  TACTICS",
        "skills_title": "PLAYER SKILLS",
        "skills_hint": "Enter values from 0 to 100 per category.",
        "avg_label": "OVERALL AVERAGE",
        "level_label": "LEVEL",
        "lateral_hint": "← Fill in the data in the sidebar and press REGISTER.",
        "tactics_title": "TACTICAL SETUP",
        "player_data": "PLAYER DATA",
        "full_name": "Full name",
        "name_placeholder": "E.g.: Lionel García",
        "foot": "Foot",
        "right": "Right",
        "left": "Left",
        "both": "Both",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "skills_section": "SKILLS — see tab",
        "skills_note": "Enter values in the",
        "tab_ref": "✏️ INPUT",
        "pos_detected": "DETECTED POSITION",
        "register_btn": "➕  REGISTER PLAYER",
        "field_empty": "ADD PLAYERS FROM THE SIDEBAR TO SEE THEM ON THE FIELD",
        "no_players": "No players registered yet.",
        "radar": "RADAR",
        "download_pdf": "📄 Download Report PDF",
        "delete": "🗑️ Delete",
        "compare_need": "YOU NEED AT LEAST 2 PLAYERS TO COMPARE",
        "player1": "Player 1",
        "player2": "Player 2",
        "stats_title": "COMPARED STATISTICS",
        "skill_col": "SKILL",
        "ai_analysis": "🤖 AI ANALYSIS",
        "ai_btn": "⚡ Generate AI Analysis",
        "ai_loading": "Analyzing with artificial intelligence...",
        "ai_error": "Could not connect to AI. Check your connection.",
        "pdf_error": "PDF generation error",
        "nivel_elite": "ELITE",
        "nivel_comp": "COMPETITIVE",
        "nivel_dev": "DEVELOPING",
        "obs_elite": "Elite profile player. Technical and tactical capabilities above average. High competitive projection at professional level. Immediate follow-up recommended.",
        "obs_comp": "Competitive player with good physical and technical conditions. Has solid attributes and growth potential in a high-performance environment.",
        "obs_dev": "Player in development stage. Significant room for improvement. With focused training can reach a higher competitive level in the coming cycles.",
        "ai_prompt": lambda p, habs, scores: f"""You are an elite professional football scout. Analyze this player and return a JSON with the exact format below, no extra text, no markdown:
{{
  "posicion_recomendada": "string (most precise position)",
  "posicion_alternativa": "string (second viable position)",
  "perfil": "string (2-3 sentences describing the player's profile)",
  "fortalezas": ["string", "string", "string"],
  "debilidades": ["string", "string"],
  "recomendaciones": ["string", "string", "string"],
  "potencial": "HIGH|MEDIUM|LOW",
  "comparacion": "string (similar professional player, brief)"
}}

PLAYER DATA:
- Name: {p['name']}
- Dominant foot: {p['foot']}
- Height: {p['h']} cm
- Weight: {p['w']} kg
- Overall average: {p['avg']}

SKILLS (0-100):
{chr(10).join(f'- {h}: {s}' for h, s in zip(habs, scores))}

Analyze the skills in detail and give a very precise position (can be: Goalkeeper, Central Defender, Right Back, Left Back, Right Wing-Back, Left Wing-Back, Defensive Midfielder, Central Midfielder, Box-to-Box Midfielder, Attacking Midfielder, Right Winger, Left Winger, Centre Forward, Second Striker). Be specific and useful.""",
    }
}

# =========================================================
# SESSION STATE INIT
# =========================================================

if "players" not in st.session_state:
    st.session_state.players = []
if "puntajes_tmp" not in st.session_state:
    st.session_state.puntajes_tmp = [60] * 16
# Migrar sesiones antiguas que quedaron con 12 valores
elif len(st.session_state.puntajes_tmp) < 16:
    st.session_state.puntajes_tmp += [60] * (16 - len(st.session_state.puntajes_tmp))
if "lang" not in st.session_state:
    st.session_state.lang = "es"
if "ai_results" not in st.session_state:
    st.session_state.ai_results = {}
if "anthropic_api_key" not in st.session_state:
    st.session_state.anthropic_api_key = ""

def T(key):
    return LANG[st.session_state.lang][key]

# =========================================================
# HABILIDADES
# =========================================================

HABILIDADES = {
    "es": [
        ("Control",       "técnica"),
        ("Conducción",    "técnica"),
        ("Pase Corto",    "técnica"),
        ("Pase Largo",    "técnica"),
        ("Definición",    "ataque"),
        ("Regate",        "ataque"),
        ("Cabeceo",       "ataque"),
        ("Anticipación",  "defensa"),
        ("Entrada",       "defensa"),
        ("Posicionamiento","defensa"),
        ("Visión",        "creación"),
        ("Decisión",      "creación"),
        ("Aceleración",   "físico"),
        ("Velocidad",     "físico"),
        ("Fondo Físico",  "físico"),
        ("Fuerza",        "físico"),
    ],
    "en": [
        ("Ball Control",  "technique"),
        ("Dribbling",     "technique"),
        ("Short Pass",    "technique"),
        ("Long Pass",     "technique"),
        ("Finishing",     "attack"),
        ("Skill Moves",   "attack"),
        ("Heading",       "attack"),
        ("Anticipation",  "defense"),
        ("Tackling",      "defense"),
        ("Positioning",   "defense"),
        ("Vision",        "creation"),
        ("Decision",      "creation"),
        ("Acceleration",  "physical"),
        ("Speed",         "physical"),
        ("Stamina",       "physical"),
        ("Strength",      "physical"),
    ]
}

COLORES_CAT = {
    "técnica":    "#3B82F6",
    "technique":  "#3B82F6",
    "ataque":     "#EF4444",
    "attack":     "#EF4444",
    "defensa":    "#10B981",
    "defense":    "#10B981",
    "creación":   "#8B5CF6",
    "creation":   "#8B5CF6",
    "físico":     "#F59E0B",
    "physical":   "#F59E0B",
}

def habs():
    return HABILIDADES[st.session_state.lang]

def hab_labels():
    return [h[0] for h in habs()]

# =========================================================
# ESTÁNDARES DE EVALUACIÓN POR EDAD (TESTS FÍSICOS Y TÉCNICOS)
# =========================================================
# Cada habilidad tiene un test estándar asociado. Las marcas de
# referencia están calculadas para SUB-18 (jugador formado) y se
# escalan automáticamente para categorías menores con un factor
# de desarrollo por edad. Son valores de referencia orientativos
# (estándares habituales de fútbol formativo) y se pueden ajustar
# editando AGE_MULT o el "calib" de cada test en TEST_DEFS.

AGE_MULT = {
    "sub12": 0.72, "sub13": 0.78, "sub14": 0.84, "sub15": 0.89,
    "sub16": 0.93, "sub17": 0.97, "sub18": 1.00,
}
CATEGORIAS = ["sub12", "sub13", "sub14", "sub15", "sub16", "sub17", "sub18"]

def edad_a_categoria(edad):
    edad = int(edad)
    if edad <= 12: return "sub12"
    if edad == 13: return "sub13"
    if edad == 14: return "sub14"
    if edad == 15: return "sub15"
    if edad == 16: return "sub16"
    if edad == 17: return "sub17"
    return "sub18"

# Orden alineado 1 a 1 con HABILIDADES["es"] / HABILIDADES["en"]
# tipo: "tiempo" (seg, menor=mejor) | "conteo" (aciertos, mayor=mejor) | "distancia" (m, mayor=mejor)
TEST_DEFS = [
    {"nombre_es": "Control orientado", "nombre_en": "Ball control drill",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 10, 80: 8, 60: 6, 40: 4, 20: 2, 0: 0}},
    {"nombre_es": "Slalom con balón 20m", "nombre_en": "20m dribbling slalom",
     "unidad": "seg", "tipo": "tiempo", "lower_is_better": True,
     "calib": {100: 5.5, 80: 6.0, 60: 6.5, 40: 7.2, 20: 8.0, 0: 9.0}},
    {"nombre_es": "Precisión pase corto (8m)", "nombre_en": "Short pass accuracy (8m)",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 10, 80: 8, 60: 6, 40: 4, 20: 2, 0: 0}},
    {"nombre_es": "Precisión pase largo (30m)", "nombre_en": "Long pass accuracy (30m)",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 10, 80: 7, 60: 5, 40: 3, 20: 1, 0: 0}},
    {"nombre_es": "Finalización (tiros a arco)", "nombre_en": "Finishing on goal",
     "unidad": "goles/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 9, 80: 7, 60: 5, 40: 3, 20: 1, 0: 0}},
    {"nombre_es": "Circuito de regate 1v1 (conos)", "nombre_en": "1v1 cone dribbling circuit",
     "unidad": "seg", "tipo": "tiempo", "lower_is_better": True,
     "calib": {100: 6.0, 80: 6.6, 60: 7.2, 40: 8.0, 20: 9.0, 0: 10.0}},
    {"nombre_es": "Precisión de cabeceo a arco", "nombre_en": "Heading accuracy on goal",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 8, 80: 6, 60: 4, 40: 2, 20: 1, 0: 0}},
    {"nombre_es": "Intercepciones en circuito", "nombre_en": "Interception drill",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 9, 80: 7, 60: 5, 40: 3, 20: 1, 0: 0}},
    {"nombre_es": "Duelos defensivos ganados", "nombre_en": "Defensive duels won",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 9, 80: 7, 60: 5, 40: 3, 20: 1, 0: 0}},
    {"nombre_es": "Test situacional de posicionamiento", "nombre_en": "Positioning situational test",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 9, 80: 7, 60: 5, 40: 3, 20: 1, 0: 0}},
    {"nombre_es": "Pases clave en situación de juego", "nombre_en": "Key passes in game situation",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 9, 80: 7, 60: 5, 40: 3, 20: 1, 0: 0}},
    {"nombre_es": "Decisiones correctas (superioridad/inferioridad)", "nombre_en": "Correct decisions drill",
     "unidad": "aciertos/10", "tipo": "conteo", "lower_is_better": False,
     "calib": {100: 9, 80: 7, 60: 5, 40: 3, 20: 1, 0: 0}},
    {"nombre_es": "Sprint 10m", "nombre_en": "10m sprint",
     "unidad": "seg", "tipo": "tiempo", "lower_is_better": True,
     "calib": {100: 1.65, 80: 1.78, 60: 1.90, 40: 2.05, 20: 2.20, 0: 2.40}},
    {"nombre_es": "Sprint 30m", "nombre_en": "30m sprint",
     "unidad": "seg", "tipo": "tiempo", "lower_is_better": True,
     "calib": {100: 4.00, 80: 4.30, 60: 4.60, 40: 5.00, 20: 5.50, 0: 6.00}},
    {"nombre_es": "Test Cooper (12 min)", "nombre_en": "Cooper test (12 min)",
     "unidad": "metros", "tipo": "distancia", "lower_is_better": False,
     "calib": {100: 3000, 80: 2700, 60: 2400, 40: 2100, 20: 1800, 0: 1500}},
    {"nombre_es": "Salto horizontal sin impulso", "nombre_en": "Standing long jump",
     "unidad": "metros", "tipo": "distancia", "lower_is_better": False,
     "calib": {100: 2.60, 80: 2.40, 60: 2.20, 40: 2.00, 20: 1.80, 0: 1.60}},
]

def calib_por_categoria(idx, categoria):
    """Tabla de marcas {score: valor} escalada a la categoría de edad."""
    base = TEST_DEFS[idx]
    mult = AGE_MULT.get(categoria, 1.0)
    lower = base["lower_is_better"]
    out = {}
    for score, val in base["calib"].items():
        nv = (val / mult) if lower else (val * mult)
        if base["tipo"] == "conteo":
            nv = round(nv)
        else:
            nv = round(nv, 2)
        out[score] = nv
    return out

def score_from_mark(mark, calib, lower_is_better):
    """Interpola la marca ingresada contra la tabla de calibración -> nota 0-100."""
    items = sorted(calib.items(), key=lambda kv: kv[1])
    xp = [v for _, v in items]
    fp = [s for s, _ in items]
    score = float(np.interp(mark, xp, fp))
    return round(max(0, min(100, score)), 1)

def test_def_for(idx, lang):
    t = TEST_DEFS[idx]
    nombre = t["nombre_es"] if lang == "es" else t["nombre_en"]
    return nombre, t["unidad"], t["tipo"], t["lower_is_better"]

# =========================================================
# FORMACIONES
# =========================================================

FORMACIONES = {
    "4-4-2": {
        "GK": (8,50), "LB": (25,85), "CB1": (22,62), "CB2": (22,38), "RB": (25,15),
        "LM": (50,85), "CM1": (45,62), "CM2": (45,38), "RM": (50,15),
        "ST1": (80,60), "ST2": (80,40),
    },
    "4-3-3": {
        "GK": (8,50), "LB": (25,85), "CB1": (22,62), "CB2": (22,38), "RB": (25,15),
        "CM1": (50,72), "CM2": (46,50), "CM3": (50,28),
        "LW": (80,80), "ST": (85,50), "RW": (80,20),
    },
    "3-5-2": {
        "GK": (8,50), "CB1": (22,75), "CB2": (18,50), "CB3": (22,25),
        "LM": (50,90), "CM1": (44,68), "CM2": (44,50), "CM3": (44,32), "RM": (50,10),
        "ST1": (80,62), "ST2": (80,38),
    },
    "4-2-3-1": {
        "GK": (8,50), "LB": (25,85), "CB1": (22,62), "CB2": (22,38), "RB": (25,15),
        "CDM1": (38,62), "CDM2": (38,38),
        "LW": (62,78), "CAM": (62,50), "RW": (62,22),
        "ST": (82,50),
    },
    "5-3-2": {
        "GK": (8,50), "LWB": (28,90), "CB1": (20,70), "CB2": (18,50),
        "CB3": (20,30), "RWB": (28,10),
        "CM1": (48,70), "CM2": (44,50), "CM3": (48,30),
        "ST1": (78,62), "ST2": (78,38),
    },
    "4-1-4-1": {
        "GK": (8,50), "LB": (25,85), "CB1": (22,62), "CB2": (22,38), "RB": (25,15),
        "CDM": (38,50),
        "LM": (58,85), "CM1": (55,62), "CM2": (55,38), "RM": (58,15),
        "ST": (82,50),
    },
}

ROLE_COLORS = {"DEF": "#10B981", "MID": "#3B82F6", "ATT": "#EF4444", "GK": "#F59E0B"}

# =========================================================
# MOTOR POSICIONAL IA LOCAL (mejorado, 16 skills)
# =========================================================

def motor_posicional_local(v, pie, h, w):
    """
    v = lista de 16 valores (índices):
    0:Control 1:Conducción 2:PaseCorto 3:PaseLargo 4:Definición
    5:Regate 6:Cabeceo 7:Anticipación 8:Entrada 9:Posicionamiento
    10:Visión 11:Decisión 12:Aceleración 13:Velocidad 14:FondoFísico 15:Fuerza
    """
    # Perfiles compuestos
    tecnica   = (v[0]+v[1]+v[2]+v[3]) / 4
    ataque    = (v[4]+v[5]+v[6]) / 3
    defensa   = (v[7]+v[8]+v[9]) / 3
    creacion  = (v[10]+v[11]) / 2
    velocidad = (v[12]+v[13]) / 2
    fondo     = v[14]
    fuerza    = v[15]
    pase      = (v[2]+v[3]) / 2
    vision    = v[10]
    decision  = v[11]

    # Score por posición (cuanto más alto, más adecuado)
    scores_pos = {}

    scores_pos["Portero"]               = (defensa*0.5 + fuerza*0.3 + decision*0.2)
    scores_pos["Defensor Central"]      = (defensa*0.5 + fuerza*0.25 + v[6]*0.15 + decision*0.1)
    scores_pos["Lateral Derecho"]       = (defensa*0.35 + velocidad*0.3 + tecnica*0.2 + fondo*0.15) if pie in ("Derecho","Ambidiestro") else defensa*0.3
    scores_pos["Lateral Izquierdo"]     = (defensa*0.35 + velocidad*0.3 + tecnica*0.2 + fondo*0.15) if pie in ("Izquierdo","Ambidiestro") else defensa*0.3
    scores_pos["Carrilero Derecho"]     = (velocidad*0.3 + fondo*0.25 + defensa*0.2 + ataque*0.15 + tecnica*0.1) if pie in ("Derecho","Ambidiestro") else velocidad*0.2
    scores_pos["Carrilero Izquierdo"]   = (velocidad*0.3 + fondo*0.25 + defensa*0.2 + ataque*0.15 + tecnica*0.1) if pie in ("Izquierdo","Ambidiestro") else velocidad*0.2
    scores_pos["Mediocentro Defensivo"] = (defensa*0.4 + pase*0.25 + fuerza*0.2 + decision*0.15)
    scores_pos["Mediocentro"]           = (tecnica*0.3 + creacion*0.25 + defensa*0.2 + fondo*0.15 + velocidad*0.1)
    scores_pos["Mediocentro Box-to-Box"]= (fondo*0.3 + tecnica*0.25 + ataque*0.2 + defensa*0.15 + velocidad*0.1)
    scores_pos["Mediapunta"]            = (creacion*0.35 + tecnica*0.3 + ataque*0.2 + vision*0.15)
    scores_pos["Extremo Derecho"]       = (velocidad*0.35 + regate(v)*0.25 + ataque*0.2 + tecnica*0.2) if pie in ("Derecho","Ambidiestro") else velocidad*0.25
    scores_pos["Extremo Izquierdo"]     = (velocidad*0.35 + regate(v)*0.25 + ataque*0.2 + tecnica*0.2) if pie in ("Izquierdo","Ambidiestro") else velocidad*0.25
    scores_pos["Delantero Centro"]      = (ataque*0.4 + fuerza*0.25 + v[6]*0.2 + decision*0.15)
    scores_pos["Segundo Delantero"]     = (ataque*0.35 + velocidad*0.25 + creacion*0.2 + tecnica*0.2)

    # Bonus por físico (altura para centrales y delanteros)
    if h >= 183:
        scores_pos["Defensor Central"] += 8
        scores_pos["Delantero Centro"] += 6
    if h <= 172:
        scores_pos["Mediocentro"] += 4
        scores_pos["Mediapunta"]  += 4

    # Portero solo si defensa muy alta y físico
    if defensa < 70 or fuerza < 60:
        scores_pos["Portero"] = 0

    best = max(scores_pos, key=scores_pos.get)
    sorted_pos = sorted(scores_pos.items(), key=lambda x: x[1], reverse=True)
    alt = sorted_pos[1][0] if sorted_pos[1][0] != best else sorted_pos[2][0]
    return best, alt

def regate(v):
    return (v[1] + v[5]) / 2

def detectar_rol(j):
    p = j["pos"]
    if any(x in p for x in ["Portero"]): return "GK"
    if any(x in p for x in ["Defensor","Lateral","Carrilero","Back","Defender"]): return "DEF"
    if any(x in p for x in ["Medio","Pivot","Enganche","Midfielder","Midfield","Attacking Mid","Defensive Mid"]): return "MID"
    if any(x in p for x in ["Extremo","Delantero","Winger","Forward","Striker"]): return "ATT"
    return "MID"

def get_role_color(pos):
    r = detectar_rol({"pos": pos})
    return ROLE_COLORS.get(r, ROLE_COLORS["MID"])

# =========================================================
# IA — CLAUDE API
# =========================================================

def analizar_con_ia(jugador):
    lang = st.session_state.lang
    prompt_fn = LANG[lang]["ai_prompt"]
    habs_list = hab_labels()
    prompt = prompt_fn(jugador, habs_list, jugador["scores"])

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    api_key = st.session_state.get("anthropic_api_key", "")
    if not api_key:
        raise ValueError("Ingresá tu API Key de Anthropic en el panel lateral antes de usar el análisis IA.")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    raw = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            raw += block["text"]

    # Limpiar posibles markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)

# =========================================================
# ASIGNAR FORMACIÓN
# =========================================================

def asignar_formacion(jugadores, formacion):
    estructura = FORMACIONES[formacion]
    finales = []
    defensas, medios, ataques = [], [], []

    for j in jugadores:
        rol = detectar_rol(j)
        if rol == "DEF": defensas.append(j)
        elif rol == "MID": medios.append(j)
        elif rol == "ATT": ataques.append(j)
        # GK ignora por ahora

    lat_izq = [j for j in defensas if any(x in j["pos"] for x in ["Lateral Izq","Left","Carrilero Izq"]) and j["foot"] in ("Izquierdo","Left")]
    lat_der = [j for j in defensas if any(x in j["pos"] for x in ["Lateral Der","Right","Carrilero Der"]) and j["foot"] in ("Derecho","Right")]
    centrales = [j for j in defensas if j not in lat_izq and j not in lat_der]

    def asignar(j, key):
        if key in estructura:
            n = j.copy(); n["coords"] = estructura[key]; n["rol_tactico"] = key
            finales.append(n)

    if lat_izq and "LB" in estructura: asignar(lat_izq.pop(0), "LB")
    if lat_der and "RB" in estructura: asignar(lat_der.pop(0), "RB")
    cbs = [k for k in estructura if "CB" in k]
    for i, j in enumerate(centrales):
        if i < len(cbs): asignar(j, cbs[i])

    m_izq = [j for j in medios if j["foot"] in ("Izquierdo","Left")]
    m_der = [j for j in medios if j["foot"] in ("Derecho","Right")]
    m_ctr = [j for j in medios if j["foot"] in ("Ambidiestro","Both")]
    if m_izq and "LM" in estructura: asignar(m_izq.pop(0), "LM")
    if m_der and "RM" in estructura: asignar(m_der.pop(0), "RM")
    mid_keys = [k for k in estructura if any(x in k for x in ["CM","CAM","CDM"])]
    for i, j in enumerate(m_ctr + m_izq + m_der):
        if i < len(mid_keys): asignar(j, mid_keys[i])

    ext_izq = [j for j in ataques if any(x in j["pos"] for x in ["Izquierdo","Left","Izq"])]
    ext_der = [j for j in ataques if any(x in j["pos"] for x in ["Derecho","Right","Der"])]
    dels = [j for j in ataques if j not in ext_izq and j not in ext_der]
    if ext_izq and "LW" in estructura: asignar(ext_izq.pop(0), "LW")
    if ext_der and "RW" in estructura: asignar(ext_der.pop(0), "RW")
    sts = [k for k in estructura if "ST" in k]
    for i, j in enumerate(dels):
        if i < len(sts): asignar(j, sts[i])

    return finales

# =========================================================
# CSS PREMIUM
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --gold:       #C9A84C;
    --gold-light: #F0D080;
    --gold-dim:   #7A5E28;
    --dark:       #0A0A0F;
    --dark2:      #111118;
    --dark3:      #1A1A24;
    --dark4:      #22222F;
    --border:     rgba(201,168,76,0.18);
    --text:       #E8E8F0;
    --text-muted: #7A7A92;
    --green:      #10B981;
    --amber:      #F59E0B;
    --red:        #EF4444;
    --blue:       #3B82F6;
    --purple:     #8B5CF6;
}

html, body, [class*="css"] {
    background-color: var(--dark) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stApp { background: var(--dark) !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--dark2); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 4px; }

section[data-testid="stSidebar"] {
    background: var(--dark2) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

.sidebar-logo { text-align:center; padding:1.5rem 0 1rem; border-bottom:1px solid var(--border); margin-bottom:1.5rem; }
.sidebar-logo .brand { font-family:'Bebas Neue',sans-serif; font-size:2.2rem; letter-spacing:5px; background:linear-gradient(135deg,var(--gold-light),var(--gold)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1; }
.sidebar-logo .sub { font-family:'Space Mono',monospace; font-size:0.5rem; letter-spacing:3px; color:var(--text-muted) !important; -webkit-text-fill-color:var(--text-muted) !important; margin-top:4px; }

.sidebar-section { font-family:'Space Mono',monospace; font-size:0.58rem; letter-spacing:3px; color:var(--gold) !important; -webkit-text-fill-color:var(--gold) !important; text-transform:uppercase; margin:1.2rem 0 0.5rem; padding-bottom:4px; border-bottom:1px solid var(--border); }

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--dark3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--gold), var(--gold-dim)) !important;
    color: #000 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 20px rgba(201,168,76,0.35) !important; }

.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid var(--gold) !important;
    color: var(--gold) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
}
.stDownloadButton > button:hover { background: var(--gold) !important; color: #000 !important; }

.hero-header { display:flex; align-items:center; justify-content:space-between; padding:2rem 2.5rem; background:linear-gradient(135deg,var(--dark2) 0%,var(--dark3) 100%); border:1px solid var(--border); border-radius:16px; margin-bottom:1.5rem; position:relative; overflow:hidden; }
.hero-header::before { content:''; position:absolute; top:-60px; right:-60px; width:200px; height:200px; background:radial-gradient(circle,rgba(201,168,76,0.08) 0%,transparent 70%); border-radius:50%; }
.hero-title { font-family:'Bebas Neue',sans-serif; font-size:3.2rem; letter-spacing:6px; background:linear-gradient(135deg,var(--gold-light),var(--gold)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1; }
.hero-sub { font-family:'Space Mono',monospace; font-size:0.62rem; letter-spacing:3px; color:var(--text-muted); margin-top:4px; }
.hero-badge { background:rgba(201,168,76,0.1); border:1px solid var(--border); border-radius:50px; padding:0.4rem 1rem; font-family:'Space Mono',monospace; font-size:0.62rem; color:var(--gold); letter-spacing:2px; }

.stat-row { display:flex; gap:1rem; margin-bottom:1.5rem; }
.stat-chip { flex:1; background:var(--dark2); border:1px solid var(--border); border-radius:12px; padding:1rem 1.2rem; text-align:center; }
.stat-chip .val { font-family:'Bebas Neue',sans-serif; font-size:2.2rem; color:var(--gold); line-height:1; }
.stat-chip .lbl { font-size:0.62rem; letter-spacing:2px; color:var(--text-muted); text-transform:uppercase; margin-top:2px; font-family:'Space Mono',monospace; }

.section-title { font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:3px; color:var(--text); border-left:3px solid var(--gold); padding-left:0.8rem; margin-bottom:1rem; }

.pos-detected { background:linear-gradient(135deg,rgba(201,168,76,0.15),rgba(201,168,76,0.05)); border:1px solid var(--gold); border-radius:8px; padding:0.6rem 1rem; font-family:'Space Mono',monospace; font-size:0.68rem; color:var(--gold); text-align:center; letter-spacing:2px; margin-top:0.5rem; }

.player-card { background:var(--dark2); border:1px solid var(--border); border-radius:14px; padding:1.2rem 1.5rem; margin-bottom:1rem; position:relative; overflow:hidden; }
.player-card::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background:linear-gradient(180deg,var(--gold),var(--gold-dim)); border-radius:3px 0 0 3px; }
.player-card .pc-name { font-family:'Bebas Neue',sans-serif; font-size:1.5rem; letter-spacing:2px; color:var(--text); line-height:1; }
.player-card .pc-pos { font-family:'Space Mono',monospace; font-size:0.6rem; letter-spacing:2px; color:var(--gold); text-transform:uppercase; margin-top:2px; }
.player-card .pc-avg { position:absolute; top:1rem; right:1.5rem; font-family:'Bebas Neue',sans-serif; font-size:2.5rem; color:var(--gold); line-height:1; }
.pc-meta { display:flex; gap:0.8rem; margin-top:0.8rem; flex-wrap:wrap; }
.pc-tag { background:var(--dark3); border:1px solid var(--dark4); border-radius:4px; padding:2px 8px; font-size:0.7rem; color:var(--text-muted); font-family:'Space Mono',monospace; }
.pc-bar-row { display:flex; align-items:center; gap:0.5rem; margin-top:0.4rem; }
.pc-bar-label { font-size:0.62rem; color:var(--text-muted); width:80px; font-family:'Space Mono',monospace; flex-shrink:0; }
.pc-bar-track { flex:1; height:4px; background:var(--dark4); border-radius:2px; overflow:hidden; }
.pc-bar-fill { height:100%; border-radius:2px; }
.pc-bar-val { font-size:0.62rem; color:var(--text); width:24px; text-align:right; font-family:'Space Mono',monospace; }

/* AI Card */
.ai-card { background:linear-gradient(135deg,rgba(139,92,246,0.08),rgba(59,130,246,0.05)); border:1px solid rgba(139,92,246,0.3); border-radius:14px; padding:1.5rem; margin-top:1rem; }
.ai-card .ai-title { font-family:'Bebas Neue',sans-serif; font-size:1.2rem; letter-spacing:3px; color:#A78BFA; margin-bottom:0.8rem; }
.ai-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-family:'Space Mono',monospace; font-size:0.6rem; letter-spacing:2px; margin-right:6px; margin-bottom:6px; }
.ai-pos { background:rgba(201,168,76,0.15); border:1px solid rgba(201,168,76,0.4); color:#F0D080; font-family:'Space Mono',monospace; font-size:0.7rem; letter-spacing:2px; padding:0.4rem 1rem; border-radius:6px; display:inline-block; margin-bottom:0.8rem; }
.ai-section-lbl { font-family:'Space Mono',monospace; font-size:0.58rem; letter-spacing:3px; color:#7A7A92; text-transform:uppercase; margin:0.8rem 0 0.3rem; }
.ai-text { font-size:0.85rem; color:#C8C8D8; line-height:1.6; }
.ai-item { display:flex; align-items:flex-start; gap:0.5rem; margin:0.3rem 0; font-size:0.82rem; color:#C8C8D8; }
.ai-dot-g { color:#10B981; }
.ai-dot-r { color:#EF4444; }
.ai-dot-b { color:#3B82F6; }
.lang-btn { cursor:pointer; }

[data-testid="metric-container"] { background:var(--dark3) !important; border:1px solid var(--border) !important; border-radius:10px !important; padding:1rem !important; }
[data-testid="metric-container"] label { color:var(--text-muted) !important; font-family:'Space Mono',monospace !important; font-size:0.6rem !important; letter-spacing:2px !important; }
[data-testid="metric-container"] [data-testid="metric-value"] { color:var(--gold) !important; font-family:'Bebas Neue',sans-serif !important; font-size:2rem !important; }

.stTabs [data-baseweb="tab-list"] { background:var(--dark2) !important; border-bottom:1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--text-muted) !important; font-family:'Space Mono',monospace !important; font-size:0.62rem !important; letter-spacing:2px !important; padding:0.8rem 1.2rem !important; border:none !important; }
.stTabs [aria-selected="true"] { color:var(--gold) !important; border-bottom:2px solid var(--gold) !important; }
.stTabs [data-baseweb="tab-panel"] { background:var(--dark) !important; padding:1.5rem 0 !important; }

hr { border-color:var(--border) !important; }
.stAlert { background:var(--dark3) !important; border:1px solid var(--border) !important; border-radius:8px !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    # Logo + selector de idioma
    lang_icon = "🇪🇸" if st.session_state.lang == "es" else "🇬🇧"
    other_lang = "en" if st.session_state.lang == "es" else "es"
    other_icon = "🇬🇧" if st.session_state.lang == "es" else "🇪🇸"

    st.markdown(f"""
    <div class="sidebar-logo">
        <div class="brand">SCOUT PRO</div>
        <div class="sub">TALENT ANALYSIS SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"{other_icon} {'English' if st.session_state.lang == 'es' else 'Español'}"):
        st.session_state.lang = other_lang
        st.rerun()

    st.markdown('<div class="sidebar-section">🔑 API KEY</div>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "", placeholder="sk-ant-api...",
        type="password", label_visibility="collapsed",
        key="api_key_field"
    )
    if api_key_input:
        st.session_state.anthropic_api_key = api_key_input

    st.markdown(f'<div class="sidebar-section">⚽ {T("tactics_title")}</div>', unsafe_allow_html=True)
    formacion = st.selectbox("", list(FORMACIONES.keys()), label_visibility="collapsed")

    st.markdown(f'<div class="sidebar-section">👤 {T("player_data")}</div>', unsafe_allow_html=True)
    nombre = st.text_input("", placeholder=T("name_placeholder"), label_visibility="collapsed")

    c1, c2 = st.columns(2)
    with c1:
        pie_opts = [T("right"), T("left"), T("both")]
        pie = st.selectbox(T("foot"), pie_opts)
    with c2:
        altura = st.number_input(T("height"), 100, 220, 175)
    c3, c4 = st.columns(2)
    with c3:
        peso = st.number_input(T("weight"), 1, 200, 72)
    with c4:
        edad = st.number_input("Edad" if st.session_state.lang == "es" else "Age", 6, 45, 15)

    categoria = edad_a_categoria(edad)
    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#7A7A92;letter-spacing:1px;padding:2px 0 0.4rem 0;">
        {"CATEGORÍA" if st.session_state.lang == "es" else "CATEGORY"}: <span style="color:#C9A84C;">{categoria.upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="sidebar-section">📊 {T("skills_section")}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#7A7A92;letter-spacing:1px;padding:0.4rem 0;">
        {T("skills_note")} <span style="color:#C9A84C;">{T("tab_ref")}</span>
    </div>
    """, unsafe_allow_html=True)

    # Posición local
    v = st.session_state.puntajes_tmp
    pos_local, pos_alt_local = motor_posicional_local(v, pie, altura, peso)
    st.markdown(f'<div class="pos-detected">📍 {pos_local.upper()}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.55rem;color:#7A7A92;text-align:center;margin-top:4px;">Alt: {pos_alt_local}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(T("register_btn")):
        if nombre.strip():
            puntajes_reg = list(st.session_state.puntajes_tmp)
            pos_reg, _ = motor_posicional_local(puntajes_reg, pie, altura, peso)
            st.session_state.players.append({
                "name": nombre.strip(),
                "pos": pos_reg,
                "scores": puntajes_reg,
                "avg": round(sum(puntajes_reg) / len(puntajes_reg), 1),
                "foot": pie,
                "h": altura,
                "w": peso,
                "edad": edad,
                "categoria": categoria,
            })
            st.rerun()

# =========================================================
# CANCHA
# =========================================================

def dibujar_cancha(jugadores):
    fig = go.Figure()

    def shape(tipo, x0, y0, x1, y1):
        fig.add_shape(type=tipo, x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color="rgba(255,255,255,0.55)", width=1.5), layer="below")

    for i, shade in enumerate(np.linspace(0.13, 0.22, 12)):
        fig.add_shape(type="rect", x0=i*8.33, y0=0, x1=(i+1)*8.33, y1=100,
                      fillcolor=f"rgba(20,{int(100+shade*100)},30,1)",
                      line_color="rgba(0,0,0,0)", layer="below")

    shape("rect", 0, 0, 100, 100)
    shape("line", 50, 0, 50, 100)
    shape("circle", 41, 41, 59, 59)
    fig.add_shape(type="circle", x0=49.5, y0=49.5, x1=50.5, y1=50.5,
                  fillcolor="rgba(255,255,255,0.6)", line_color="rgba(255,255,255,0.6)", layer="below")
    shape("rect", 0, 18, 16, 82); shape("rect", 84, 18, 100, 82)
    shape("rect", 0, 33, 6, 67); shape("rect", 94, 33, 100, 67)
    shape("rect", 0, 43, 1.5, 57); shape("rect", 98.5, 43, 100, 57)

    for p in jugadores:
        x, y = p["coords"]
        color = get_role_color(p["pos"])
        avg = p.get("avg", 50)

        fig.add_trace(go.Scatter(x=[x], y=[y-1.8], mode="markers",
            marker=dict(size=28, color="rgba(0,0,0,0.4)"), hoverinfo="skip", showlegend=False))

        fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text",
            text=[f"<b>{p['name'][:10]}</b>"], textposition="top center",
            textfont=dict(family="DM Sans", size=10, color="white"),
            marker=dict(size=26, color=color, line=dict(width=2.5, color="white")),
            hovertemplate=f"<b>{p['name']}</b><br>Pos: {p.get('rol_tactico',p['pos'])}<br>Avg: {avg}<extra></extra>",
            showlegend=False))

        fig.add_trace(go.Scatter(x=[x], y=[y], mode="text",
            text=[str(int(avg))], textfont=dict(size=9, color="white"),
            hoverinfo="skip", showlegend=False))

    for rol, color in [("DEF", ROLE_COLORS["DEF"]), ("MID", ROLE_COLORS["MID"]), ("ATT", ROLE_COLORS["ATT"])]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
            marker=dict(size=10, color=color), name=rol, showlegend=True))

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", x=0.5, y=-0.02, xanchor="center",
                    font=dict(family="Space Mono", size=9, color="white"),
                    bgcolor="rgba(0,0,0,0.5)", bordercolor="#7A5E28", borderwidth=1),
        xaxis=dict(visible=False, range=[-2,102]),
        yaxis=dict(visible=False, range=[-5,108]),
        height=620, margin=dict(l=0,r=0,t=0,b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# =========================================================
# RADAR
# =========================================================

def generar_radar(scores, nombre, color="#C9A84C"):
    labels = hab_labels()
    N = len(labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    values = scores + [scores[0]]
    angles += [angles[0]]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#111118")
    ax.set_facecolor("#111118")
    ax.set_ylim(0,100)
    ax.set_yticks([20,40,60,80,100])
    ax.set_yticklabels(["20","40","60","80","100"], color=(1,1,1,0.25), fontsize=6)
    ax.grid(color=(1,1,1,0.08), linewidth=0.8)
    ax.spines['polar'].set_color((1,1,1,0.15))
    ax.fill(angles, values, alpha=0.25, color=color)
    ax.plot(angles, values, linewidth=2.5, color=color)
    ax.scatter(angles[:-1], values[:-1], s=40, color=color, zorder=5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=7, color=(1,1,1,0.85), fontfamily="monospace")
    plt.tight_layout(pad=1.5)
    return fig

def radar_comparacion(p1, p2):
    labels = hab_labels()
    N = len(labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += [angles[0]]
    v1 = p1["scores"] + [p1["scores"][0]]
    v2 = p2["scores"] + [p2["scores"][0]]

    fig, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#111118")
    ax.set_facecolor("#111118")
    ax.set_ylim(0,100)
    ax.set_yticks([20,40,60,80])
    ax.set_yticklabels(["20","40","60","80"], color=(1,1,1,0.25), fontsize=6)
    ax.grid(color=(1,1,1,0.08))
    ax.spines['polar'].set_color((1,1,1,0.15))
    ax.fill(angles, v1, alpha=0.2, color="#C9A84C")
    ax.plot(angles, v1, linewidth=2, color="#C9A84C", label=p1["name"])
    ax.fill(angles, v2, alpha=0.2, color="#3B82F6")
    ax.plot(angles, v2, linewidth=2, color="#3B82F6", label=p2["name"])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=7, color=(1,1,1,0.85), fontfamily="monospace")
    leg = ax.legend(loc="upper right", bbox_to_anchor=(1.35,1.1),
                    facecolor="#1A1A24", edgecolor="#7A5E28", fontsize=9)
    for t in leg.get_texts(): t.set_color("white")
    plt.tight_layout()
    return fig

# =========================================================
# PDF
# =========================================================

def generar_pdf(p, ai_data=None):
    fig_radar = generar_radar(p["scores"], p["name"])
    buf = BytesIO()
    fig_radar.savefig(buf, format="png", bbox_inches="tight", dpi=150, facecolor="#111118")
    plt.close(fig_radar)
    buf.seek(0)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(buf.read()); tmp.close()

    pdf = FPDF(); pdf.add_page()
    W, H = 210, 297

    # Fondo
    pdf.set_fill_color(10,10,15); pdf.rect(0,0,W,H,"F")
    pdf.set_fill_color(20,20,28); pdf.rect(0,0,W,42,"F")
    pdf.set_fill_color(201,168,76); pdf.rect(0,42,W,1.5,"F")

    # Logo
    pdf.set_text_color(201,168,76); pdf.set_font("Arial","B",26)
    pdf.set_xy(12,8); pdf.cell(0,10,"SCOUT PRO")
    pdf.set_text_color(120,120,140); pdf.set_font("Arial","",7)
    pdf.set_xy(12,22); pdf.cell(0,6,"SISTEMA DE ANALISIS Y SEGUIMIENTO DE TALENTO")
    pdf.set_text_color(100,100,120); pdf.set_font("Arial","",7)
    pdf.set_xy(140,30); pdf.cell(0,6,f"REPORTE: {date.today().strftime('%d/%m/%Y')}")

    # Nombre
    pdf.set_text_color(255,255,255); pdf.set_font("Arial","B",28)
    pdf.set_xy(12,50); pdf.cell(0,12, p["name"].upper())

    # Badge posición IA o local
    pos_display = ai_data["posicion_recomendada"] if ai_data else p["pos"]
    pdf.set_fill_color(201,168,76); pdf.set_text_color(0,0,0)
    pdf.set_font("Arial","B",9); pdf.set_xy(12,66)
    pdf.cell(70,7,f"  {pos_display.upper()}",0,0,"L",True)

    if ai_data and "posicion_alternativa" in ai_data:
        pdf.set_fill_color(40,40,60); pdf.set_text_color(180,160,100)
        pdf.set_font("Arial","",8); pdf.set_xy(84,66)
        pdf.cell(60,7,f"  Alt: {ai_data['posicion_alternativa']}",0,0,"L",True)

    # Stats
    stats_data = [("PROMEDIO",str(p["avg"])),("PIE",p["foot"][:3].upper()),("ALTURA",f"{p['h']}cm"),("PESO",f"{p['w']}kg")]
    sx=12
    for label,val in stats_data:
        pdf.set_fill_color(25,25,35); pdf.rect(sx,78,42,20,"F")
        pdf.set_draw_color(60,60,80); pdf.rect(sx,78,42,20,"D")
        pdf.set_text_color(201,168,76); pdf.set_font("Arial","B",14)
        pdf.set_xy(sx,81); pdf.cell(42,8,val,0,0,"C")
        pdf.set_text_color(100,100,120); pdf.set_font("Arial","",6)
        pdf.set_xy(sx,91); pdf.cell(42,5,label,0,0,"C")
        sx+=44

    pdf.set_fill_color(40,40,55); pdf.rect(12,102,W-24,0.5,"F")
    pdf.image(tmp.name, x=110, y=50, w=90)
    os.unlink(tmp.name)

    # Habilidades
    pdf.set_text_color(201,168,76); pdf.set_font("Arial","B",11)
    pdf.set_xy(12,108); pdf.cell(0,8,"ANALISIS DE HABILIDADES")

    habs_list = habs()
    y_start = 120
    for i, (hab, cat) in enumerate(habs_list):
        val = p["scores"][i] if i < len(p["scores"]) else 0
        y = y_start + i*10
        fill = (20,20,30) if i%2==0 else (24,24,36)
        pdf.set_fill_color(*fill); pdf.rect(12,y,W-24,9,"F")
        pdf.set_text_color(220,220,230); pdf.set_font("Arial","",8)
        pdf.set_xy(15,y+1); pdf.cell(45,7,hab)
        cat_colors = {"técnica":(59,130,246),"ataque":(239,68,68),"defensa":(16,185,129),"creación":(139,92,246),"físico":(245,158,11),
                      "technique":(59,130,246),"attack":(239,68,68),"defense":(16,185,129),"creation":(139,92,246),"physical":(245,158,11)}
        cr,cg,cb = cat_colors.get(cat,(100,100,100))
        pdf.set_text_color(cr,cg,cb); pdf.set_font("Arial","",6)
        pdf.set_xy(62,y+2); pdf.cell(20,5,cat.upper())
        pdf.set_fill_color(35,35,50); pdf.rect(88,y+2,90,5,"F")
        if val>=80: pdf.set_fill_color(16,185,129)
        elif val>=60: pdf.set_fill_color(245,158,11)
        else: pdf.set_fill_color(239,68,68)
        pdf.rect(88,y+2,val*0.9,5,"F")
        pdf.set_text_color(255,255,255); pdf.set_font("Arial","B",8)
        pdf.set_xy(182,y+1); pdf.cell(15,7,str(val),0,0,"R")

    # IA Sección en PDF
    y_obs = y_start + len(habs_list)*10 + 6
    if ai_data:
        pdf.set_fill_color(18,18,30); pdf.rect(12,y_obs,W-24,45,"F")
        pdf.set_draw_color(139,92,246); pdf.set_line_width(0.5)
        pdf.rect(12,y_obs,W-24,45)
        pdf.set_text_color(167,139,250); pdf.set_font("Arial","B",9)
        pdf.set_xy(16,y_obs+3); pdf.cell(0,6,"ANALISIS IA — SCOUT PRO")
        pdf.set_text_color(200,200,215); pdf.set_font("Arial","",8)

        if "perfil" in ai_data:
            pdf.set_xy(16,y_obs+11)
            pdf.multi_cell(W-28,5,str(ai_data.get("perfil","")))

        y_rec = y_obs+26
        if "recomendaciones" in ai_data:
            pdf.set_text_color(16,185,129); pdf.set_font("Arial","B",7)
            pdf.set_xy(16,y_rec); pdf.cell(0,5,"RECOMENDACIONES:")
            pdf.set_text_color(180,220,180); pdf.set_font("Arial","",7)
            for rec in ai_data.get("recomendaciones",[])[:2]:
                pdf.set_xy(16,y_rec+5); pdf.cell(0,5,f"• {str(rec)[:80]}")
                y_rec+=5
        y_obs2 = y_obs+46
    else:
        pdf.set_fill_color(20,20,30); pdf.rect(12,y_obs,W-24,26,"F")
        pdf.set_draw_color(201,168,76); pdf.set_line_width(0.5)
        pdf.rect(12,y_obs,W-24,26)
        pdf.set_text_color(201,168,76); pdf.set_font("Arial","B",8)
        pdf.set_xy(16,y_obs+3); pdf.cell(0,6,"OBSERVACION SCOUT")
        pdf.set_text_color(200,200,215); pdf.set_font("Arial","",9)
        pdf.set_xy(16,y_obs+11)
        if p["avg"]>=85: obs="Jugador de perfil elite. Alta proyeccion competitiva. Se recomienda seguimiento inmediato."
        elif p["avg"]>=70: obs="Jugador competitivo con buenas condiciones. Potencial de crecimiento en alto rendimiento."
        else: obs="Jugador en desarrollo. Con trabajo dirigido puede alcanzar un nivel superior."
        pdf.multi_cell(W-28,6,obs)
        y_obs2 = y_obs+28

    # Footer
    pdf.set_fill_color(15,15,22); pdf.rect(0,H-14,W,14,"F")
    pdf.set_fill_color(201,168,76); pdf.rect(0,H-14,W,0.5,"F")
    pdf.set_text_color(80,80,100); pdf.set_font("Arial","I",7)
    pdf.set_xy(0,H-11)
    pdf.cell(W,6,"SCOUT PRO  |  Sistema de Analisis de Talento Deportivo  |  Confidencial",0,0,"C")

    return pdf.output(dest="S").encode("latin-1")

# =========================================================
# MAIN
# =========================================================

n_players = len(st.session_state.players)
avg_team  = round(sum(p["avg"] for p in st.session_state.players)/n_players,1) if n_players else 0
top       = max(st.session_state.players, key=lambda x: x["avg"])["name"] if n_players else "—"

st.markdown(f"""
<div class="hero-header">
    <div>
        <div class="hero-title">{T("app_title")}</div>
        <div class="hero-sub">{T("app_sub")}</div>
    </div>
    <div class="hero-badge">⬤ &nbsp; {T("active")}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="stat-row">
    <div class="stat-chip"><div class="val">{n_players}</div><div class="lbl">{T("players")}</div></div>
    <div class="stat-chip"><div class="val">{avg_team}</div><div class="lbl">{T("team_avg")}</div></div>
    <div class="stat-chip"><div class="val">{formacion}</div><div class="lbl">{T("formation")}</div></div>
    <div class="stat-chip"><div class="val" style="font-size:1rem;padding-top:10px;">{top}</div><div class="lbl">{T("top_player")}</div></div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab0, tab1, tab2, tab3 = st.tabs([T("tab_input"), T("tab_field"), T("tab_stats"), T("tab_compare")])

# ─────────────────────────────────────────────
# TAB 0: INGRESAR HABILIDADES
# ─────────────────────────────────────────────
with tab0:
    st.markdown(f'<div class="section-title">{T("skills_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.63rem;letter-spacing:1px;color:#7A7A92;margin-bottom:0.5rem;">{T("skills_hint")}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace;font-size:0.6rem;letter-spacing:1px;color:#C9A84C;margin-bottom:1.2rem;">
        {"📏 Categoría activa" if st.session_state.lang == "es" else "📏 Active category"}: <b>{categoria.upper()}</b>
        &nbsp;|&nbsp; {"Elegí Manual o Por Marca en cada habilidad" if st.session_state.lang=="es" else "Choose Manual or By Mark for each skill"}
    </div>
    """, unsafe_allow_html=True)

    habs_list = habs()
    cats = {}
    for hab, cat in habs_list:
        cats.setdefault(cat, []).append(hab)

    cat_list = list(cats.items())
    for row_start in range(0, len(cat_list), 4):
        row_cats = cat_list[row_start:row_start+4]
        cols = st.columns(len(row_cats))
        for ci, (cat, cat_habs) in enumerate(row_cats):
            with cols[ci]:
                color_cat = COLORES_CAT.get(cat, "#C9A84C")
                st.markdown(f"""
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;letter-spacing:3px;
                            color:{color_cat};text-transform:uppercase;border-bottom:1px solid {color_cat}33;
                            padding-bottom:6px;margin-bottom:0.8rem;">{cat}</div>
                """, unsafe_allow_html=True)
                for hab in cat_habs:
                    idx = hab_labels().index(hab)
                    prev = st.session_state.puntajes_tmp[idx] if idx < len(st.session_state.puntajes_tmp) else 60

                    nombre_test, unidad, tipo, lower_is_better = test_def_for(idx, st.session_state.lang)
                    modo = st.radio(
                        hab, ["Manual", "📏 Por marca" if st.session_state.lang == "es" else "📏 By mark"],
                        horizontal=True, key=f"modo_{hab}_{st.session_state.lang}", label_visibility="visible"
                    )

                    if modo == "Manual":
                        val = st.number_input("", min_value=0, max_value=100, value=int(prev), step=1,
                                               key=f"ni_{hab}_{st.session_state.lang}", label_visibility="collapsed")
                        st.session_state.puntajes_tmp[idx] = val
                    else:
                        calib = calib_por_categoria(idx, categoria)
                        ref_100 = calib[100]
                        ref_60 = calib[60]
                        st.markdown(f"""
                        <div style="font-family:'Space Mono',monospace;font-size:0.58rem;color:#7A7A92;margin-bottom:2px;">
                            {nombre_test} ({unidad}) — 100: {ref_100} | 60: {ref_60}
                        </div>
                        """, unsafe_allow_html=True)
                        step = 1.0 if tipo == "conteo" else 0.01
                        default_mark = calib[60]
                        marca = st.number_input(
                            "", min_value=0.0, max_value=float(max(calib.values())) * 1.5,
                            value=float(default_mark), step=step,
                            key=f"marca_{hab}_{st.session_state.lang}", label_visibility="collapsed"
                        )
                        val = score_from_mark(marca, calib, lower_is_better)
                        st.session_state.puntajes_tmp[idx] = val
                        st.markdown(f"""
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#C9A84C;margin-top:-4px;">
                            {val:.0f} <span style="font-family:'Space Mono',monospace;font-size:0.55rem;color:#7A7A92;">{"NOTA" if st.session_state.lang=="es" else "SCORE"}</span>
                        </div>
                        """, unsafe_allow_html=True)

    avg_live = round(sum(st.session_state.puntajes_tmp)/len(st.session_state.puntajes_tmp),1)
    nivel_live = T("nivel_elite") if avg_live>=85 else (T("nivel_comp") if avg_live>=70 else T("nivel_dev"))
    color_live = "#10B981" if avg_live>=80 else ("#F59E0B" if avg_live>=65 else "#EF4444")

    st.markdown(f"""
    <div style="margin-top:1.5rem;display:flex;gap:1rem;align-items:center;">
        <div style="background:var(--dark2);border:1px solid var(--border);border-radius:10px;padding:1rem 2rem;text-align:center;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;color:{color_live};line-height:1;">{avg_live}</div>
            <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--text-muted);letter-spacing:2px;">{T("avg_label")}</div>
        </div>
        <div style="background:var(--dark2);border:1px solid var(--border);border-radius:10px;padding:1rem 2rem;text-align:center;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:{color_live};line-height:1;">{nivel_live}</div>
            <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--text-muted);letter-spacing:2px;">{T("level_label")}</div>
        </div>
    </div>
    <div style="margin-top:1rem;font-family:'Space Mono',monospace;font-size:0.65rem;color:#C9A84C;letter-spacing:1px;">
        {T("lateral_hint")}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 1: CANCHA
# ─────────────────────────────────────────────
with tab1:
    jugadores_t = asignar_formacion(st.session_state.players, formacion)
    st.plotly_chart(dibujar_cancha(jugadores_t), use_container_width=True)
    if n_players == 0:
        st.markdown(f"""
        <div style="text-align:center;padding:2rem;color:var(--text-muted);
                    font-family:'Space Mono',monospace;font-size:0.72rem;letter-spacing:2px;">
            {T("field_empty")}
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 2: ESTADÍSTICAS
# ─────────────────────────────────────────────
with tab2:
    if not st.session_state.players:
        st.info(T("no_players"))
    else:
        for i, p in enumerate(st.session_state.players):
            avg = p["avg"]
            color_avg = "#10B981" if avg>=80 else ("#F59E0B" if avg>=65 else "#EF4444")
            nivel = T("nivel_elite") if avg>=85 else (T("nivel_comp") if avg>=70 else T("nivel_dev"))
            ai_key = p["name"]
            ai_data = st.session_state.ai_results.get(ai_key)

            bars_html = ""
            habs_list = habs()
            for j, (hab, cat) in enumerate(habs_list):
                val = p["scores"][j] if j < len(p["scores"]) else 0
                c = COLORES_CAT.get(cat, "#C9A84C")
                bars_html += f"""
                <div class="pc-bar-row">
                    <div class="pc-bar-label">{hab[:12]}</div>
                    <div class="pc-bar-track"><div class="pc-bar-fill" style="width:{val}%;background:{c};"></div></div>
                    <div class="pc-bar-val">{val}</div>
                </div>"""

            pos_show = ai_data["posicion_recomendada"] if ai_data else p["pos"]

            with st.expander(f"📋  {p['name'].upper()}  —  {pos_show}  |  Avg: {avg}", expanded=False):
                st.markdown(f"""
                <div class="player-card" style="margin-bottom:0;">
                    <div class="pc-name">{p['name'].upper()}</div>
                    <div class="pc-pos">{pos_show} &nbsp;|&nbsp; {nivel}</div>
                    <div class="pc-avg" style="color:{color_avg};">{avg}</div>
                    <div class="pc-meta">
                        <span class="pc-tag">🦶 {p['foot']}</span>
                        <span class="pc-tag">📏 {p['h']} cm</span>
                        <span class="pc-tag">⚖️ {p['w']} kg</span>
                        <span class="pc-tag">🎂 {p.get('edad','-')} ({p.get('categoria','-').upper()})</span>
                    </div>
                    <br>{bars_html}
                </div>""", unsafe_allow_html=True)

                col_r, col_right = st.columns([1,1])
                with col_r:
                    fig_r = generar_radar(p["scores"], p["name"])
                    st.pyplot(fig_r, use_container_width=True)
                    plt.close(fig_r)

                with col_right:
                    # Botón IA
                    st.markdown(f'<div class="section-title" style="font-size:1rem;">{T("ai_analysis")}</div>', unsafe_allow_html=True)
                    if st.button(T("ai_btn"), key=f"ia_{i}"):
                        with st.spinner(T("ai_loading")):
                            try:
                                result = analizar_con_ia(p)
                                st.session_state.ai_results[ai_key] = result
                                st.rerun()
                            except Exception as e:
                                st.error(f"{T('ai_error')}: {e}")

                    if ai_data:
                        pot_color = {"ALTO":"#10B981","ALTO":"#10B981","HIGH":"#10B981",
                                     "MEDIO":"#F59E0B","MEDIUM":"#F59E0B",
                                     "BAJO":"#EF4444","LOW":"#EF4444"}.get(ai_data.get("potencial",""), "#C9A84C")
                        st.markdown(f"""
                        <div class="ai-card">
                            <div class="ai-title">🤖 ANÁLISIS IA</div>
                            <div class="ai-pos">📍 {ai_data.get("posicion_recomendada","")}</div>
                            <span class="ai-badge" style="background:rgba(201,168,76,0.1);border:1px solid #7A5E28;color:#F0D080;">
                                Alt: {ai_data.get("posicion_alternativa","")}
                            </span>
                            <span class="ai-badge" style="background:{pot_color}22;border:1px solid {pot_color}55;color:{pot_color};">
                                Potencial: {ai_data.get("potencial","")}
                            </span>
                            <div class="ai-section-lbl">PERFIL</div>
                            <div class="ai-text">{ai_data.get("perfil","")}</div>
                            <div class="ai-section-lbl">FORTALEZAS</div>
                            {"".join(f'<div class="ai-item"><span class="ai-dot-g">▲</span> {f}</div>' for f in ai_data.get("fortalezas",[]))}
                            <div class="ai-section-lbl">ÁREAS DE MEJORA</div>
                            {"".join(f'<div class="ai-item"><span class="ai-dot-r">▼</span> {d}</div>' for d in ai_data.get("debilidades",[]))}
                            <div class="ai-section-lbl">RECOMENDACIONES</div>
                            {"".join(f'<div class="ai-item"><span class="ai-dot-b">→</span> {r}</div>' for r in ai_data.get("recomendaciones",[]))}
                            <div class="ai-section-lbl">SIMILAR A</div>
                            <div class="ai-text" style="color:#C9A84C;">⭐ {ai_data.get("comparacion","")}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # PDF + Eliminar
                col_d, col_x = st.columns([3,1])
                with col_d:
                    try:
                        pdf_bytes = generar_pdf(p, ai_data)
                        st.download_button(T("download_pdf"), pdf_bytes,
                            file_name=f"scout_{p['name'].replace(' ','_')}.pdf",
                            mime="application/pdf", key=f"pdf_{i}")
                    except Exception as e:
                        st.error(f"{T('pdf_error')}: {e}")
                with col_x:
                    if st.button(T("delete"), key=f"del_{i}"):
                        st.session_state.players.pop(i)
                        st.session_state.ai_results.pop(ai_key, None)
                        st.rerun()

# ─────────────────────────────────────────────
# TAB 3: COMPARAR
# ─────────────────────────────────────────────
with tab3:
    if len(st.session_state.players) < 2:
        st.markdown(f"""
        <div style="text-align:center;padding:3rem;color:var(--text-muted);
                    font-family:'Space Mono',monospace;font-size:0.72rem;letter-spacing:2px;">
            {T("compare_need")}
        </div>""", unsafe_allow_html=True)
    else:
        names = [p["name"] for p in st.session_state.players]
        colA, colB = st.columns(2)
        with colA: n1 = st.selectbox(T("player1"), names, key="cmp1")
        with colB: n2 = st.selectbox(T("player2"), [n for n in names if n!=n1], key="cmp2")

        if n1 and n2:
            p1 = next(p for p in st.session_state.players if p["name"]==n1)
            p2 = next(p for p in st.session_state.players if p["name"]==n2)

            fig_cmp = radar_comparacion(p1,p2)
            st.pyplot(fig_cmp, use_container_width=True)
            plt.close(fig_cmp)

            st.markdown(f'<div class="section-title">{T("stats_title")}</div>', unsafe_allow_html=True)
            col1,col2,col3 = st.columns([3,1,1])
            with col1: st.markdown(f"<span style='font-family:Space Mono;font-size:0.7rem;color:var(--text-muted);'>{T('skill_col')}</span>", unsafe_allow_html=True)
            with col2: st.markdown(f"<span style='font-family:Bebas Neue;font-size:1rem;color:#C9A84C;'>{n1[:12]}</span>", unsafe_allow_html=True)
            with col3: st.markdown(f"<span style='font-family:Bebas Neue;font-size:1rem;color:#3B82F6;'>{n2[:12]}</span>", unsafe_allow_html=True)

            habs_list = habs()
            for i,(hab,_) in enumerate(habs_list):
                v1 = p1["scores"][i] if i<len(p1["scores"]) else 0
                v2 = p2["scores"][i] if i<len(p2["scores"]) else 0
                c1 = "#C9A84C" if v1>=v2 else "var(--text-muted)"
                c2 = "#3B82F6" if v2>v1 else "var(--text-muted)"
                col1,col2,col3 = st.columns([3,1,1])
                with col1: st.markdown(f"<span style='font-size:0.8rem;'>{hab}</span>", unsafe_allow_html=True)
                with col2: st.markdown(f"<span style='font-family:Space Mono;color:{c1};font-weight:700;'>{v1}</span>", unsafe_allow_html=True)
                with col3: st.markdown(f"<span style='font-family:Space Mono;color:{c2};font-weight:700;'>{v2}</span>", unsafe_allow_html=True)