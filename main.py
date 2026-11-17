# -*- coding: utf-8 -*-
"""
Система управління доброчесністю v4 — прототип для хакатону.
Запуск: python -m streamlit run main.py
Методика навчальна, не є затвердженим стандартом. Прямі ідентифікатори не збираються.
"""
from __future__ import annotations

import json
import random
import hashlib
import html
import io
import os
import re
import secrets
import sqlite3
import zipfile
import tempfile
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DB_PATH = Path(__file__).resolve().parent / "integrity_dashboard.db"
st.set_page_config(page_title="Система управління доброчесністю", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="expanded")

# ---------- Стиль ----------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {--bg:#0b1220;--panel:#172235;--panel2:#1b2c3c;--line:rgba(148,163,184,.22);
       --cyan:#12c8d5;--blue:#168eea;--muted:#9aabc0;--white:#eef6ff;}
html, body, .stApp, button, input, textarea, [class*="css"] {font-family:'Inter',sans-serif;}
.stApp {background:radial-gradient(ellipse at 78% 8%,rgba(0,180,190,.13),transparent 35%),
        linear-gradient(135deg,#0b1220 0%,#101a2c 55%,#092a32 100%); color:var(--white);}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:rgba(11,18,32,.88);}
.block-container {padding-top:1.25rem; padding-bottom:2.5rem; max-width:1600px;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#171e2c 0%,#111a29 100%);
 border-right:1px solid rgba(148,163,184,.18);}
[data-testid="stSidebar"] > div:first-child {padding-top:1.35rem;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#aab8ca;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:9px 12px;border-radius:9px;
 margin:3px 0;color:#b8c6d8;font-weight:500;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:rgba(31,151,220,.13);color:white;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
 background:linear-gradient(90deg,rgba(22,142,234,.28),rgba(18,200,213,.10));
 color:#55c8ff;border:1px solid rgba(56,189,248,.16);}
[data-testid="stSidebar"] [data-testid="stRadio"] label p {font-size:.93rem;}
[data-testid="stSidebar"] hr {border-color:var(--line);}
h1,h2,h3,h4,h5,p,li,label {color:var(--white);}
small,.stCaption,[data-testid="stCaptionContainer"] {color:var(--muted)!important;}
.hero {background:linear-gradient(110deg,rgba(14,31,54,.96),rgba(8,64,76,.88));
 border:1px solid rgba(80,190,220,.25); color:#fff;padding:24px 28px;border-radius:17px;
 margin:0 0 20px;box-shadow:0 12px 35px rgba(0,0,0,.18);}
.hero h1 {margin:0;font-size:1.9rem;font-weight:750;color:#eaf6ff;padding:0;letter-spacing:-.03em;}
.hero p {margin:7px 0 0;color:#a9bfd2;opacity:1;}
div[data-testid="stMetric"] {background:linear-gradient(145deg,rgba(35,49,69,.94),rgba(21,35,52,.94));
 border:1px solid var(--line);padding:17px 18px;border-radius:15px;min-height:112px;
 box-shadow:0 8px 22px rgba(0,0,0,.12);}
[data-testid="stMetricLabel"] {color:#b6c5d7!important;font-weight:600;}
[data-testid="stMetricValue"] {color:#f4f9ff!important;font-weight:750;}
[data-testid="stMetricDelta"] {font-weight:600;}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stExpander"] {
 border-radius:15px;border-color:var(--line);}
.stTabs [data-baseweb="tab-list"] {gap:7px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"] {border-radius:9px 9px 0 0;padding:10px 16px;color:#aabbd0;}
.stTabs [aria-selected="true"] {color:#42c9f1!important;border-bottom-color:#19b9d0!important;}
.stButton>button,.stDownloadButton>button {border-radius:10px;font-weight:650;
 border:1px solid rgba(65,185,220,.28);background:linear-gradient(110deg,#126e9d,#087d85);
 color:white;transition:all .18s ease;}
.stButton>button:hover,.stDownloadButton>button:hover {border-color:#40d4e5;color:white;
 box-shadow:0 0 0 3px rgba(18,200,213,.12);}
input,textarea,[data-baseweb="select"] > div {background:#172438!important;color:#edf6ff!important;
 border-color:rgba(148,163,184,.28)!important;border-radius:9px!important;}
[data-testid="stDataFrame"],[data-testid="stTable"] {border:1px solid var(--line);border-radius:12px;overflow:hidden;}
[data-testid="stAlert"] {border-radius:12px;}
.pill {display:inline-block;padding:2px 12px;border-radius:999px;font-size:.78rem;font-weight:600;color:#fff;}
button[data-baseweb="tab"] {font-weight:600;}
hr {border-color:var(--line)!important;}

/* Контрастність: примусово узгоджуємо текст і фон усіх віджетів Streamlit */
.stApp, .stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdownContainer"] span,
.stApp [data-testid="stMarkdownContainer"] strong,
.stApp [data-testid="stMarkdownContainer"] em {color:#eaf2ff;}
.stApp [data-testid="stWidgetLabel"],
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stCheckbox"] label,
.stApp [data-testid="stRadio"] label,
.stApp [data-testid="stSelectbox"] label,
.stApp [data-testid="stMultiSelect"] label,
.stApp [data-testid="stTextInput"] label,
.stApp [data-testid="stNumberInput"] label,
.stApp [data-testid="stDateInput"] label,
.stApp [data-testid="stTimeInput"] label,
.stApp [data-testid="stTextArea"] label,
.stApp [data-testid="stSlider"] label {color:#dce8f7!important;}
.stApp input, .stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea,
.stApp [data-baseweb="select"] input {background:#172438!important;color:#f4f8ff!important;
 -webkit-text-fill-color:#f4f8ff!important;caret-color:#ffffff!important;}
.stApp input::placeholder,.stApp textarea::placeholder {color:#9aabc0!important;opacity:1!important;}
.stApp [data-baseweb="select"] > div,
.stApp [data-baseweb="popover"] [role="listbox"],
.stApp [data-baseweb="menu"],
.stApp [data-baseweb="popover"] {background:#172438!important;color:#f4f8ff!important;
 border-color:rgba(148,163,184,.35)!important;}
.stApp [role="option"],.stApp [role="listbox"] *,
.stApp [data-baseweb="menu"] * {color:#edf5ff!important;}
.stApp [role="option"]:hover,.stApp [aria-selected="true"] {background:#24415a!important;}
.stApp [data-testid="stExpander"],
.stApp [data-testid="stVerticalBlockBorderWrapper"] {background:rgba(23,34,53,.72)!important;
 border-color:var(--line)!important;}
.stApp [data-testid="stExpander"] summary,
.stApp [data-testid="stExpander"] summary span,
.stApp [data-testid="stExpander"] summary p {color:#edf5ff!important;}
/* Повідомлення st.info / st.warning / st.error: темний фон на всіх внутрішніх контейнерах */
.stApp [data-testid="stAlert"] {
 background:#172b45!important;
 background-color:#172b45!important;
 color:#f4f8ff!important;
 border:1px solid rgba(65,185,220,.30)!important;
 border-radius:12px!important;
}
/* Streamlit/BaseWeb може задавати білий фон внутрішньому контейнеру повідомлення */
.stApp [data-testid="stAlert"] > div,
.stApp [data-testid="stAlert"] [role="alert"],
.stApp [data-testid="stAlert"] [data-baseweb="notification"],
.stApp [data-testid="stAlert"] [data-testid="stAlertContent"],
.stApp [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
 background:transparent!important;
 background-color:transparent!important;
 color:#f4f8ff!important;
}
.stApp [data-testid="stAlert"] p,
.stApp [data-testid="stAlert"] span,
.stApp [data-testid="stAlert"] strong,
.stApp [data-testid="stAlert"] a,
.stApp [data-testid="stAlert"] div {color:#f4f8ff!important;}
.stApp [data-testid="stAlert"] svg {fill:#55cfff!important;color:#55cfff!important;}
.stApp [data-testid="stDataFrame"],.stApp [data-testid="stTable"] {color:#edf5ff!important;}
.stApp [data-testid="stDataFrame"] *, .stApp [data-testid="stTable"] * {color:inherit;}
.stApp [data-testid="stForm"] {border-color:var(--line)!important;}
.stApp [data-testid="stFileUploader"] section {background:#172438!important;color:#edf5ff!important;
 border:1px dashed rgba(148,163,184,.4)!important;}
.stApp [data-testid="stFileUploader"] small,
.stApp [data-testid="stFileUploader"] span {color:#dce8f7!important;}
.stApp [data-testid="stMetric"] [data-testid="stMetricLabel"] {color:#c6d4e5!important;}
.stApp [data-testid="stMetric"] [data-testid="stMetricValue"] {color:#ffffff!important;}
.stApp [data-testid="stCaptionContainer"],.stApp .stCaption {color:#aebed1!important;}
.stApp [data-testid="stMarkdownContainer"] a {color:#55cfff!important;}
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {color:#dce8f7;}

/* Єдина темна палітра для всіх полів: прибираємо білі вставки BaseWeb/Streamlit */
.stApp [data-baseweb="select"] > div,
.stApp [data-baseweb="select"] > div > div,
.stApp [data-baseweb="input"] > div,
.stApp [data-baseweb="textarea"] > div,
.stApp [data-testid="stDateInput"] [data-baseweb="input"] > div,
.stApp [data-testid="stTimeInput"] [data-baseweb="input"] > div,
.stApp [data-testid="stNumberInput"] [data-baseweb="input"] > div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background:#172438!important;
  color:#f4f8ff!important;
  border-color:rgba(148,163,184,.35)!important;
}
.stApp [data-baseweb="select"] svg,
.stApp [data-baseweb="input"] svg,
.stApp [data-testid="stNumberInput"] button,
.stApp [data-testid="stDateInput"] button,
.stApp [data-testid="stTimeInput"] button {
  color:#dce8f7!important;
  fill:#dce8f7!important;
  background:#20334b!important;
}
.stApp [data-baseweb="popover"],
.stApp [data-baseweb="popover"] > div,
.stApp [data-baseweb="calendar"],
.stApp [data-baseweb="calendar"] > div,
.stApp [role="dialog"],
.stApp [role="listbox"],
.stApp [role="option"] {
  background:#172438!important;
  color:#f4f8ff!important;
  border-color:rgba(148,163,184,.35)!important;
}
.stApp [data-baseweb="calendar"] *,
.stApp [role="dialog"] *,
.stApp [data-baseweb="popover"] * {color:#edf5ff!important;}
.stApp [data-baseweb="tag"] {
  background:#24415a!important;
  color:#f4f8ff!important;
  border:1px solid rgba(65,185,220,.3)!important;
}
.stApp [data-testid="stCheckbox"] [role="checkbox"],
.stApp [data-testid="stRadio"] [role="radio"] {
  background:#172438!important;
  border-color:#6c829c!important;
}
.stApp [data-testid="stFileUploader"] button,
.stApp [data-testid="stLinkButton"] a {
  background:linear-gradient(110deg,#126e9d,#087d85)!important;
  color:#ffffff!important;
}
.stApp [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
  background:transparent!important;
}

</style>""", unsafe_allow_html=True)

def hero(title: str, sub: str) -> None:
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{sub}</p></div>', unsafe_allow_html=True)

def pill(text: str, color: str) -> str:
    return f'<span class="pill" style="background:{color}">{text}</span>'

def style(fig, h: int = 360):
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_family="Inter", margin=dict(l=10, r=10, t=30, b=10))
    return fig

# ---------- Методика ----------
THRESHOLD, GAP_ALERT, MIN_RESPONDENTS, MIN_GROUP = 70, 20, 5, 3
QUESTIONS = [
    ("Прозорість", "Чи доступні працівникам зрозумілі правила та процедури прийняття рішень?"),
    ("Прозорість", "Чи зрозуміло, за якими критеріями ухвалюються важливі рішення?"),
    ("Прозорість", "Чи доводиться інформація про важливі рішення до зацікавлених працівників?"),
    ("Підзвітність", "Чи визначені відповідальні особи за ключові процеси та рішення?"),
    ("Підзвітність", "Чи перевіряється виконання доручень і встановлених процедур?"),
    ("Підзвітність", "Чи передбачені зрозумілі наслідки за порушення правил?"),
    ("Запобігання корупції", "Чи існують чіткі правила запобігання корупції?"),
    ("Запобігання корупції", "Чи визначено порядок дій у разі конфлікту інтересів?"),
    ("Запобігання корупції", "Чи мають працівники можливість безпечно повідомляти про порушення?"),
    ("Етична культура", "Чи проводяться регулярні навчання з питань доброчесності?"),
    ("Етична культура", "Чи знають працівники, до кого звертатися з етичними питаннями?"),
    ("Етична культура", "Чи підтримує керівництво прикладом дотримання етичних принципів?"),
    ("Контроль і реагування", "Чи реєструються повідомлення про можливі порушення?"),
    ("Контроль і реагування", "Чи розглядаються повідомлення у визначені строки?"),
    ("Контроль і реагування", "Чи вживаються коригувальні заходи за результатами перевірок?"),
]
DOMAINS = list(dict.fromkeys(q[0] for q in QUESTIONS))
ANSWER_SCORES = {"Так": 100, "Частково": 50, "Ні": 0}
SKIP = "Не можу оцінити"
ANSWER_OPTIONS = ["Так", "Частково", "Ні", SKIP]
MODES = ["Самооцінювання", "Експертне оцінювання"]
UNITS = ["Керівництво", "Адміністративний підрозділ", "Операційний підрозділ", "Контрольний підрозділ", "Інше"]
STATUSES = ["Заплановано", "У процесі", "Виконано"]
OBJECTIVE_FIELDS = {
    "Прозорість": ["Частка процедур із доступними письмовими правилами (%)",
                   "Частка рішень із документованим обґрунтуванням (%)"],
    "Підзвітність": ["Частка ключових процесів із визначеними відповідальними (%)",
                     "Частка заходів, виконаних у строк (%)"],
    "Запобігання корупції": ["Частка працівників, ознайомлених з антикорупційними правилами (%)",
                             "Частка конфліктів інтересів, щодо яких вжито заходів (%)"],
    "Етична культура": ["Частка працівників, які пройшли навчання (%)",
                        "Частка працівників, які підтвердили ознайомлення з кодексом етики (%)"],
    "Контроль і реагування": ["Частка повідомлень, опрацьованих у встановлений строк (%)",
                              "Частка рекомендацій/коригувальних заходів, виконаних у строк (%)"],
}
GUIDANCE = {
    "Прозорість": ("Недостатня прозорість процедур",
                   "Оприлюднити/довести до працівників правила, критерії ухвалення рішень та порядок документування."),
    "Підзвітність": ("Недостатня визначеність відповідальності",
                     "Закріпити відповідальних за ключові процеси, строки та регулярну перевірку виконання."),
    "Запобігання корупції": ("Потребують посилення антикорупційні механізми",
                             "Оновити антикорупційні процедури, порядок врегулювання конфлікту інтересів і безпечні канали повідомлення."),
    "Етична культура": ("Недостатній рівень етичного навчання",
                        "Запровадити план регулярних навчань, інструктажів та перевірки обізнаності працівників."),
    "Контроль і реагування": ("Потребує покращення реагування на порушення",
                              "Визначити порядок реєстрації, розгляду повідомлень, контролю строків і виконання коригувальних заходів."),
}
EXTRA_MEASURES = {
    "Прозорість": ["Створити єдиний реєстр процедур і критеріїв рішень, доступний усім працівникам.",
                   "Запровадити обов'язкове письмове обґрунтування ключових рішень."],
    "Підзвітність": ["Затвердити матрицю відповідальності для ключових процесів.",
                     "Запровадити щомісячний звіт про виконання доручень."],
    "Запобігання корупції": ["Провести оцінку корупційних ризиків і оновити антикорупційну програму.",
                             "Запровадити реєстр конфліктів інтересів і щоквартальні декларації."],
    "Етична культура": ["Провести тренінги для керівників щодо етичного лідерства.",
                        "Запровадити коротке щорічне тестування з кодексу етики."],
    "Контроль і реагування": ["Запровадити єдиний журнал повідомлень зі строками розгляду.",
                              "Проводити щоквартальний аудит виконання коригувальних заходів."],
}
THEMES = {"Навчання": ["навч", "тренінг"], "Канали повідомлення": ["повідом", "скарг", "гаряч"],
          "Керівництво": ["керів", "начальн"], "Прозорість": ["прозор", "критері", "правил"],
          "Конфлікт інтересів": ["конфлікт"]}

def nav_radio(pages, label_visibility="collapsed"):
    role = st.sidebar.selectbox("Роль", ["Респондент", "Адміністратор"])
    if role == "Респондент":
        return st.sidebar.radio("Розділи", [pages[1]], label_visibility=label_visibility)
    configured = os.environ.get("INTEGRITY_ADMIN_PW", "").strip()
    if not configured:
        st.sidebar.error("Пароль адміністратора не налаштовано.")
        st.info("Для доступу адміністратора задайте змінну середовища INTEGRITY_ADMIN_PW і перезапустіть застосунок. Пароль за замовчуванням вимкнено.")
        st.stop()
    pw = st.sidebar.text_input("Пароль адміністратора", type="password")
    if not secrets.compare_digest(pw, configured):
        if pw:
            st.sidebar.error("Невірний пароль")
        st.info("Введіть пароль адміністратора в бічній панелі.")
        st.stop()
    st.sidebar.success("Режим адміністратора")
    full = pages[:4] + ["🎯 Цілі та сценарії", "🔑 Коди доступу"] + pages[4:]
    return st.sidebar.radio("Розділи", full, label_visibility=label_visibility)

def load_targets() -> dict:
    with db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key='targets'").fetchone()
    saved = json.loads(row["value"]) if row else {}
    return {d: float(saved.get(d, 80)) for d in DOMAINS}

def save_targets(t: dict) -> None:
    with db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings VALUES ('targets', ?)", (json.dumps(t, ensure_ascii=False),))
        conn.commit()

def hash_code(c: str) -> str:
    return hashlib.sha256(c.encode()).hexdigest()

def codes_enabled() -> bool:
    with db() as conn:
        return conn.execute("SELECT COUNT(*) FROM access_codes").fetchone()[0] > 0

def use_code(c: str) -> bool:
    with db() as conn:
        cur = conn.execute("UPDATE access_codes SET used=1 WHERE hash=? AND used=0", (hash_code(c),))
        conn.commit()
        return cur.rowcount == 1

def forecast(vals: list) -> float:
    n = len(vals)
    if n < 2:
        return vals[-1]
    xm, ym = (n - 1) / 2, sum(vals) / n
    b = sum((i - xm) * (v - ym) for i, v in enumerate(vals)) / sum((i - xm) ** 2 for i in range(n))
    return max(0.0, min(100.0, ym + b * (n - xm)))

def declining(vals: list) -> bool:
    return len(vals) >= 3 and vals[-1] < vals[-2] < vals[-3]

def deadline_banner() -> None:
    with db() as conn:
        acts = conn.execute("SELECT due_date FROM actions WHERE status!='Виконано' AND due_date!=''").fetchall()
    od = soon = 0
    for a in acts:
        try:
            d = date.fromisoformat(a["due_date"])
        except ValueError:
            continue
        if d < date.today():
            od += 1
        elif (d - date.today()).days <= 7:
            soon += 1
    if od:
        st.error(f"🔴 Прострочених заходів: {od}")
    if soon:
        st.warning(f"⏰ Строк спливає протягом 7 днів: {soon}")

def report_docx(md: str):
    try:
        from docx import Document
    except ImportError:
        return None
    doc = Document()
    for line in md.splitlines():
        t = line.replace("**", "").strip("_")
        if line.startswith("# "): doc.add_heading(t[2:], 0)
        elif line.startswith("## "): doc.add_heading(t[3:], 1)
        elif line.startswith("- "): doc.add_paragraph(t[2:], style="List Bullet")
        elif t.strip(): doc.add_paragraph(t)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

def report_pdf(md: str):
    """Створює PDF через ReportLab; повертає None, якщо залежність відсутня."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    # Unicode font fallback: Windows fonts are optional; Helvetica remains usable for Latin text.
    font_name = "Helvetica"
    candidates = [Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/ARIAL.TTF"),
                  Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
    for fp in candidates:
        if fp.exists():
            try:
                pdfmetrics.registerFont(TTFont("ArialUnicode", str(fp)))
                font_name = "ArialUnicode"
                break
            except Exception:
                pass
    styles.add(ParagraphStyle(name="UA_Title", parent=styles["Title"], fontName=font_name, textColor=colors.HexColor("#0f766e"), alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="UA_H2", parent=styles["Heading2"], fontName=font_name, textColor=colors.HexColor("#1d4ed8"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="UA_Body", parent=styles["BodyText"], fontName=font_name, leading=15, spaceAfter=5))
    story = []
    for line in md.splitlines():
        raw = html.escape(line.replace("**", "").replace("_", ""))
        if line.startswith("# "):
            story.append(Paragraph(raw[2:], styles["UA_Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(raw[3:], styles["UA_H2"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + raw[2:], styles["UA_Body"]))
        elif raw.strip():
            story.append(Paragraph(raw, styles["UA_Body"]))
        else:
            story.append(Spacer(1, 5))
    doc.build(story)
    return buf.getvalue()

def report_html(md: str) -> str:
    out = []
    for line in md.splitlines():
        t = html.escape(line.replace("**", "").strip("_"))
        out.append(f"<h1>{t[2:]}</h1>" if line.startswith("# ") else f"<h2>{t[3:]}</h2>" if line.startswith("## ")
                   else f"<p>• {t[2:]}</p>" if line.startswith("- ") else f"<p>{t}</p>" if t.strip() else "")
    return ("<html><head><meta charset='utf-8'><style>body{font-family:Arial;max-width:800px;margin:30px auto}"
            "</style></head><body>" + "\n".join(out) + "</body></html>")

PII = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d\s\-()]{8,}\d")

# ---------- База даних ----------
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def add_col(conn, table: str, col: str, ddl: str) -> None:
    if col not in [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")

def init_db() -> None:
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, period TEXT NOT NULL,
            mode TEXT NOT NULL, answers_json TEXT NOT NULL, objective_json TEXT NOT NULL DEFAULT '{}',
            note TEXT NOT NULL DEFAULT '')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, domain TEXT NOT NULL,
            problem TEXT NOT NULL, recommendation TEXT NOT NULL, responsible TEXT NOT NULL DEFAULT '',
            due_date TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Заплановано')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS objective_by_period (
            period TEXT PRIMARY KEY, data_json TEXT NOT NULL, source_note TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL)""")
        conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS access_codes (hash TEXT PRIMARY KEY, used INTEGER NOT NULL DEFAULT 0)")
        conn.execute("CREATE TABLE IF NOT EXISTS action_log (id INTEGER PRIMARY KEY AUTOINCREMENT, action_id INTEGER NOT NULL, at TEXT NOT NULL, status TEXT NOT NULL, comment TEXT NOT NULL DEFAULT '')")
        add_col(conn, "assessments", "unit", "TEXT NOT NULL DEFAULT 'Не вказано'")
        add_col(conn, "actions", "priority", "TEXT NOT NULL DEFAULT 'Середній'")
        conn.commit()

def load_assessments() -> pd.DataFrame:
    with db() as conn:
        rows = conn.execute("SELECT * FROM assessments ORDER BY created_at DESC, id DESC").fetchall()
    if not rows:
        return pd.DataFrame()
    recs = []
    for r in rows:
        rec = dict(r)
        rec["answers"] = json.loads(rec.pop("answers_json"))
        rec.pop("objective_json", None)
        recs.append(rec)
    return pd.DataFrame(recs)

def load_objective(period: str) -> tuple[dict, str]:
    with db() as conn:
        row = conn.execute("SELECT data_json, source_note FROM objective_by_period WHERE period=?", (period,)).fetchone()
    return (json.loads(row["data_json"]), row["source_note"]) if row else ({}, "")

# ---------- Розрахунки ----------
def score_answers(answers: dict) -> tuple[dict, float, int]:
    ds, n = {}, 0
    for domain in DOMAINS:
        vals = [ANSWER_SCORES[answers.get(str(i))] for i, (d, _) in enumerate(QUESTIONS)
                if d == domain and answers.get(str(i)) in ANSWER_SCORES]
        if vals:
            ds[domain] = sum(vals) / len(vals)
            n += len(vals)
    return ds, (sum(ds.values()) / len(ds) if ds else 0.0), n

def aggregate(df: pd.DataFrame) -> tuple[dict, float, int]:
    per = {d: [] for d in DOMAINS}
    for answers in df["answers"]:
        for d, v in score_answers(answers)[0].items():
            per[d].append(v)
    ds = {d: sum(v) / len(v) for d, v in per.items() if v}
    return ds, (sum(ds.values()) / len(ds) if ds else 0.0), len(df)

def question_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, (d, q) in enumerate(QUESTIONS):
        vals = [ANSWER_SCORES[a[str(i)]] for a in df["answers"] if a.get(str(i)) in ANSWER_SCORES]
        rows.append({"Компонент": d, "Питання": q, "Оцінка": sum(vals) / len(vals) if vals else None,
                     "Відповідей": len(vals)})
    return pd.DataFrame(rows)

def objective_scores(obj: dict) -> dict:
    out = {}
    for d, fields in OBJECTIVE_FIELDS.items():
        vals = [float(obj[f]) for f in fields if obj.get(f) not in (None, "")]
        if vals:
            out[d] = sum(vals) / len(vals)
    return out

init_db()

# ---------- Навігація ----------
st.sidebar.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding:4px 2px 12px">
 <div style="width:34px;height:34px;border-radius:50%;border:5px solid #16c6c8;
 border-right-color:transparent;transform:rotate(-35deg);"></div>
 <div style="font-size:1.15rem;font-weight:800;letter-spacing:.04em;color:#eef6ff">INTEGRITY</div>
</div>
<div style="font-size:.76rem;color:#8fa3b9;line-height:1.45;margin-bottom:14px">
СИСТЕМА УПРАВЛІННЯ ДОБРОЧЕСНІСТЮ</div>
""", unsafe_allow_html=True)
page = nav_radio(["📊 Огляд", "📝 Пройти оцінювання", "📎 Об'єктивні показники",
                                    "✅ Рекомендації та заходи", "📦 Дані та експорт", "📅 Календар заходів",
                                    "🏢 Порівняння підрозділів", "🕘 Історія оцінювання", "💾 Резервне копіювання",
                                    "🔐 Захист і ролі", "📘 Методика"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("🔒 Анкети анонімні: імена, email, телефони та IP не зберігаються.")

# Вага опитування задається в бічній панелі (прозорість методики).
W_SURVEY = 0.6
if page != "📝 Пройти оцінювання":
    with st.sidebar.expander("⚙️ Параметри методики"):
        W_SURVEY = st.slider("Вага опитування, %", 0, 100, 60, 5) / 100
        st.caption(f"Вага об'єктивних даних: {(1 - W_SURVEY):.0%}")
W_OBJ = 1 - W_SURVEY

def combine(survey: dict, obj: dict) -> dict:
    return {d: (W_SURVEY * survey[d] + W_OBJ * obj[d]) if d in obj else survey[d] for d in DOMAINS if d in survey}

def compute(df: pd.DataFrame, period: str) -> dict:
    sub = df[df["period"] == period]
    survey, s_idx, n = aggregate(sub)
    obj, src = load_objective(period)
    obj_s = objective_scores(obj)
    comb = combine(survey, obj_s)
    return dict(sub=sub, survey=survey, s_idx=s_idx, n=n, obj_s=obj_s, src=src, comb=comb,
                idx=sum(comb.values()) / len(comb) if comb else 0.0)

def index_label(v: float) -> str:
    return ("Високий демонстраційний рівень" if v >= 85 else "Достатній демонстраційний рівень" if v >= 70
            else "Рівень потребує покращення" if v >= 50 else "Критична зона уваги")

def level_color(v: float) -> str:
    return "#10b981" if v >= 85 else "#22c55e" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444"

def period_list(df: pd.DataFrame) -> list[str]:
    return df.groupby("period")["id"].max().sort_values(ascending=False).index.tolist()

def effective_status(status: str, due: str) -> str:
    if status != "Виконано" and due:
        try:
            if date.fromisoformat(due) < date.today():
                return "Прострочено"
        except ValueError:
            pass
    return status

def gauge(v: float) -> go.Figure:
    fig = go.Figure(go.Indicator(mode="gauge+number", value=v, number={"font": {"size": 46}},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": level_color(v), "thickness": .3},
               "steps": [{"range": [0, 50], "color": "rgba(239,68,68,.18)"},
                         {"range": [50, 70], "color": "rgba(245,158,11,.18)"},
                         {"range": [70, 85], "color": "rgba(34,197,94,.16)"},
                         {"range": [85, 100], "color": "rgba(16,185,129,.30)"}]}))
    return style(fig, 300)

def build_report(df: pd.DataFrame, period: str) -> str:
    R = compute(df, period)
    L = [f"# Звіт: оцінювання доброчесності ({period})", "",
         f"**Індекс доброчесності:** {R['idx']:.1f}/100 — {index_label(R['idx'])}",
         f"**Респондентів:** {R['n']}",
         f"**Ваги:** опитування {W_SURVEY:.0%}, об'єктивні дані {W_OBJ:.0%}", "", "## Компоненти"]
    L += [f"- {d}: {v:.1f}" for d, v in R["comb"].items()]
    L += ["", "## Рекомендації"]
    L += [f"- **{d}** ({v:.0f}): {GUIDANCE[d][1]}" for d, v in R["comb"].items() if v < THRESHOLD] or ["- Критичних зон не виявлено."]
    with db() as conn:
        acts = conn.execute("SELECT * FROM actions ORDER BY id").fetchall()
    L += ["", "## План заходів"]
    L += [f"- [{effective_status(a['status'], a['due_date'])}] {a['domain']} ({a['priority']}): "
          f"{a['recommendation']} · відповідальний: {a['responsible'] or '—'} · строк: {a['due_date'] or '—'}"
          for a in acts] or ["- Заходів немає."]
    L += ["", "_Індекс орієнтовний і не доводить наявність чи відсутність корупції._"]
    return "\n".join(L)

def seed_demo_data() -> None:
    with db() as conn:
        if conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]:
            return
        rng = random.Random(42)
        for period, p_yes, base in [("2026-Q2", .35, 60), ("2026-Q3", .55, 72)]:
            for k in range(10):
                ans = {str(i): rng.choices(["Так", "Частково", "Ні"], [p_yes, .4, 1.05 - p_yes - .4])[0]
                       for i in range(len(QUESTIONS))}
                conn.execute("INSERT INTO assessments (created_at, period, mode, answers_json, note, unit) VALUES (?,?,?,?,?,?)",
                             (datetime.now().isoformat(timespec="seconds"), period, MODES[1 if k >= 8 else 0],
                              json.dumps(ans, ensure_ascii=False), "Умовні демонстраційні дані.", UNITS[k % 4]))
            obj = {f: min(100, max(0, base + rng.randint(-12, 12))) for fs in OBJECTIVE_FIELDS.values() for f in fs}
            conn.execute("INSERT OR REPLACE INTO objective_by_period VALUES (?,?,?,?)",
                         (period, json.dumps(obj, ensure_ascii=False), "Умовні дані",
                          datetime.now().isoformat(timespec="seconds")))
        conn.commit()



def pick_period(df: pd.DataFrame, key: str) -> str:
    return st.selectbox("Період", period_list(df), key=key)

# ---------- Огляд ----------
if page == "📊 Огляд":
    hero("Панель управління доброчесністю", "Сильні сторони, проблемні компоненти та динаміка змін")
    deadline_banner()
    df_all = load_assessments()
    if df_all.empty:
        st.info("Поки немає оцінювань. Пройдіть оцінювання або додайте демо-дані в розділі «Методика».")
        st.stop()
    f1, f2 = st.columns(2)
    mode_f = f1.selectbox("Тип оцінювання", ["Усі"] + MODES)
    df = df_all if mode_f == "Усі" else df_all[df_all["mode"] == mode_f]
    if df.empty:
        st.warning("Для цього типу оцінювання даних немає.")
        st.stop()
    with f2:
        period = pick_period(df, "ov_period")
    R = compute(df, period)
    periods = period_list(df)
    pos = periods.index(period)
    delta = None
    if pos + 1 < len(periods):
        prev = compute(df, periods[pos + 1])
        delta = R["idx"] - prev["idx"] if prev["comb"] else None

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Індекс доброчесності", f"{R['idx']:.1f}", None if delta is None else f"{delta:+.1f} до попер. періоду")
    m2.metric("Рівень", index_label(R["idx"]).replace(" демонстраційний рівень", ""))
    m3.metric("Респондентів", R["n"])
    m4.metric("Індекс опитування", f"{R['s_idx']:.1f}")
    if R["n"] < MIN_RESPONDENTS:
        st.warning(f"Лише {R['n']} відповідей (мінімум {MIN_RESPONDENTS}). Висновки ненадійні.")

    t1, t2, t3, t4 = st.tabs(["Зведення", "Питання та підрозділи", "Опитування vs дані", "Прозорий розрахунок"])

    with t1:
        c1, c2 = st.columns(2)
        dom_df = pd.DataFrame({"Компонент": list(R["comb"]), "Оцінка": list(R["comb"].values())})
        with c1:
            st.markdown("##### Загальний індекс")
            st.plotly_chart(gauge(R["idx"]), width="stretch")
        with c2:
            st.markdown("##### Профіль за компонентами")
            fig = px.line_polar(dom_df, r="Оцінка", theta="Компонент", line_close=True, range_r=[0, 100])
            fig.update_traces(fill="toself", line_color="#1d4ed8")
            st.plotly_chart(style(fig, 300), width="stretch")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("##### Оцінки за компонентами")
            fig = px.bar(dom_df, x="Компонент", y="Оцінка", range_y=[0, 100], text=dom_df["Оцінка"].round(1),
                         color="Оцінка", color_continuous_scale="RdYlGn", range_color=[0, 100])
            fig.add_hline(y=THRESHOLD, line_dash="dash", annotation_text=f"Поріг {THRESHOLD}")
            tg = load_targets()
            fig.add_scatter(x=dom_df["Компонент"], y=[tg[d] for d in dom_df["Компонент"]], mode="markers", name="Ціль",
                            marker=dict(symbol="diamond", size=12, color="#0f172a"))
            fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(style(fig, 330), width="stretch")
        with c4:
            st.markdown("##### Динаміка")
            trend = []
            for p in reversed(periods):
                rp_ = compute(df, p)
                trend.append({"Період": p, "Індекс": rp_["idx"], "Респондентів": rp_["n"]})
            if len(trend) > 1:
                fig = px.line(pd.DataFrame(trend), x="Період", y="Індекс", markers=True, range_y=[0, 100],
                              hover_data=["Респондентів"])
                fig.update_traces(line_color="#7c3aed", line_width=3)
                tvals = [t["Індекс"] for t in trend]
                fig.add_scatter(x=[trend[-1]["Період"], "Прогноз"], y=[tvals[-1], forecast(tvals)], mode="lines+markers",
                                line=dict(dash="dash", color="#94a3b8"), name="Прогноз")
                if declining(tvals):
                    st.error("📉 Індекс знижується три періоди поспіль.")
                fig.update_layout(xaxis_title="", yaxis_title="")
                st.plotly_chart(style(fig, 330), width="stretch")
            else:
                st.caption("Для динаміки потрібно щонайменше два періоди.")
        s1, s2 = st.columns(2)
        s1.markdown("##### 💪 Сильні сторони")
        s2.markdown("##### ⚠️ Проблемні компоненти")
        strong = {d: v for d, v in R["comb"].items() if v >= THRESHOLD}
        weak = {d: v for d, v in R["comb"].items() if v < THRESHOLD}
        for d, v in sorted(strong.items(), key=lambda x: -x[1]):
            s1.success(f"{d}: {v:.1f}")
        for d, v in sorted(weak.items(), key=lambda x: x[1]):
            s2.warning(f"{d}: {v:.1f}")
        if not strong: s1.caption("Немає компонентів вище порога.")
        if not weak: s2.caption("Усі компоненти вище порога.")

    with t2:
        qs = question_stats(R["sub"]).dropna(subset=["Оцінка"]).sort_values("Оцінка").head(8)
        st.markdown("##### Найслабші питання")
        fig = px.bar(qs, x="Оцінка", y="Питання", orientation="h", range_x=[0, 100], color="Оцінка",
                     color_continuous_scale="RdYlGn", range_color=[0, 100], text=qs["Оцінка"].round(0))
        fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="", yaxis=dict(autorange="reversed"))
        st.plotly_chart(style(fig, 380), width="stretch")

        st.markdown("##### Теплова карта за підрозділами")
        rows, hidden = {}, 0
        for u, g in R["sub"].groupby("unit"):
            if len(g) >= MIN_GROUP:
                rows[f"{u} (відповідей: {len(g)})"] = aggregate(g)[0]
            else:
                hidden += 1
        if rows:
            heat = pd.DataFrame(rows).T.reindex(columns=DOMAINS)
            fig = px.imshow(heat, text_auto=".0f", color_continuous_scale="RdYlGn", zmin=0, zmax=100, aspect="auto")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style(fig, 300), width="stretch")
        if hidden:
            st.caption(f"🔒 Груп із менш ніж {MIN_GROUP} відповідями приховано для захисту анонімності: {hidden}.")
        if not rows:
            st.caption(f"Немає груп із щонайменше {MIN_GROUP} відповідями.")

        st.markdown("##### Самооцінювання vs експертне оцінювання")
        sub_all = df_all[df_all["period"] == period]
        cmp_rows = []
        for m, g in sub_all.groupby("mode"):
            if len(g) >= MIN_GROUP:
                cmp_rows += [{"Тип": f"{m} (відповідей: {len(g)})", "Компонент": d, "Оцінка": v} for d, v in aggregate(g)[0].items()]
        if len({r["Тип"] for r in cmp_rows}) >= 2:
            fig = px.bar(pd.DataFrame(cmp_rows), x="Компонент", y="Оцінка", color="Тип", barmode="group", range_y=[0, 100])
            fig.update_layout(xaxis_title="", yaxis_title="", legend_title="")
            st.plotly_chart(style(fig, 330), width="stretch")
        else:
            st.caption(f"Потрібні обидва типи оцінювання (по {MIN_GROUP}+ відповідей) для порівняння.")

        st.markdown("##### Теми коментарів")
        cnt = {t: 0 for t in THEMES}
        for note in R["sub"]["note"]:
            low = str(note).lower()
            if "умовні демонстраційні" in low:
                continue
            for t, kws in THEMES.items():
                if any(k in low for k in kws):
                    cnt[t] += 1
        if sum(cnt.values()):
            fig = px.bar(pd.DataFrame({"Тема": list(cnt), "Коментарів": list(cnt.values())}), x="Тема", y="Коментарів")
            fig.update_layout(xaxis_title="")
            st.plotly_chart(style(fig, 280), width="stretch")
        else:
            st.caption("Коментарів за темами поки немає.")

    with t3:
        if not R["obj_s"]:
            st.info("Для цього періоду немає об'єктивних показників. Додайте їх у розділі «Об'єктивні показники».")
        else:
            cmp = pd.DataFrame([{"Компонент": d, "Опитування": R["survey"][d], "Об'єктивні дані": R["obj_s"][d],
                                 "Розбіжність": abs(R["survey"][d] - R["obj_s"][d])}
                                for d in R["survey"] if d in R["obj_s"]])
            fig = px.bar(cmp.melt(id_vars="Компонент", value_vars=["Опитування", "Об'єктивні дані"]),
                         x="Компонент", y="value", color="variable", barmode="group", range_y=[0, 100],
                         color_discrete_sequence=["#1d4ed8", "#10b981"])
            fig.update_layout(xaxis_title="", yaxis_title="", legend_title="")
            st.plotly_chart(style(fig, 340), width="stretch")
            st.dataframe(cmp.round(1), width="stretch", hide_index=True)
            for _, r in cmp.iterrows():
                if r["Розбіжність"] >= GAP_ALERT:
                    st.warning(f"{r['Компонент']}: розбіжність {r['Розбіжність']:.1f}. Перевірте документи та методику.")
            if R["src"]:
                st.caption(f"Джерело об'єктивних даних: {R['src']}")

    with t4:
        st.markdown(f"**Формула:** компонент = {W_SURVEY:.0%} × опитування + {W_OBJ:.0%} × об'єктивні дані; "
                    "Індекс доброчесності = середнє компонентів. Без об'єктивних даних використовується лише опитування.")
        calc = [{"Компонент": d, "Респондентів": R["n"], "Опитування": round(R["survey"].get(d, float("nan")), 1),
                 "Об'єктивні": round(R["obj_s"][d], 1) if d in R["obj_s"] else None,
                 "Підсумок": round(R["comb"].get(d, float("nan")), 1)} for d in DOMAINS]
        st.dataframe(pd.DataFrame(calc), width="stretch", hide_index=True)
        st.success(f"Індекс доброчесності = середнє підсумків = {R['idx']:.2f}")
        if R["obj_s"]:
            sens = []
            for w in range(0, 101, 10):
                vals = [(w / 100 * R["survey"][d] + (1 - w / 100) * R["obj_s"][d]) if d in R["obj_s"] else R["survey"][d]
                        for d in R["survey"]]
                sens.append({"Вага опитування, %": w, "Індекс": sum(vals) / len(vals)})
            st.markdown("##### Чутливість індексу до ваги опитування")
            fig = px.line(pd.DataFrame(sens), x="Вага опитування, %", y="Індекс", markers=True, range_y=[0, 100])
            st.plotly_chart(style(fig, 280), width="stretch")
        with st.expander("Оцінки за кожним питанням"):
            st.dataframe(question_stats(R["sub"]).round(1), width="stretch", hide_index=True)
    st.caption("Показники орієнтовні й не доводять наявність або відсутність корупції.")

# ---------- Анкета ----------
elif page == "📝 Пройти оцінювання":
    hero("Цифровий опитувальник", "Самооцінювання та експертне оцінювання. Повністю анонімно")
    with st.form("assessment_form"):
        c1, c2, c3 = st.columns(3)
        period = c1.text_input("Період оцінювання", value=date.today().strftime("%Y-%m"))
        mode = c2.selectbox("Тип оцінювання", MODES)
        unit = c3.selectbox("Група / підрозділ", UNITS)
        code = st.text_input("Код доступу (одноразовий)", type="password") if codes_enabled() else ""
        st.info("Відповіді не вибрані наперед. Питання без відповіді та «Не можу оцінити» не враховуються.")
        answers = {}
        for domain in DOMAINS:
            with st.container(border=True):
                st.subheader(domain)
                for idx, (d, q) in enumerate(QUESTIONS):
                    if d == domain:
                        answers[str(idx)] = st.radio(q, ANSWER_OPTIONS, index=None, key=f"q_{idx}", horizontal=True)
        note = st.text_area("Коментар без персональних даних (необов'язково)", max_chars=500)
        submitted = st.form_submit_button("Зберегти анонімне оцінювання", type="primary")
    if submitted:
        answers = {k: (v or SKIP) for k, v in answers.items()}
        ds, total, n = score_answers(answers)
        if n == 0:
            st.error("Потрібно надати хоча б одну оцінювану відповідь.")
        elif PII.search(note):
            st.error("У коментарі схоже на email чи телефон. Приберіть персональні дані й збережіть знову.")
        elif codes_enabled() and not use_code(code.strip()):
            st.error("Невірний або вже використаний код доступу.")
        else:
            with db() as conn:
                conn.execute("INSERT INTO assessments (created_at, period, mode, answers_json, note, unit) VALUES (?,?,?,?,?,?)",
                             (date.today().isoformat(),
                              period.strip() or date.today().strftime("%Y-%m"), mode,
                              json.dumps(answers, ensure_ascii=False), note.strip(), unit))
                conn.commit()
            st.success("Оцінювання збережено.")
            a, b = st.columns([1, 2])
            a.metric("Попередній індекс", f"{total:.1f}/100")
            a.caption(f"Враховано відповідей: {n} із {len(QUESTIONS)}")
            b.dataframe(pd.DataFrame([{"Компонент": k, "Оцінка": round(v, 1)} for k, v in ds.items()]),
                        width="stretch", hide_index=True)
            st.warning("Це результат одного респондента. Для висновків потрібна достатня кількість відповідей.")

# ---------- Об'єктивні показники ----------
elif page == "📎 Об'єктивні показники":
    hero("Об'єктивні показники", "Значення, підтверджені документами або статистикою (0–100 %)")
    df = load_assessments()
    existing = period_list(df) if not df.empty else []
    c1, c2 = st.columns(2)
    choice = c1.selectbox("Період", existing + ["Інший..."])
    period = c2.text_input("Назва періоду", value=date.today().strftime("%Y-%m")) if choice == "Інший..." else choice
    saved, saved_src = load_objective(period)
    valid_fields = [f for fs in OBJECTIVE_FIELDS.values() for f in fs]

    with st.expander("📥 Імпорт з CSV / Excel"):
        tpl = pd.DataFrame({"Показник": valid_fields, "Значення": [saved.get(f) for f in valid_fields]})
        st.download_button("Завантажити шаблон CSV", tpl.to_csv(index=False).encode("utf-8-sig"), "objective_template.csv", "text/csv")
        up = st.file_uploader("Файл із колонками «Показник» і «Значення»", type=["csv", "xlsx"])
        if up and st.button("Імпортувати файл"):
            try:
                imp = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
                data, n = dict(saved), 0
                for _, r in imp.iterrows():
                    k = str(r["Показник"]).strip()
                    if k in valid_fields:
                        data[k] = max(0.0, min(100.0, float(r["Значення"])))
                        n += 1
                with db() as conn:
                    conn.execute("INSERT OR REPLACE INTO objective_by_period VALUES (?,?,?,?)",
                                 (period.strip(), json.dumps(data, ensure_ascii=False), saved_src or up.name,
                                  datetime.now().isoformat(timespec="seconds")))
                    conn.commit()
                for f in valid_fields:
                    st.session_state.pop(f"obj_{period}_{f}", None)
                st.success(f"Імпортовано показників: {n}")
                st.rerun()
            except Exception as e:
                st.error(f"Не вдалося прочитати файл: {e}")

    with st.form(f"obj_form_{period}"):
        values = {}
        for domain, fields in OBJECTIVE_FIELDS.items():
            with st.container(border=True):
                st.subheader(domain)
                cols = st.columns(2)
                for i, f in enumerate(fields):
                    default = float(saved[f]) if saved.get(f) is not None else None
                    values[f] = cols[i % 2].number_input(f, 0.0, 100.0, default, 1.0, key=f"obj_{period}_{f}")
        source = st.text_input("Джерело підтвердження (документ, реєстр, звіт)", value=saved_src)
        ok = st.form_submit_button("Зберегти показники", type="primary")
    if ok:
        if not period.strip():
            st.error("Вкажіть період.")
        else:
            with db() as conn:
                conn.execute("INSERT OR REPLACE INTO objective_by_period VALUES (?,?,?,?)",
                             (period.strip(), json.dumps(values, ensure_ascii=False), source.strip(),
                              datetime.now().isoformat(timespec="seconds")))
                conn.commit()
            st.success("Показники збережено.")

# ---------- Рекомендації ----------
elif page == "✅ Рекомендації та заходи":
    hero("Рекомендації та моніторинг виконання", "Від проблемних компонентів до плану заходів")
    df = load_assessments()
    if df.empty:
        st.info("Спочатку потрібно провести оцінювання.")
        st.stop()
    period = pick_period(df, "rec_period")
    R = compute(df, period)
    qs = question_stats(R["sub"])
    weak = {d: v for d, v in R["comb"].items() if v < THRESHOLD}
    with db() as conn:
        actions = conn.execute("SELECT * FROM actions ORDER BY id DESC").fetchall()
    planned = {(a["domain"], a["problem"]) for a in actions if a["status"] != "Виконано"}

    if not weak:
        st.success(f"Усі компоненти мають оцінку {THRESHOLD}+. Перевірте результати експертно.")
    for domain, score in sorted(weak.items(), key=lambda x: x[1]):
        problem, rec0 = GUIDANCE[domain]
        prio, col = ("Високий", "#ef4444") if score < 50 else ("Середній", "#f59e0b")
        with st.container(border=True):
            st.markdown(f"**{domain}** · {score:.0f}/100 &nbsp; {pill('Пріоритет: ' + prio, col)}", unsafe_allow_html=True)
            st.write(f"**{problem}.**")
            rec = st.selectbox("Варіант заходу", [rec0] + EXTRA_MEASURES[domain], key=f"opt_{domain}")
            wq = qs[(qs["Компонент"] == domain) & (qs["Оцінка"] < THRESHOLD)]
            if not wq.empty:
                st.caption("Проблемні питання: " + " · ".join(wq["Питання"].tolist()))
            if (domain, problem) in planned:
                st.caption("✅ Захід уже в плані.")
            elif st.button("Додати захід до плану", key=f"add_{domain}"):
                with db() as conn:
                    conn.execute("INSERT INTO actions (created_at, domain, problem, recommendation, priority) VALUES (?,?,?,?,?)",
                                 (datetime.now().isoformat(timespec="seconds"), domain, problem, rec, prio))
                    conn.commit()
                st.rerun()

    st.divider()
    st.subheader("План заходів")
    if not actions:
        st.caption("Заходів поки немає.")
    else:
        eff = [effective_status(a["status"], a["due_date"]) for a in actions]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Усього", len(actions)); k2.metric("У процесі", eff.count("У процесі"))
        k3.metric("Виконано", eff.count("Виконано")); k4.metric("Прострочено", eff.count("Прострочено"))
        st.progress(eff.count("Виконано") / len(actions), text="Виконання плану")
        for a, es in zip(actions, eff):
            with st.container(border=True):
                badge = pill(es, {"Виконано": "#10b981", "Прострочено": "#ef4444", "У процесі": "#1d4ed8"}.get(es, "#64748b"))
                st.markdown(f"**{a['domain']}** — {a['problem']} &nbsp; {badge} &nbsp; {pill(a['priority'], '#7c3aed')}",
                            unsafe_allow_html=True)
                st.write(a["recommendation"])
                with db() as conn:
                    hist = conn.execute("SELECT at, status, comment FROM action_log WHERE action_id=? ORDER BY id DESC",
                                        (a["id"],)).fetchall()
                if hist:
                    with st.expander(f"Історія змін ({len(hist)})"):
                        for h in hist:
                            st.caption(f"{h['at']} · {h['status']}" + (f" · {h['comment']}" if h["comment"] else ""))
                cmt = st.text_input("Коментар до оновлення", key=f"cmt_{a['id']}")
                c1, c2, c3 = st.columns(3)
                resp = c1.text_input("Відповідальний (посада/підрозділ)", a["responsible"], key=f"resp_{a['id']}")
                try:
                    dv = date.fromisoformat(a["due_date"]) if a["due_date"] else None
                except ValueError:
                    dv = None
                due = c2.date_input("Строк", value=dv, key=f"due_{a['id']}")
                stt = c3.selectbox("Статус", STATUSES, index=STATUSES.index(a["status"]) if a["status"] in STATUSES else 0,
                                   key=f"status_{a['id']}")
                b1, b2, _ = st.columns([1, 1, 4])
                if b1.button("Зберегти", key=f"upd_{a['id']}"):
                    with db() as conn:
                        if stt != a["status"] or cmt.strip():
                            conn.execute("INSERT INTO action_log (action_id, at, status, comment) VALUES (?,?,?,?)",
                                         (a["id"], datetime.now().isoformat(timespec="seconds"), stt, cmt.strip()))
                        conn.execute("UPDATE actions SET responsible=?, due_date=?, status=? WHERE id=?",
                                     (resp, due.isoformat() if due else "", stt, a["id"]))
                        conn.commit()
                    st.rerun()
                if b2.button("Видалити", key=f"del_{a['id']}"):
                    with db() as conn:
                        conn.execute("DELETE FROM action_log WHERE action_id=?", (a["id"],))
                        conn.execute("DELETE FROM actions WHERE id=?", (a["id"],))
                        conn.commit()
                    st.rerun()

# ---------- Дані та експорт ----------
elif page == "📦 Дані та експорт":
    hero("Дані та експорт", "Таблиці CSV та управлінський звіт")
    df = load_assessments()
    if df.empty:
        st.info("Даних поки немає.")
        st.stop()
    view = [{"ID": r["id"], "Дата": r["created_at"], "Період": r["period"], "Тип": r["mode"], "Група": r["unit"],
             "Індекс доброчесності": round(score_answers(r["answers"])[1], 1),
             "Враховано відповідей": score_answers(r["answers"])[2]} for _, r in df.iterrows()]
    out = pd.DataFrame(view)
    st.dataframe(out, width="stretch", hide_index=True)
    ans = pd.DataFrame([{"ID оцінювання": r["id"], "Період": r["period"], "Компонент": d, "Питання": q,
                         "Відповідь": r["answers"].get(str(i), "")}
                        for _, r in df.iterrows() for i, (d, q) in enumerate(QUESTIONS)])
    with db() as conn:
        act = pd.DataFrame([dict(a) for a in conn.execute("SELECT * FROM actions").fetchall()])
    c1, c2, c3, c4 = st.columns(4)
    c1.download_button("Результати CSV", out.to_csv(index=False).encode("utf-8-sig"), "integrity_assessments.csv", "text/csv")
    c2.download_button("Відповіді CSV", ans.to_csv(index=False).encode("utf-8-sig"), "integrity_answers.csv", "text/csv")
    if not act.empty:
        c3.download_button("План заходів CSV", act.to_csv(index=False).encode("utf-8-sig"), "integrity_actions.csv", "text/csv")
    rp = st.selectbox("Період для звіту", period_list(df))
    md = build_report(df, rp)
    c4.download_button("Звіт (.md)", md.encode("utf-8"), f"integrity_report_{rp}.md", "text/markdown")
    d1, d2, _ = st.columns([1, 1, 2])
    dx = report_docx(md)
    if dx:
        d1.download_button("Звіт Word (.docx)", dx, f"integrity_report_{rp}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        d1.caption("Для Word: pip install python-docx")
    pdf_data = report_pdf(md)
    if pdf_data:
        d2.download_button("Завантажити звіт PDF", pdf_data, f"integrity_report_{rp}.pdf", "application/pdf")
    else:
        d2.download_button("Звіт HTML → PDF", report_html(md).encode("utf-8"), f"integrity_report_{rp}.html", "text/html")
        st.caption("Для прямого PDF встановіть reportlab. Альтернатива: відкрийте HTML і виберіть Друк → Зберегти як PDF.")
    st.caption("Експорт не містить імен респондентів. Коментарі перевіряються на email і телефони.")

# ---------- Цілі ----------
elif page == "🎯 Цілі та сценарії":
    hero("Цілі та порівняння з фактом", "Цільові рівні за компонентами і розрив «факт проти цілі»")
    tg = load_targets()
    with st.form("targets_form"):
        cols = st.columns(len(DOMAINS))
        new = {d: c.number_input(d, 0.0, 100.0, float(tg[d]), 5.0) for c, d in zip(cols, DOMAINS)}
        if st.form_submit_button("Зберегти цілі", type="primary"):
            save_targets(new)
            tg = new
            st.success("Цілі збережено.")
    df = load_assessments()
    if df.empty:
        st.info("Даних для порівняння поки немає.")
    else:
        R = compute(df, pick_period(df, "tg_period"))
        tdf = pd.DataFrame([{"Компонент": d, "Факт": R["comb"][d], "Ціль": tg[d], "Розрив": R["comb"][d] - tg[d]}
                            for d in R["comb"]])
        fig = px.bar(tdf.melt(id_vars="Компонент", value_vars=["Факт", "Ціль"]), x="Компонент", y="value",
                     color="variable", barmode="group", range_y=[0, 100],
                     color_discrete_sequence=["#1d4ed8", "#94a3b8"])
        fig.update_layout(xaxis_title="", yaxis_title="", legend_title="")
        st.plotly_chart(style(fig, 340), width="stretch")
        st.dataframe(tdf.round(1), width="stretch", hide_index=True)

# ---------- Коди доступу ----------
elif page == "🔑 Коди доступу":
    hero("Одноразові коди доступу", "Один код — одна анкета. Код не пов'язується з відповіддю")
    with db() as conn:
        tot, used = conn.execute("SELECT COUNT(*), COALESCE(SUM(used),0) FROM access_codes").fetchone()
    c1, c2 = st.columns(2)
    c1.metric("Видано кодів", tot)
    c2.metric("Використано", int(used))
    n = st.number_input("Скільки кодів створити", 1, 200, 10)
    if st.button("Згенерувати коди", type="primary"):
        codes = [secrets.token_hex(3).upper() for _ in range(int(n))]
        with db() as conn:
            conn.executemany("INSERT OR IGNORE INTO access_codes (hash, used) VALUES (?,0)", [(hash_code(c),) for c in codes])
            conn.commit()
        st.session_state["new_codes"] = "\n".join(codes)
    if st.session_state.get("new_codes"):
        st.text_area("Нові коди (показано один раз, роздайте респондентам)", st.session_state["new_codes"], height=180)
    st.caption("Коли створено хоча б один код, анкета вимагає код. У базі зберігаються лише хеші кодів.")

# ---------- Календар заходів ----------
elif page == "📅 Календар заходів":
    hero("Календар заходів", "Планування строків, контроль виконання та прострочених завдань")
    with db() as conn:
        acts = [dict(a) for a in conn.execute("SELECT * FROM actions ORDER BY CASE WHEN due_date='' THEN 1 ELSE 0 END, due_date, id DESC").fetchall()]
    if not acts:
        st.info("План заходів поки порожній. Додайте захід у розділі «Рекомендації та заходи».")
    else:
        month = st.date_input("Місяць календаря (оберіть будь-яку дату місяця)", value=date.today())
        month_rows = []
        for a in acts:
            try:
                due = date.fromisoformat(a["due_date"]) if a["due_date"] else None
            except ValueError:
                due = None
            if due and due.year == month.year and due.month == month.month:
                month_rows.append({"Дата": due.isoformat(), "Компонент": a["domain"], "Захід": a["recommendation"],
                                   "Відповідальний": a["responsible"] or "Не призначено",
                                   "Статус": effective_status(a["status"], a["due_date"]), "Пріоритет": a["priority"]})
        if month_rows:
            st.dataframe(pd.DataFrame(month_rows), width="stretch", hide_index=True)
        else:
            st.info("На обраний місяць заходів зі встановленими строками немає.")
        st.subheader("Усі найближчі заходи")
        upcoming = []
        for a in acts:
            if not a["due_date"]:
                continue
            upcoming.append({"Строк": a["due_date"], "Компонент": a["domain"], "Захід": a["recommendation"],
                             "Відповідальний": a["responsible"] or "—", "Статус": effective_status(a["status"], a["due_date"])})
        if upcoming:
            st.dataframe(pd.DataFrame(upcoming), width="stretch", hide_index=True)
            st.download_button("Експорт календаря CSV", pd.DataFrame(upcoming).to_csv(index=False).encode("utf-8-sig"),
                               "integrity_calendar.csv", "text/csv")

# ---------- Порівняння підрозділів ----------
elif page == "🏢 Порівняння підрозділів":
    hero("Порівняння підрозділів", "Порівняльний аналіз результатів із дотриманням мінімального порогу анонімності")
    df = load_assessments()
    if df.empty:
        st.info("Даних для порівняння поки немає.")
    else:
        period = pick_period(df, "unit_compare_period")
        d = df[df["period"] == period]
        rows = []
        hidden = 0
        for unit, group in d.groupby("unit"):
            if len(group) < MIN_GROUP:
                hidden += 1
                continue
            scores, idx, n = aggregate(group)
            rows.append({"Підрозділ": unit, "Індекс": idx, "Респондентів": n, **scores})
        if rows:
            cmp_df = pd.DataFrame(rows).sort_values("Індекс", ascending=False)
            st.metric("Підрозділів у порівнянні", len(cmp_df))
            fig = px.bar(cmp_df, x="Підрозділ", y="Індекс", color="Індекс", range_y=[0, 100],
                         color_continuous_scale="RdYlGn", text=cmp_df["Індекс"].round(1))
            fig.add_hline(y=THRESHOLD, line_dash="dash", annotation_text=f"Порогове значення {THRESHOLD}")
            st.plotly_chart(style(fig, 360), width="stretch")
            st.dataframe(cmp_df.round(1), width="stretch", hide_index=True)
            st.download_button("Експорт порівняння CSV", cmp_df.to_csv(index=False).encode("utf-8-sig"),
                               f"unit_comparison_{period}.csv", "text/csv")
        else:
            st.info(f"Немає підрозділів із щонайменше {MIN_GROUP} відповідями.")
        if hidden:
            st.caption(f"🔒 Приховано малочисельних груп: {hidden}. Поріг анонімності: {MIN_GROUP} відповіді.")

# ---------- Історія оцінювання ----------
elif page == "🕘 Історія оцінювання":
    hero("Історія оцінювання", "Хронологія проведених анкетувань та результати за кожним записом")
    df = load_assessments()
    if df.empty:
        st.info("Історія оцінювань порожня.")
    else:
        hist_rows = []
        for _, r in df.sort_values(["created_at", "id"], ascending=False).iterrows():
            _, idx, n = score_answers(r["answers"])
            hist_rows.append({"ID": int(r["id"]), "Дата": r["created_at"], "Період": r["period"],
                              "Тип": r["mode"], "Підрозділ": r["unit"], "Індекс": round(idx, 1),
                              "Враховано відповідей": n})
        hist = pd.DataFrame(hist_rows)
        cf1, cf2 = st.columns(2)
        periods = ["Усі"] + sorted(hist["Період"].dropna().unique().tolist(), reverse=True)
        selected_period = cf1.selectbox("Фільтр за періодом", periods)
        selected_mode = cf2.selectbox("Тип оцінювання", ["Усі"] + MODES)
        filtered = hist.copy()
        if selected_period != "Усі": filtered = filtered[filtered["Період"] == selected_period]
        if selected_mode != "Усі": filtered = filtered[filtered["Тип"] == selected_mode]
        st.dataframe(filtered, width="stretch", hide_index=True)
        st.download_button("Завантажити історію CSV", filtered.to_csv(index=False).encode("utf-8-sig"),
                           "assessment_history.csv", "text/csv")
        chosen = st.selectbox("Переглянути деталі оцінювання (ID)", filtered["ID"].tolist()) if not filtered.empty else None
        if chosen is not None:
            row = df[df["id"] == chosen].iloc[0]
            st.subheader(f"Оцінювання №{chosen}")
            st.write(f"Період: {row['period']} · Тип: {row['mode']} · Підрозділ: {row['unit']}")
            st.dataframe(pd.DataFrame([{"Компонент": d, "Оцінка": round(v, 1)}
                                       for d, v in score_answers(row["answers"])[0].items()]), width="stretch", hide_index=True)

# ---------- Резервне копіювання ----------
elif page == "💾 Резервне копіювання":
    hero("Резервне копіювання", "Створення переносної копії бази даних без зміни поточних записів")
    if DB_PATH.exists():
        st.metric("Розмір бази даних", f"{DB_PATH.stat().st_size / 1024:.1f} КБ")
        if st.button("Підготувати резервну копію", type="primary"):
            with tempfile.TemporaryDirectory() as td:
                snapshot = Path(td) / "integrity_dashboard.db"
                with sqlite3.connect(DB_PATH) as src, sqlite3.connect(snapshot) as dst:
                    src.backup(dst)
                manifest = {"created_at": datetime.now().isoformat(timespec="seconds"),
                            "database": "integrity_dashboard.db", "format": 1}
                archive = io.BytesIO()
                with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.write(snapshot, "integrity_dashboard.db")
                    zf.writestr("backup_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
                st.session_state["backup_bytes"] = archive.getvalue()
        if st.session_state.get("backup_bytes"):
            st.download_button("Завантажити ZIP-копію бази", st.session_state["backup_bytes"],
                               f"integrity_backup_{datetime.now():%Y%m%d_%H%M}.zip", "application/zip")
        st.warning("Зберігайте резервну копію в захищеному місці. Вона може містити службові коментарі та результати оцінювання.")
    else:
        st.error("Файл бази даних не знайдено.")

# ---------- Захист і ролі ----------
elif page == "🔐 Захист і ролі":
    hero("Захист і ролі", "Налаштування доступу та базові рекомендації з безпеки")
    st.subheader("Розмежування доступу")
    st.markdown("- **Респондент:** доступ лише до анкети.\n- **Адміністратор:** доступ до аналітики, управління заходами, експорту та резервного копіювання.")
    configured = bool(os.environ.get("INTEGRITY_ADMIN_PW", "").strip())
    st.metric("Пароль адміністратора", "Налаштовано" if configured else "Не налаштовано")
    st.code("INTEGRITY_ADMIN_PW=ваш_довгий_унікальний_пароль", language="text")
    st.caption("Задайте змінну середовища в конфігурації запуску PyCharm або в системі Windows і перезапустіть застосунок. Не зберігайте пароль у коді чи репозиторії.")
    st.subheader("Рекомендації")
    st.write("1. Не відкривайте застосунок у публічну мережу без HTTPS та окремого механізму автентифікації.\n2. Обмежте доступ до файлу integrity_dashboard.db.\n3. Створюйте резервну копію перед оновленням.\n4. Не вносьте до анонімних коментарів персональні або службові таємні дані.")
    st.info("Поточна роль адміністратора захищена паролем із змінної середовища. Для багатокористувацького розгортання потрібна серверна автентифікація та персональні облікові записи.")

# ---------- Методика ----------
elif page == "📘 Методика":
    hero("Методика оцінювання", "Прозорі правила розрахунку індексу доброчесності")
    st.warning("Навчальна пропозиція для прототипу. Її потрібно погодити з експертами перед використанням.")
    st.markdown(f"""
**Шкала:** Так — 100, Частково — 50, Ні — 0. «Не можу оцінити» та порожні відповіді не враховуються.

**Компонент (опитування):** середнє за питаннями компонента, далі середнє по респондентах періоду.

**Об'єктивні дані:** середнє введених відсотків компонента на рівні періоду, із зазначенням джерела.

**Підсумковий компонент:** {W_SURVEY:.0%} опитування + {W_OBJ:.0%} об'єктивні дані (вагу змінюйте в бічній панелі).

**Індекс доброчесності:** середнє підсумкових оцінок компонентів.

**Інтерпретація:** 85–100 високий; 70–84,9 достатній; 50–69,9 потребує покращення; 0–49,9 критична зона.

**Пороги:** зона уваги нижче {THRESHOLD}; розбіжність від {GAP_ALERT}; надійність від {MIN_RESPONDENTS} респондентів.

**Захист анонімності:** ПІБ, email, телефон та IP не збираються; коментарі з email/телефоном відхиляються;
розріз за групами показується лише за {MIN_GROUP}+ відповідями.

**Обмеження:** індекс не доводить наявність чи відсутність корупції.
""")
    st.divider()
    if st.button("Додати умовні демонстраційні дані"):
        seed_demo_data()
        st.success("Демо-дані додано (якщо база була порожньою).")
    st.checkbox("Підтверджую видалення всіх даних", key="confirm_clear")
    if st.button("Очистити всі дані", disabled=not st.session_state.get("confirm_clear")):
        with db() as conn:
            for t in ("assessments", "actions", "action_log", "objective_by_period"):
                conn.execute(f"DELETE FROM {t}")
            conn.commit()
        st.success("Дані видалено.")

st.sidebar.caption("Система управління доброчесністю · v4.0")