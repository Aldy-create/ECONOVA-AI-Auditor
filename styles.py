"""
styles.py — Bright Glass 3D Full-Color Solarpunk Design System & Faction CSS
Menyediakan palet faksi permanen, CSS global widget kaca, dan styling dinamis giliran aktif.
"""

from typing import Dict

import streamlit as st

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
@keyframes cloudDrift {
    0% { background-position: 0 0, 0 0; }
    100% { background-position: 1600px 0, -1400px 0; }
}

html, body, .stApp {
    background-color: var(--bg-sky-mid) !important;
    background-image: linear-gradient(180deg, #B8E1F7 0%, #DDF0F6 24%, #F4F1E1 62%, #F9F6E8 100%) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

.stApp::before {
    content: "";
    position: fixed;
    top: -120px;
    right: -80px;
    width: 420px;
    height: 420px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 236, 160, 0.95) 0%, rgba(255, 221, 120, 0.45) 35%, rgba(255, 221, 120, 0) 70%);
    pointer-events: none;
    z-index: 0;
    animation: sunGlow 6s ease-in-out infinite;
}

h1, h2, h3, h4, .stat-outfit {
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}
p, span, label, li, td, th {
    color: var(--text-primary);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.block-container {
    max-width: 1480px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 6rem !important;
}

/* Tactile Eco-Solarpunk Card Panels */
div[data-testid="stVerticalBlockBorderWrapper"] > div,
div[class*="st-key-panel_"],
.eco-card {
    background: var(--card-cream) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
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

/* Champion Card */
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

/* Poster Ribbon Headers ("WHAT IS ECONOVA?" / "MEET THE AI AUDITOR") */
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

/* Tab Bar Styling */
div[data-testid="stTabs"] div[role="tablist"] {
    gap: 12px !important;
    border-bottom: 2px solid rgba(5, 150, 105, 0.25) !important;
    padding: 8px 12px 14px 12px !important;
    background: rgba(255, 255, 255, 0.82) !important;
    backdrop-filter: blur(16px) !important;
    border-radius: 18px 18px 0 0 !important;
    border: 1px solid rgba(255, 255, 255, 0.95) !important;
    box-shadow: 0 6px 24px rgba(2, 132, 199, 0.08) !important;
    margin-bottom: 18px !important;
}
div[data-testid="stTabs"] [role="tab"],
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.88) !important;
    backdrop-filter: blur(10px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
    border-bottom: 3.5px solid #CFE3D6 !important;
    border-radius: 14px !important;
    padding: 10px 22px !important;
    color: #334155 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 12px rgba(15, 42, 29, 0.05) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stTabs"] [role="tab"]:hover,
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    border-color: #0284C7 !important;
    border-bottom: 3.5px solid #0284C7 !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F0FDF4 100%) !important;
    border-color: #059669 !important;
    border-bottom: 4px solid #059669 !important;
    box-shadow: 0 8px 24px rgba(5, 150, 105, 0.22) !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] * {
    color: #047857 !important;
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
.eco-pill-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 999px;
    background: linear-gradient(180deg, #1E6B47 0%, #144A31 100%);
    border: 1px solid #0E3B26;
    box-shadow: 0 3px 0 #0D3321;
    color: #FFFFFF;
    font-family: 'Fredoka', 'Outfit', sans-serif;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
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

/* Tactile Board-Game Buttons (Primary & Round Navigation) */
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
div[class*="st-key-btn_prev_round"] button {
    background: #FFFDF7 !important;
    color: #164E33 !important;
    border: 1.5px solid #B7D5C4 !important;
    border-bottom: 3.5px solid #0E3B26 !important;
    border-radius: 14px !important;
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}
div[class*="st-key-btn_prev_round"] button:hover {
    background: #F4FBF6 !important;
    border-color: #164E33 !important;
}

/* Custom Cream Input, Select, Multiselect, Labels & Expander Styling */
div[data-testid="stWidgetLabel"] p {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    color: #164E33 !important;
}
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background: #FFFDF7 !important;
    border: 1.5px solid #B7D5C4 !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 3px rgba(22, 78, 51, 0.05) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-baseweb="input"] div[data-baseweb="base-input"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus-within {
    border-color: #16A34A !important;
    box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.18) !important;
}
div[data-baseweb="base-input"] input {
    background: transparent !important;
    color: #164E33 !important;
    font-weight: 600 !important;
}
div[data-baseweb="select"] > div {
    background: #FFFDF7 !important;
    border: 1.5px solid #B7D5C4 !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 2px rgba(22, 78, 51, 0.04) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-baseweb="select"] > div:hover,
div[data-baseweb="select"] > div:focus-within {
    border-color: #0284C7 !important;
    box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.14) !important;
}
span[data-baseweb="tag"] {
    background: #DCFCE7 !important;
    color: #14532D !important;
    border: 1px solid #86EFAC !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 3px rgba(20, 83, 45, 0.08) !important;
}
span[data-baseweb="tag"] span,
span[data-baseweb="tag"] svg {
    color: #14532D !important;
    fill: #14532D !important;
}
div[data-testid="stExpander"] {
    border-radius: 14px !important;
    background: rgba(255, 253, 247, 0.92) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1.5px solid #B7D5C4 !important;
    box-shadow: 0 4px 10px rgba(22, 78, 51, 0.05) !important;
    overflow: hidden !important;
    margin-top: 8px !important;
}
div[data-testid="stExpander"] details summary {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: #164E33 !important;
    background: rgba(255, 253, 247, 0.95) !important;
    transition: background 0.2s ease !important;
}
div[data-testid="stExpander"] details summary:hover {
    background: #DCFCE7 !important;
}

/* Progress Bars */
.eco-prog-wrap { margin-bottom: 9px; }
.eco-prog-hdr {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.84rem;
    margin-bottom: 3px;
    font-weight: 600;
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

/* Chat Styling & Tab 3 Avatars / Status Dot */
@keyframes aiStatusPulse {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.65); }
    70% { box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
.ai-status-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #10B981;
    margin-right: 7px;
    vertical-align: middle;
    animation: aiStatusPulse 1.8s infinite;
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
    font-family: 'Outfit', sans-serif;
    letter-spacing: 0.03em;
}
.chat-avatar-ai {
    background: linear-gradient(135deg, #A7F3D0 0%, #34D399 55%, #0EA5E9 100%);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}
.chat-avatar-user {
    background: linear-gradient(135deg, #FDE68A 0%, #FBBF24 55%, #F59E0B 100%);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}
.ai-persona-box {
    background: rgba(255, 255, 255, 0.88) !important;
    backdrop-filter: blur(16px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
    border-radius: 18px !important;
    box-shadow: 0 6px 20px rgba(15, 42, 29, 0.05) !important;
    padding: 16px 18px !important;
    margin-bottom: 14px !important;
}
.ai-avatar-3d {
    width: 50px;
    height: 50px;
    border-radius: 16px;
    background: linear-gradient(180deg, #34D399 0%, #10B981 55%, #0EA5E9 100%);
    border: 2px solid #FFFFFF;
    box-shadow: 0 4px 12px rgba(15, 118, 110, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
}
.chat-row-user { display: flex; justify-content: flex-end; align-items: flex-start; gap: 10px; margin-bottom: 14px; }
.chat-row-ai { display: flex; justify-content: flex-start; align-items: flex-start; gap: 10px; margin-bottom: 14px; }
.chat-bubble-ai {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #D6E4DA;
    border-top: 3px solid #10B981;
    border-radius: 6px 18px 18px 18px;
    padding: 14px 18px;
    box-shadow: 0 6px 16px rgba(15, 42, 29, 0.07);
    max-width: 88%;
    font-size: 0.93rem;
    line-height: 1.6;
}
.chat-sender-tag {
    display: flex;
    align-items: center;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.chat-bubble-user {
    background: linear-gradient(180deg, #16A34A 0%, #15803D 100%);
    border-radius: 18px 6px 18px 18px;
    padding: 12px 18px;
    box-shadow: 0 6px 16px rgba(21, 128, 61, 0.2);
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
    """Menyuntikkan CSS global EcoNova Official Poster (Tactile Eco-Solarpunk Board Game HUD)."""
    render_html(GLOBAL_STYLES_CSS)


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
            f"linear-gradient(180deg, #FFFDF7 0%, #FFFDF7 72%, {f_th['tint']} 100%)"
            if is_turn
            else "#FFFDF7"
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
