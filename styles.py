"""
styles.py — EcoNova Official Poster Tactile Board Game HUD Design System
Menyediakan palet faksi permanen, CSS global kartu fisik taktil, navigasi tab stateful,
diploma sertifikat 2075, dan terminal AI Game Master.
"""

import base64
from pathlib import Path
from typing import Dict

import streamlit as st


@st.cache_data
def get_econova_bg_uri() -> str:
    """Memuat latar ilustrasi web EcoNova (WebP) sebagai Data URI base64 agar selalu tampil."""
    bg_path = Path(__file__).resolve().parent / "assets" / "econova_bg.webp"
    if not bg_path.is_file():
        return ""
    encoded = base64.b64encode(bg_path.read_bytes()).decode("ascii")
    return f"data:image/webp;base64,{encoded}"

FACTION_THEMES: Dict[int, Dict[str, str]] = {
    1: {
        "name": "Faksi Emerald",
        "short": "P1 · Emerald",
        "accent": "#059669",
        "dark": "#047857",
        "tint": "rgba(16, 185, 129, 0.10)",
        "border": "rgba(5, 150, 105, 0.55)",
        "glow": "0 0 0 3px rgba(16, 185, 129, 0.28), 0 12px 32px rgba(5, 150, 105, 0.22)",
        "badge_bg": "rgba(5, 150, 105, 0.14)",
    },
    2: {
        "name": "Faksi Sky Blue",
        "short": "P2 · Sky Blue",
        "accent": "#0284C7",
        "dark": "#0369A1",
        "tint": "rgba(2, 132, 199, 0.10)",
        "border": "rgba(2, 132, 199, 0.55)",
        "glow": "0 0 0 3px rgba(2, 132, 199, 0.28), 0 12px 32px rgba(2, 132, 199, 0.22)",
        "badge_bg": "rgba(2, 132, 199, 0.14)",
    },
    3: {
        "name": "Faksi Amber",
        "short": "P3 · Amber",
        "accent": "#D97706",
        "dark": "#B45309",
        "tint": "rgba(245, 158, 11, 0.10)",
        "border": "rgba(217, 119, 6, 0.55)",
        "glow": "0 0 0 3px rgba(245, 158, 11, 0.28), 0 12px 32px rgba(217, 119, 6, 0.22)",
        "badge_bg": "rgba(245, 158, 11, 0.16)",
    },
    4: {
        "name": "Faksi Violet",
        "short": "P4 · Violet",
        "accent": "#7C3AED",
        "dark": "#6D28D9",
        "tint": "rgba(124, 58, 237, 0.10)",
        "border": "rgba(124, 58, 237, 0.55)",
        "glow": "0 0 0 3px rgba(124, 58, 237, 0.28), 0 12px 32px rgba(124, 58, 237, 0.22)",
        "badge_bg": "rgba(124, 58, 237, 0.14)",
    },
}

GLOBAL_STYLES_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700;800;900&family=Outfit:wght@500;600;700;800;900&family=Plus+Jakarta+Sans:ital,wght@0,500;0,600;0,700;0,800;1,500&display=swap');

:root {
    --bg-sky-top: #B8E1F7;
    --bg-sky-mid: #DDF0F6;
    --bg-sky-bot: #F9F6E8;
    --text-primary: #164E33;
    --text-secondary: #3E5B4C;
    --card-cream: #FFFDF7;
    --glass-bg: rgba(255, 253, 247, 0.96);
    --glass-border: #C7DEC9;
    --shadow-3d: 0 6px 0 rgba(22, 78, 51, 0.14), 0 12px 24px rgba(0, 0, 0, 0.06);
}

@keyframes sunGlow {
    0%, 100% { opacity: 0.85; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}

html, body, .stApp {
    background-color: var(--bg-sky-mid) !important;
    background-image: linear-gradient(180deg, #B8E1F7 0%, #DDF0F6 24%, #F4F1E1 62%, #F9F6E8 100%) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
section.main {
    background: transparent !important;
    background-color: transparent !important;
}

[data-testid="stHeader"] {
    background: rgba(221, 240, 246, 0.45) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}

.stApp::before {
    content: "";
    position: fixed;
    top: -120px;
    right: -80px;
    width: 420px;
    height: 420px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 236, 160, 0.55) 0%, rgba(255, 221, 120, 0.25) 35%, rgba(255, 221, 120, 0) 70%);
    pointer-events: none;
    z-index: 0;
    animation: sunGlow 6s ease-in-out infinite;
}

h1, h2, h3, h4, .stat-outfit {
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-variant-numeric: tabular-nums;
}
p, span, label, li, td, th {
    color: var(--text-primary);
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.tabular-num {
    font-variant-numeric: tabular-nums;
}

.block-container {
    max-width: 1480px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 6rem !important;
}

/* Stateful Top Navigation Bar Shell */
div[class*="st-key-nav_bar_shell"] {
    background: #FFFDF7 !important;
    border: 2px solid #B7D5C4 !important;
    border-radius: 18px !important;
    padding: 8px 10px !important;
    box-shadow: 0 5px 0 rgba(22, 78, 51, 0.14), 0 10px 20px rgba(0, 0, 0, 0.05) !important;
    margin-bottom: 14px !important;
}
div[class*="st-key-nav_btn_"] button {
    border-radius: 13px !important;
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 10px 16px !important;
}

/* Tactile Eco-Solarpunk Card Panels */
div[data-testid="stVerticalBlockBorderWrapper"] > div,
div[class*="st-key-panel_"],
.eco-card {
    background: rgba(255, 253, 247, 0.94) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    border: 2px solid #CFE2D4 !important;
    border-radius: 20px !important;
    box-shadow: var(--shadow-3d) !important;
    padding: 18px 20px !important;
    margin-bottom: 14px !important;
    transition: all 0.22s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div:hover,
div[class*="st-key-panel_"]:hover,
.eco-card:hover {
    border-color: rgba(22, 163, 74, 0.45) !important;
    box-shadow: 0 7px 0 rgba(22, 78, 51, 0.16), 0 14px 28px rgba(0, 0, 0, 0.08) !important;
}

/* Champion Card & Official Diploma Frame */
.eco-card-champion {
    background: linear-gradient(135deg, #FFFDF7 0%, #FEF3C7 60%, #FFFBEB 100%) !important;
    border: 2.5px solid #EAB308 !important;
    border-radius: 22px !important;
    box-shadow: 0 6px 0 rgba(180, 83, 9, 0.22), 0 14px 32px rgba(234, 179, 8, 0.18) !important;
    padding: 24px 28px !important;
    margin-bottom: 18px !important;
}
.badge-champion {
    display: inline-flex;
    align-items: center;
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.35) !important;
    box-shadow: 0 4px 0 #0D3321 !important;
    color: #FFFFFF !important;
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.82rem !important;
    padding: 6px 18px !important;
    border-radius: 999px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
.cert-diploma {
    background: linear-gradient(135deg, #FFFDF7 0%, #F7F4E8 55%, #EFF9F3 100%);
    border: 3px solid #164E33;
    outline: 2px dashed #D97706;
    outline-offset: -8px;
    border-radius: 22px;
    padding: 28px 32px;
    box-shadow: 0 8px 0 rgba(22, 78, 51, 0.18), 0 16px 36px rgba(15, 42, 29, 0.09);
    margin-bottom: 18px;
}

/* 4-Pillar Stat Grid (Poster "Meet the AI Auditor" Style) */
.pillar-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 16px 0;
}
@media (max-width: 768px) {
    .pillar-grid-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.pillar-tile {
    border-radius: 16px;
    padding: 12px 14px;
    text-align: center;
    border: 2px solid;
    box-shadow: 0 4px 0 rgba(22, 78, 51, 0.10);
}
.pillar-tile-title {
    font-family: 'Outfit', sans-serif;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.pillar-tile-val {
    font-family: 'Fredoka', 'Outfit', sans-serif;
    font-size: 1.85rem;
    font-weight: 900;
    line-height: 1.1;
    margin: 3px 0;
    font-variant-numeric: tabular-nums;
}
.pillar-tile-tier {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 800;
    padding: 2px 9px;
    border-radius: 999px;
}

/* Diagnostic Narrative Cards (Tab 2) */
.diag-card {
    background: #FFFDF7;
    border: 1.5px solid #CFE2D4;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 5px 0 rgba(22, 78, 51, 0.10);
    margin-bottom: 14px;
    height: 100%;
}
.diag-card-hdr {
    display: flex;
    align-items: center;
    gap: 9px;
    font-family: 'Fredoka', 'Outfit', sans-serif;
    font-size: 1.06rem;
    font-weight: 800;
    margin-bottom: 8px;
}

/* Poster Ribbon Headers */
.eco-ribbon-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    margin: 4px 0 12px 0;
}
.eco-ribbon-header {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%) !important;
    color: #FFFFFF !important;
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 7px 22px !important;
    border-radius: 999px !important;
    border: 1.5px solid rgba(255, 255, 255, 0.28) !important;
    box-shadow: 0 4px 0 #0D3321, 0 8px 16px rgba(13, 51, 33, 0.16) !important;
}
.eco-ribbon-header * {
    color: #FFFFFF !important;
}
.eco-rating-badge {
    width: 54px;
    height: 54px;
    min-width: 54px;
    border-radius: 50%;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    border: 2.5px solid #FFFFFF;
    box-shadow: 0 4px 0 rgba(22, 78, 51, 0.22), 0 6px 14px rgba(0, 0, 0, 0.10);
}

/* Inner Sub-Tabs Styling (Certificate Player Tabs) */
div[data-testid="stTabs"] div[role="tablist"] {
    gap: 10px !important;
    padding: 8px 10px 10px 10px !important;
    background: #F4F1E1 !important;
    border-radius: 16px !important;
    border: 1.5px solid #B7D5C4 !important;
    margin-bottom: 14px !important;
}
div[data-testid="stTabs"] [role="tab"],
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    background: #FFFDF7 !important;
    border: 1.5px solid #B7D5C4 !important;
    border-bottom: 3px solid #94B8A4 !important;
    border-radius: 12px !important;
    padding: 8px 16px !important;
    color: #164E33 !important;
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%) !important;
    border-color: #144A31 !important;
    border-bottom: 3.5px solid #0D3321 !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] * {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

/* Hero Banner (EcoNova Poster Command Deck) */
.eco-hero-banner {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #FFFDF7 0%, #F4FBF6 60%, #E7F5FC 100%);
    border: 2.5px solid #B7D5C4;
    border-radius: 20px;
    padding: 14px 22px;
    margin-bottom: 12px;
    box-shadow: 0 6px 0 rgba(22, 78, 51, 0.14), 0 12px 24px rgba(0, 0, 0, 0.06);
}
.eco-hero-banner::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #16A34A 0%, #0284C7 36%, #EAB308 72%, #E11D48 100%);
}
.eco-hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.eco-hero-title {
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-size: 1.54rem !important;
    font-weight: 900 !important;
    color: #164E33 !important;
    margin: 0 !important;
    line-height: 1.15;
}
.eco-logo-plaque {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%);
    padding: 8px 16px;
    border-radius: 14px;
    border: 1.5px solid #0E3B26;
    box-shadow: 0 4px 0 #0D3321;
}
.eco-logo-img {
    height: 40px;
    width: auto;
    display: block;
    object-fit: contain;
}
.eco-hero-subtitle {
    font-family: 'Fredoka', 'Outfit', sans-serif;
    font-size: 1.16rem;
    font-weight: 800;
    color: #164E33;
    border-left: 2.5px solid #B7D5C4;
    padding-left: 14px;
    line-height: 1.2;
}
.eco-cert-kop-wrap {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}
.eco-cert-logo-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #164E33;
    padding: 5px 12px;
    border-radius: 10px;
}
.eco-cert-logo-img {
    height: 26px;
    width: auto;
    display: block;
    object-fit: contain;
}
.eco-legend-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    align-items: center;
}
.eco-legend-pill,
.eco-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
}
.pill-env, .eco-pill-env { background: rgba(22, 163, 74, 0.13); border: 1.5px solid rgba(22, 163, 74, 0.35); color: #16A34A !important; }
.pill-m, .eco-pill-m { background: rgba(2, 132, 199, 0.13); border: 1.5px solid rgba(2, 132, 199, 0.35); color: #0284C7 !important; }
.pill-e, .eco-pill-e { background: rgba(234, 179, 8, 0.16); border: 1.5px solid rgba(234, 179, 8, 0.45); color: #B45309 !important; }
.pill-qol, .eco-pill-qol { background: rgba(225, 29, 72, 0.13); border: 1.5px solid rgba(225, 29, 72, 0.35); color: #E11D48 !important; }
.eco-pill-env *, .pill-env * { color: #15803D !important; }
.eco-pill-m *, .pill-m * { color: #0284C7 !important; }
.eco-pill-e *, .pill-e * { color: #B45309 !important; }
.eco-pill-qol *, .pill-qol * { color: #E11D48 !important; }

/* Tactile Board-Game Buttons */
button[kind="primary"],
[data-testid="stBaseButton-primary"],
div[class*="st-key-btn_next_round"] button {
    background: linear-gradient(180deg, #1E6B47 0%, #164E33 100%) !important;
    color: #FFFFFF !important;
    border: 1.5px solid #144A31 !important;
    border-bottom: 3.5px solid #0E3B26 !important;
    border-radius: 14px !important;
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 10px rgba(22, 78, 51, 0.18) !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.18s ease !important;
}
button[kind="primary"] *,
[data-testid="stBaseButton-primary"] *,
div[class*="st-key-btn_next_round"] button * {
    color: #FFFFFF !important;
}
button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover,
div[class*="st-key-btn_next_round"] button:hover {
    background: linear-gradient(180deg, #237A51 0%, #19593B 100%) !important;
    transform: translateY(-1px) !important;
}
button[kind="primary"]:active,
[data-testid="stBaseButton-primary"]:active,
div[class*="st-key-btn_next_round"] button:active,
div[class*="st-key-btn_prev_round"] button:active {
    transform: translateY(2px) !important;
    border-bottom-width: 1.5px !important;
    box-shadow: 0 2px 6px rgba(22, 78, 51, 0.12) !important;
}
button[kind="secondary"],
[data-testid="stBaseButton-secondary"] {
    background: #FFFDF7 !important;
    color: #164E33 !important;
    border: 1.5px solid #B7D5C4 !important;
    border-bottom: 3px solid #94B8A4 !important;
    border-radius: 13px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
}
button[kind="secondary"]:hover:not(:disabled),
[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {
    background: #F0FDF4 !important;
    border-color: #16A34A !important;
}

/* Custom Clean Input, Select, Multiselect, Labels & Expander Drawer Styling */
div[data-testid="stWidgetLabel"] p {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    color: #164E33 !important;
}
div[data-testid="stTextInputRootElement"],
div[data-testid="stNumberInputContainer"],
div[data-baseweb="input"],
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #96BCA7 !important;
    border-radius: 10px !important;
    box-shadow: inset 0 1px 2px rgba(22, 78, 51, 0.04), 0 1px 2px rgba(22, 78, 51, 0.05) !important;
    transition: border-color 0.16s ease, box-shadow 0.16s ease !important;
}
div[data-testid="stTextInputRootElement"] div[data-baseweb="input"],
div[data-testid="stNumberInputContainer"] div[data-baseweb="input"],
div[data-baseweb="input"] div[data-baseweb="base-input"] {
    border: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
}
div[data-testid="stTextInputRootElement"]:focus-within,
div[data-testid="stNumberInputContainer"]:focus-within,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: #16A34A !important;
    box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.18) !important;
}
div[data-testid="stTextInputRootElement"] input,
div[data-testid="stNumberInputContainer"] input,
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
    background-color: transparent !important;
    color: #164E33 !important;
    -webkit-text-fill-color: #164E33 !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}
div[data-baseweb="select"] input,
div[data-baseweb="select"] span {
    color: #164E33 !important;
}
div[data-baseweb="select"] [class*="placeholder"],
div[data-baseweb="select"] input::placeholder {
    color: #6B8B7A !important;
    -webkit-text-fill-color: #6B8B7A !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
}
div[data-baseweb="select"] svg {
    color: #164E33 !important;
    fill: #164E33 !important;
}
div[data-baseweb="popover"],
ul[data-baseweb="menu"] {
    background-color: #FFFDF7 !important;
    border: 1.5px solid #8BB39E !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 24px rgba(22, 78, 51, 0.14) !important;
}
ul[data-baseweb="menu"] li[role="option"] {
    color: #164E33 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
}
ul[data-baseweb="menu"] li[role="option"]:hover,
ul[data-baseweb="menu"] li[aria-selected="true"] {
    background-color: #DCFCE7 !important;
    color: #14532D !important;
}

/* Sub-Kartu Terstruktur di Dalam Drawer Kelola Kartu & Kas */
.eco-drawer-hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 6px;
}
.eco-drawer-title {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'Outfit', sans-serif;
    font-size: 0.77rem;
    font-weight: 800;
    color: #164E33;
    letter-spacing: 0.01em;
}
.eco-drawer-sub {
    font-size: 0.68rem;
    font-weight: 600;
    color: #5C7A69;
}
.eco-drawer-chip {
    display: inline-flex;
    align-items: center;
    font-family: 'Outfit', sans-serif;
    font-size: 0.68rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 999px;
    border: 1px solid;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}
.eco-field-cap {
    font-family: 'Outfit', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #2E523F;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 4px;
}

div[class*="st-key-wrap_identity_sec"] {
    background: #FFFFFF !important;
    border: 1.5px solid #CFE2D4 !important;
    border-top: 3px solid #1E6B47 !important;
    border-radius: 13px !important;
    padding: 10px 11px 11px 11px !important;
    box-shadow: 0 2px 5px rgba(22, 78, 51, 0.05) !important;
}
div[class*="st-key-wrap_proj_sec"] {
    background: #F3FBF6 !important;
    border: 1.5px solid #A7DFBE !important;
    border-left: 4px solid #16A34A !important;
    border-radius: 13px !important;
    padding: 9px 11px 10px 11px !important;
}
div[class*="st-key-wrap_tech_sec"] {
    background: #F2F9FF !important;
    border: 1.5px solid #93C5FD !important;
    border-left: 4px solid #0284C7 !important;
    border-radius: 13px !important;
    padding: 9px 11px 10px 11px !important;
}
div[class*="st-key-wrap_skill_sec"] {
    background: #FFFBEB !important;
    border: 1.5px solid #FCD34D !important;
    border-left: 4px solid #D97706 !important;
    border-radius: 13px !important;
    padding: 9px 11px 10px 11px !important;
}
div[class*="st-key-wrap_prob_sec"] {
    background: #FFF5F6 !important;
    border: 1.5px solid #FDA4AF !important;
    border-left: 4px solid #E11D48 !important;
    border-radius: 13px !important;
    padding: 9px 11px 10px 11px !important;
}
div[class*="st-key-wrap_coin_sec"] {
    background: linear-gradient(135deg, #FFFDF5 0%, #FEF3C7 100%) !important;
    border: 1.5px solid #F59E0B !important;
    border-left: 4px solid #B45309 !important;
    border-radius: 13px !important;
    padding: 9px 11px 10px 11px !important;
    box-shadow: 0 2px 6px rgba(180, 83, 9, 0.08) !important;
}
div[class*="st-key-wrap_coin_sec"] div[data-testid="stNumberInputContainer"] {
    border-color: #D97706 !important;
    background-color: #FFFFFF !important;
}
div[class*="st-key-wrap_coin_sec"] div[data-testid="stNumberInputContainer"] input {
    text-align: center !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    color: #92400E !important;
    -webkit-text-fill-color: #92400E !important;
}

/* Multiselect Tags per Kategori (Pastel Pill Kontras Tinggi) */
span[data-baseweb="tag"],
[data-baseweb="tag"] {
    background-color: #DCFCE7 !important;
    border: 1.5px solid #22C55E !important;
    color: #14532D !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
div[class*="st-key-wrap_proj_sec"] span[data-baseweb="tag"],
div[class*="st-key-wrap_proj_sec"] [data-baseweb="tag"] {
    background-color: #DCFCE7 !important;
    border: 1.5px solid #22C55E !important;
    color: #14532D !important;
}
div[class*="st-key-wrap_tech_sec"] span[data-baseweb="tag"],
div[class*="st-key-wrap_tech_sec"] [data-baseweb="tag"] {
    background-color: #E0F2FE !important;
    border: 1.5px solid #0284C7 !important;
    color: #075985 !important;
}
div[class*="st-key-wrap_skill_sec"] span[data-baseweb="tag"],
div[class*="st-key-wrap_skill_sec"] [data-baseweb="tag"] {
    background-color: #FEF3C7 !important;
    border: 1.5px solid #F59E0B !important;
    color: #92400E !important;
}
div[class*="st-key-wrap_prob_sec"] span[data-baseweb="tag"],
div[class*="st-key-wrap_prob_sec"] [data-baseweb="tag"] {
    background-color: #FFE4E6 !important;
    border: 1.5px solid #F43F5E !important;
    color: #9F1239 !important;
}
span[data-baseweb="tag"] span,
span[data-baseweb="tag"] svg,
[data-baseweb="tag"] span,
[data-baseweb="tag"] svg {
    color: inherit !important;
    fill: currentColor !important;
}

/* Stepper Buttons (- dan +) Simetris pada st.number_input */
div[data-testid="stNumberInput"] button {
    background: #164E33 !important;
    background-color: #164E33 !important;
    color: #FFFFFF !important;
    border: 1px solid #0E3B26 !important;
    border-radius: 8px !important;
    margin: 2px !important;
    min-height: 28px !important;
    padding: 0 9px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}
div[data-testid="stNumberInput"] button svg,
div[data-testid="stNumberInput"] button path {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}
div[data-testid="stNumberInput"] button:hover:not(:disabled) {
    background: #1E6B47 !important;
    background-color: #1E6B47 !important;
}

/* Expander Kelola Kartu & Kas: Soft Cream Command Drawer */
div[data-testid="stExpander"] {
    border-radius: 16px !important;
    background-color: #F7F4EA !important;
    border: 1.5px solid #B7D5C4 !important;
    box-shadow: 0 4px 0 rgba(22, 78, 51, 0.08) !important;
    overflow: hidden !important;
    margin-top: 8px !important;
}
div[data-testid="stExpander"] > details {
    background-color: #F7F4EA !important;
}
div[data-testid="stExpanderDetails"] {
    background-color: #F7F4EA !important;
    padding: 10px 11px 12px 11px !important;
}
div[data-testid="stExpander"] details summary {
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: #164E33 !important;
    background: linear-gradient(180deg, #F3EFE0 0%, #EAE4CE 100%) !important;
    border-bottom: 1px solid #D5E2D8 !important;
    padding: 9px 14px !important;
}
div[data-testid="stExpander"] details summary:hover {
    background: linear-gradient(180deg, #DCFCE7 0%, #CBEFD8 100%) !important;
}
div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
    gap: 0.55rem !important;
}

/* Progress Bars */
.eco-prog-wrap { margin-bottom: 9px; }
.eco-prog-hdr {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
    font-size: 0.84rem;
    margin-bottom: 3px;
    font-weight: 600;
    white-space: nowrap !important;
}
.eco-prog-track {
    width: 100%;
    height: 12px;
    background: #EAF1EC;
    border: 1px solid #D6E4DA;
    border-radius: 999px;
    overflow: hidden;
    box-shadow: inset 0 2px 3px rgba(15, 42, 29, 0.08);
}
.eco-prog-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.4s ease;
}

/* Tab 3: EcoNova Rulebook & AI Advisor Terminal (Forest Green + Warm Cream) */
@keyframes aiStatusPulse {
    0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.65); }
    70% { box-shadow: 0 0 0 7px rgba(22, 163, 74, 0); }
    100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
}
.ai-status-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #16A34A;
    margin-right: 7px;
    vertical-align: middle;
    animation: aiStatusPulse 1.8s infinite;
}
.ai-persona-box {
    background: linear-gradient(135deg, #F4F1E1 0%, #ECFDF5 100%) !important;
    border: 2px solid #164E33 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 0 rgba(22, 78, 51, 0.16) !important;
    padding: 15px 17px !important;
    margin-bottom: 14px !important;
}
.ai-avatar-3d {
    width: 50px;
    height: 50px;
    min-width: 50px;
    border-radius: 16px;
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%);
    border: 2px solid #FBBF24;
    box-shadow: 0 4px 0 #0D3321;
    display: flex;
    align-items: center;
    justify-content: center;
}
.rule-tile {
    background: #F9F6E8;
    border: 1.5px solid #B7D5C4;
    border-left: 4px solid #164E33;
    border-radius: 12px;
    padding: 8px 11px;
    margin-bottom: 7px;
    font-size: 0.78rem;
    line-height: 1.38;
}
.chat-avatar-badge {
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #FFFFFF;
    font-family: 'Fredoka', 'Outfit', sans-serif;
    letter-spacing: 0.03em;
}
.chat-avatar-ai {
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%);
    color: #FFFFFF !important;
    box-shadow: 0 3px 0 #0D3321;
}
.chat-avatar-user {
    background: linear-gradient(180deg, #F59E0B 0%, #B45309 100%);
    color: #FFFFFF !important;
    box-shadow: 0 3px 0 #78350F;
}
.chat-row-user { display: flex; justify-content: flex-end; align-items: flex-start; gap: 10px; margin-bottom: 14px; }
.chat-row-ai { display: flex; justify-content: flex-start; align-items: flex-start; gap: 10px; margin-bottom: 14px; }
.chat-bubble-ai {
    background: #FFFDF7;
    border: 1.5px solid #B7D5C4;
    border-top: 3.5px solid #164E33;
    border-radius: 6px 18px 18px 18px;
    padding: 14px 18px;
    box-shadow: 0 4px 0 rgba(22, 78, 51, 0.10);
    max-width: 88%;
    font-size: 0.93rem;
    line-height: 1.62;
}
.chat-bubble-ai code {
    background: #DCFCE7;
    color: #14532D;
    border: 1px solid #86EFAC;
    border-radius: 6px;
    padding: 1px 6px;
    font-size: 0.84rem;
    font-weight: 700;
}
.chat-sender-tag {
    display: flex;
    align-items: center;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 5px;
}
.chat-bubble-user {
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%);
    border-radius: 18px 6px 18px 18px;
    padding: 12px 18px;
    box-shadow: 0 4px 0 #0D3321;
    max-width: 82%;
    color: #FFFFFF;
    font-size: 0.94rem;
    font-weight: 600;
}
.chat-bubble-user *:not(.chat-sender-tag):not(.chat-sender-tag *) { color: #FFFFFF !important; }
.chat-bubble-user .chat-sender-tag,
.chat-bubble-user .chat-sender-tag * { color: #DCFCE7 !important; }
</style>
"""


def render_html(html_str: str) -> None:
    """Merender HTML multi-baris secara aman tanpa terpotong parser Markdown code-block."""
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_global_styles() -> None:
    """Menyuntikkan CSS global EcoNova Official Poster serta latar ilustrasi web Solarpunk."""
    render_html(GLOBAL_STYLES_CSS)
    bg_uri = get_econova_bg_uri()
    if bg_uri:
        render_html(
            f"""
            <style>
            html, body, .stApp {{
                background-color: #DDF0F6 !important;
                background-image:
                    linear-gradient(180deg, rgba(240, 248, 252, 0.16) 0%, rgba(249, 246, 232, 0.28) 56%, rgba(235, 246, 238, 0.22) 100%),
                    url("{bg_uri}") !important;
                background-size: cover !important;
                background-position: center bottom !important;
                background-repeat: no-repeat !important;
                background-attachment: fixed !important;
            }}
            </style>
            """
        )


def inject_faction_turn_styles(active_player_id: int) -> None:
    """Menyuntikkan CSS dinamis per faksi permanen bergaya kartu fisik EcoNova & segmented turn switcher."""
    faction_css_blocks = [
        """
        div[class*="st-key-turn_switcher_shell"] {
            background: #FFFDF7 !important;
            border: 1.5px solid #B7D5C4 !important;
            border-radius: 16px !important;
            padding: 6px 8px !important;
            box-shadow: 0 4px 0 rgba(22, 78, 51, 0.10), inset 0 1px 3px rgba(22, 78, 51, 0.04) !important;
            margin-top: 8px !important;
        }
        """
    ]
    for f_pid, f_th in FACTION_THEMES.items():
        is_turn = (f_pid == active_player_id)
        b_width = "2.5px"
        b_color = f_th["accent"] if is_turn else f_th["border"]
        shadow_rule = (
            f"0 6px 0 rgba(22, 78, 51, 0.16), {f_th['glow']}"
            if is_turn
            else "0 6px 0 rgba(22, 78, 51, 0.14), 0 12px 24px rgba(0, 0, 0, 0.06)"
        )
        bg_rule = (
            f"linear-gradient(180deg, rgba(255, 253, 247, 0.94) 0%, rgba(255, 253, 247, 0.94) 72%, {f_th['tint']} 100%)"
            if is_turn
            else "rgba(255, 253, 247, 0.94)"
        )
        turn_btn_css = (
            f"""
            div[class*="st-key-btn_turn_p{f_pid}"] button {{
                background: linear-gradient(180deg, {f_th['accent']} 0%, {f_th['dark']} 100%) !important;
                color: #FFFFFF !important;
                border: 1.5px solid {f_th['dark']} !important;
                border-bottom: 3.5px solid #0E3B26 !important;
                border-radius: 999px !important;
                font-family: 'Fredoka', 'Outfit', sans-serif !important;
                font-weight: 800 !important;
                box-shadow: 0 4px 12px {f_th['border']} !important;
            }}
            div[class*="st-key-btn_turn_p{f_pid}"] button * {{
                color: #FFFFFF !important;
            }}
            """
            if is_turn
            else f"""
            div[class*="st-key-btn_turn_p{f_pid}"] button {{
                background: #FFFDF7 !important;
                color: {f_th['dark']} !important;
                border: 1.5px solid {f_th['border']} !important;
                border-bottom: 3px solid {f_th['border']} !important;
                border-radius: 999px !important;
                font-family: 'Fredoka', 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                transition: all 0.18s ease !important;
            }}
            div[class*="st-key-btn_turn_p{f_pid}"] button:hover {{
                background: {f_th['tint']} !important;
                border-color: {f_th['accent']} !important;
                transform: translateY(-1px) !important;
            }}
            div[class*="st-key-btn_turn_p{f_pid}"] button * {{
                color: {f_th['dark']} !important;
            }}
            """
        )
        faction_css_blocks.append(
            f"""
            div[class*="st-key-panel_tracker_p{f_pid}"] {{
                border: {b_width} solid {b_color} !important;
                background: {bg_rule} !important;
                box-shadow: {shadow_rule} !important;
            }}
            div[class*="st-key-panel_tracker_p{f_pid}"]:hover {{
                border-color: {f_th['accent']} !important;
                box-shadow: 0 7px 0 rgba(22, 78, 51, 0.16), {f_th['glow']} !important;
            }}
            {turn_btn_css}
            """
        )
    render_html("<style>\n" + "\n".join(faction_css_blocks) + "\n</style>")