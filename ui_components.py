"""
ui_components.py — Komponen UI Modular EcoNova Official Poster HUD
Berisi Stateful Navigation Bar, Hero Banner, Tab 1 Live Tracker,
Tab 2 Final Audit & Sertifikat Diploma 2075, dan Tab 3 AI Game Master.
"""

import base64
import html
import importlib
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

import streamlit as st

for _dep_name, _dep_attrs in (
    ("cards_data", ("PROBLEM_SOLUTION_RULES", "get_resolvable_problems_for_tech", "get_resolvable_problems_for_skill")),
    ("styles", ("FACTION_THEMES", "inject_faction_turn_styles", "render_html")),
    ("state_manager", ("TAB_OPTIONS", "callback_switch_tab", "callback_lock_and_open_audit")),
):
    _dep_mod = importlib.import_module(_dep_name)
    if any(not hasattr(_dep_mod, _a) for _a in _dep_attrs):
        importlib.reload(_dep_mod)

from cards_data import (
    EVENT_BY_ID,
    EVENT_BY_ROUND,
    EVENT_CARDS,
    PERMANENT_TECH_BY_CODE,
    PROBLEM_BY_ID,
    PROJECT_BY_ID,
    SKILL_BY_CODE,
    calculate_coin_bonus,
    compute_player_score,
    get_card_clean_name,
    get_card_color_theme,
    get_resolvable_problems_for_skill,
    get_resolvable_problems_for_tech,
    rank_players_audit,
)
from llm_service import (
    generate_llm_enhanced_narrative,
    get_groq_api_key,
    query_llm_game_master,
)
from state_manager import (
    TAB_OPTIONS,
    WELCOME_CHAT_MESSAGE,
    callback_activate_tech,
    callback_apply_quick_card,
    callback_event_picker_changed,
    callback_lock_and_open_audit,
    callback_next_round,
    callback_prev_round,
    callback_reset_game,
    callback_reset_manual_points,
    callback_set_active_player,
    callback_switch_tab,
    callback_sync_city,
    callback_sync_coins,
    callback_sync_manual_points,
    callback_sync_name,
    callback_sync_problems,
    callback_sync_projects,
    callback_sync_skills,
    callback_sync_techs,
    callback_undo_last_action,
    callback_use_s1,
    callback_use_s1_fallback,
    callback_use_s2,
    callback_use_s3,
    callback_use_s4,
    callback_use_s5,
    callback_use_skill_solve_problem,
)
from styles import FACTION_THEMES, inject_faction_turn_styles, render_html

try:
    import plotly.graph_objects as go
except ImportError:
    go = None


project_id_options = list(PROJECT_BY_ID.keys())
tech_code_options = list(PERMANENT_TECH_BY_CODE.keys())
skill_code_options = list(SKILL_BY_CODE.keys())
problem_id_options = list(PROBLEM_BY_ID.keys())

MARKET_DISCOUNT_BADGES: Dict[str, str] = {
    "EV03": "DISKON PASAR: -2 Koin Project Card di Energy District",
    "EV05": "DISKON PASAR: -2 Koin Tech Card di City Center",
}


def format_project_label(pid: str) -> str:
    return get_card_clean_name(pid)


def format_tech_label(code: str) -> str:
    return get_card_clean_name(code)


def format_skill_label(code: str) -> str:
    return get_card_clean_name(code)


def format_problem_label(pid: str) -> str:
    return get_card_clean_name(pid)


def format_event_selector(eid: Optional[str]) -> str:
    if not eid:
        return "-- Pilih Event Card --"
    return get_card_clean_name(eid)


def get_overall_rating_grade(avg_score: float) -> Dict[str, str]:
    """Mengembalikan grade rating (A+ hingga D) dan skema warna badge bergaya poster EcoNova."""
    if avg_score >= 85:
        return {"grade": "A+", "label": "Exemplary", "bg": "linear-gradient(180deg, #16A34A 0%, #15803D 100%)", "fg": "#FFFFFF", "ring": "#86EFAC"}
    if avg_score >= 78:
        return {"grade": "A", "label": "Sustainable", "bg": "linear-gradient(180deg, #22C55E 0%, #16A34A 100%)", "fg": "#FFFFFF", "ring": "#BBF7D0"}
    if avg_score >= 70:
        return {"grade": "A-", "label": "Progressive", "bg": "linear-gradient(180deg, #0284C7 0%, #0369A1 100%)", "fg": "#FFFFFF", "ring": "#BAE6FD"}
    if avg_score >= 62:
        return {"grade": "B+", "label": "Developing", "bg": "linear-gradient(180deg, #0EA5E9 0%, #0284C7 100%)", "fg": "#FFFFFF", "ring": "#BAE6FD"}
    if avg_score >= 55:
        return {"grade": "B", "label": "Balanced", "bg": "linear-gradient(180deg, #EAB308 0%, #CA8A04 100%)", "fg": "#FFFFFF", "ring": "#FEF08A"}
    if avg_score >= 45:
        return {"grade": "C", "label": "Transitional", "bg": "linear-gradient(180deg, #F59E0B 0%, #D97706 100%)", "fg": "#FFFFFF", "ring": "#FDE68A"}
    return {"grade": "D", "label": "At Risk", "bg": "linear-gradient(180deg, #E11D48 0%, #BE123C 100%)", "fg": "#FFFFFF", "ring": "#FECDD3"}


PILLAR_BADGE_FILES: Dict[str, str] = {
    "M": "badge_pillar_m.png",
    "E": "badge_pillar_e.png",
    "ENV": "badge_pillar_env.png",
    "QoL": "badge_pillar_qol.png",
}

ARCHETYPE_BADGE_FILES: Dict[str, str] = {
    "Balanced Sustainable Metropolis": "badge_arch_balanced.png",
    "Green Eco City": "badge_arch_green.png",
    "Smart Energy City": "badge_arch_energy.png",
    "Connected Mobility City": "badge_arch_mobility.png",
    "People-First City": "badge_arch_people.png",
    "Uneven / At-Risk City": "badge_arch_risk.png",
    "Emerging Smart City": "badge_arch_emerging.png",
}


def build_aspect_progress_html(label: str, icon: str, val: int, delta: int, color: str) -> str:
    pct = max(0, min(100, int(val)))
    delta_str = f"{delta:+d}"
    text_color = {
        "#0284C7": "#0369A1",
        "#EAB308": "#B45309",
        "#16A34A": "#15803D",
        "#E11D48": "#BE123C",
        "#06B6D4": "#0369A1",
        "#F59E0B": "#B45309",
        "#10B981": "#15803D",
        "#F43F5E": "#BE123C",
    }.get(color.upper(), color)

    if delta > 0:
        delta_col = "#047857"
        delta_bg = "rgba(16, 185, 129, 0.18)"
        delta_border = "rgba(16, 185, 129, 0.45)"
    elif delta < 0:
        delta_col = "#BE123C"
        delta_bg = "rgba(244, 63, 94, 0.18)"
        delta_border = "rgba(244, 63, 94, 0.45)"
    else:
        delta_col = "#4A5D52"
        delta_bg = "rgba(148, 163, 184, 0.15)"
        delta_border = "rgba(148, 163, 184, 0.3)"

    pillar_uri = get_asset_uri(PILLAR_BADGE_FILES.get(icon, ""))
    if pillar_uri:
        icon_badge_html = f'<img src="{pillar_uri}" alt="{icon}" style="width:20px;height:20px;object-fit:contain;vertical-align:middle;flex-shrink:0;" />'
    else:
        icon_badge_html = f'<span style="background:{color}22;color:{text_color};font-size:0.75rem;padding:2px 7px;border-radius:6px;font-weight:800;border:1px solid {color}44;">{icon}</span>'

    raw_html = f"""
    <div class="eco-prog-wrap">
      <div class="eco-prog-hdr">
        <span style="display:flex;align-items:center;gap:6px;font-family:'Outfit',sans-serif;color:#0F2A1D;">
          {icon_badge_html} <b>{label}</b>
        </span>
        <span class="tabular-num" style="font-family:'Outfit',sans-serif;">
          <b style="color:{text_color};font-size:1.05rem;">{val}</b><span style="color:#4A5D52;font-size:0.86rem;">/100</span>
          <span style="color:{delta_col};font-size:0.8rem;font-weight:800;margin-left:6px;background:{delta_bg};border:1px solid {delta_border};padding:2px 7px;border-radius:999px;">
            {delta_str}
          </span>
        </span>
      </div>
      <div class="eco-prog-track">
        <div class="eco-prog-fill" style="width:{pct}%;background-color:{color};box-shadow:0 0 10px {color}88;"></div>
      </div>
    </div>
    """
    return "\n".join(line.strip() for line in raw_html.splitlines() if line.strip())


def format_chat_markdown_to_html(md_text: str) -> str:
    """Mengonversi Markdown jawaban AI menjadi HTML terstruktur (heading, bullet, numbered list, code badge)."""
    escaped = html.escape(md_text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b style='color:#0F2A1D;font-weight:800;'>\1</b>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(
        r"(?m)^####\s+(.+)$",
        r"<div style='font-family:\"Fredoka\",\"Outfit\",sans-serif;font-size:0.98rem;font-weight:800;color:#164E33;margin:10px 0 4px 0;'>\1</div>",
        escaped,
    )
    escaped = re.sub(
        r"(?m)^###\s+(.+)$",
        r"<div style='font-family:\"Fredoka\",\"Outfit\",sans-serif;font-size:1.06rem;font-weight:800;color:#164E33;margin:12px 0 6px 0;border-left:4px solid #16A34A;padding-left:10px;'>\1</div>",
        escaped,
    )
    escaped = re.sub(
        r"(?m)^(\d+)\.\s+(.+)$",
        r"<div style='margin:4px 0 4px 6px;color:#1E3A2B;display:flex;align-items:flex-start;gap:7px;'><span style='background:#164E33;color:#FFFFFF;font-size:0.7rem;font-weight:800;padding:1px 6px;border-radius:999px;margin-top:2px;'>\1</span><span>\2</span></div>",
        escaped,
    )
    escaped = re.sub(
        r"(?m)^[-•]\s+(.+)$",
        r"<div style='margin:4px 0 4px 8px;color:#1E3A2B;display:flex;align-items:flex-start;gap:7px;'><span style='color:#16A34A;font-weight:900;'>•</span><span>\1</span></div>",
        escaped,
    )
    escaped = escaped.replace("\n", "<br>")
    return escaped


@st.cache_data(show_spinner=False)
def get_asset_uri(filename: str) -> str:
    """Membaca file aset dari folder assets/ dan mengembalikan data URI base64 (atau '' jika tidak ada)."""
    if not filename:
        return ""
    asset_path = Path(__file__).resolve().parent / "assets" / filename
    if not asset_path.is_file():
        return ""
    ext = asset_path.suffix.lower().lstrip(".")
    mime = "image/png" if ext == "png" else ("image/webp" if ext == "webp" else f"image/{ext}")
    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


@st.cache_data(show_spinner=False)
def get_econova_logo_uri() -> str:
    """Membaca assets/econova_logo.png dan mengembalikan data URI base64 (atau '' jika tidak ada)."""
    return get_asset_uri("econova_logo.png")


def icon_img_html(filename: str, size: int = 18, alt: str = "", mr: int = 4) -> str:
    """Merender tag <img> ikon PNG transparan proporsional dengan fallback string kosong."""
    uri = get_asset_uri(filename)
    if not uri:
        return ""
    margin_css = f"margin-right:{mr}px;" if mr > 0 else ""
    return (
        f'<img src="{uri}" alt="{html.escape(alt)}" '
        f'style="width:{size}px;height:{size}px;object-fit:contain;vertical-align:middle;flex-shrink:0;{margin_css}" />'
    )


def render_hero_banner() -> None:
    """Merender Top HUD Bar pengunci atas serta Hero Banner EcoNova Board-Mat."""
    logo_uri = get_econova_logo_uri()
    curr_round = int(st.session_state.get("current_round", 1))
    act_pid = int(st.session_state.get("active_player_id", 1))
    act_pl = st.session_state.get("players", {}).get(act_pid, {"city": f"Kota {act_pid}"})
    ev_id = st.session_state.get("selected_event_id")
    ev_text = EVENT_BY_ID[ev_id]["name"] if ev_id and ev_id in EVENT_BY_ID else "Event Standby"
    action_count = len(st.session_state.get("action_history", []))

    hud_logo_html = (
        f'<img src="{logo_uri}" alt="EcoNova" style="height:28px;width:auto;display:block;" />'
        if logo_uri
        else '<span style="font-family:\'Fredoka\',sans-serif;font-weight:900;font-size:1.1rem;color:#FFFDF7;">EcoNova</span>'
    )
    render_html(
        f"""
        <div class="eco-top-hud">
          <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            {hud_logo_html}
            <span style="font-family:'Outfit',sans-serif;font-size:0.74rem;font-weight:800;letter-spacing:0.06em;color:#FEF08A;text-transform:uppercase;">
              Board Game Tabletop Companion
            </span>
          </div>
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span class="eco-hud-round-pill">RONDE {curr_round} / 13</span>
            <span class="eco-hud-status-pill">Giliran: P{act_pid} · {html.escape(str(act_pl.get('city', f'Kota {act_pid}')))}</span>
            <span class="eco-hud-status-pill">Event: {html.escape(ev_text)}</span>
            <span class="eco-hud-status-pill">{action_count} Log Aksi</span>
          </div>
        </div>
        """
    )

    if logo_uri:
        left_brand_html = f"""
        <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
          <div class="eco-logo-plaque" style="background:linear-gradient(180deg,#1E6B47 0%,#144A31 100%);padding:8px 16px;border-radius:14px;border:2px solid #0D3321;box-shadow:0 3px 0 #0D3321;">
            <img src="{logo_uri}" alt="EcoNova Logo" style="height:36px;width:auto;display:block;" />
          </div>
          <div class="eco-hero-subtitle">
            Sustainable City Planner &amp; <span style="color:#0284C7;">AI Auditor</span>
          </div>
        </div>
        """
    else:
        left_brand_html = """
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <h1 class="eco-hero-title">
            EcoNova <span style="color:#16A34A;">Sustainable City</span> <span style="color:#0284C7;">Planner</span>
          </h1>
          <div class="eco-hero-subtitle">
            Sustainable City Planner &amp; <span style="color:#0284C7;">AI Auditor</span>
          </div>
        </div>
        """

    render_html(
        f"""
        <div class="eco-hero-banner">
          <div class="eco-hero-top">
            {left_brand_html}
            <div class="eco-legend-row">
              <span class="eco-legend-pill pill-env">{icon_img_html('badge_pillar_env.png', 16, 'ENV', 2)}<b>ENV</b> Environment</span>
              <span class="eco-legend-pill pill-m">{icon_img_html('badge_pillar_m.png', 16, 'M', 2)}<b>M</b> Mobility</span>
              <span class="eco-legend-pill pill-e">{icon_img_html('badge_pillar_e.png', 16, 'E', 2)}<b>E</b> Energy</span>
              <span class="eco-legend-pill pill-qol">{icon_img_html('badge_pillar_qol.png', 16, 'QoL', 2)}<b>QoL</b> Quality of Life</span>
            </div>
          </div>
        </div>
        """
    )


def render_footer_bar() -> None:
    """Merender footer tipis pengunci bagian bawah alas papan permainan."""
    curr_round = int(st.session_state.get("current_round", 1))
    active_tab = st.session_state.get("active_tab", "Tab 1: Live Tracker")
    render_html(
        f"""
        <div class="eco-footer-bar">
          <span>EcoNova: Sustainable City Planner &amp; AI Auditor · Rulebook v1.0</span>
          <span style="color:#FEF08A;">{html.escape(active_tab)} · Ronde {curr_round} / 13</span>
        </div>
        """
    )


def render_navigation_bar() -> str:
    """Merender 3 tombol navigasi utama yang stateful sehingga dapat berpindah otomatis via callback."""
    active_tab = st.session_state.get("active_tab", "Tab 1: Live Tracker")
    if active_tab not in TAB_OPTIONS:
        active_tab = "Tab 1: Live Tracker"
        st.session_state.active_tab = active_tab

    tab_labels = [
        ("Tab 1: Live Tracker", "Tab 1: Live Tracker"),
        ("Tab 2: Final Audit", "Tab 2: Final Audit"),
        ("Tab 3: AI Game Master", "Tab 3: EcoBot Game Master"),
    ]

    with st.container(key="nav_bar_shell"):
        cols = st.columns(3, gap="small")
        for idx, (tab_key, display_label) in enumerate(tab_labels):
            is_selected = (active_tab == tab_key)
            with cols[idx]:
                st.button(
                    display_label,
                    key=f"nav_btn_{idx}",
                    type="primary" if is_selected else "secondary",
                    width="stretch",
                    on_click=callback_switch_tab,
                    args=(tab_key,),
                )
    return active_tab


# ==============================================================================
# TAB 1: LIVE GAME DASHBOARD TRACKER (1 LAYAR BERSAMA 4 PEMAIN)
# ==============================================================================
def render_tab_tracker() -> None:
    """Merender Tab 1: Live Tabletop Dashboard & Round Tracker untuk 4 Pemain."""
    active_player_id = int(st.session_state.get("active_player_id", 1))
    if active_player_id not in FACTION_THEMES:
        active_player_id = 1
        st.session_state.active_player_id = 1

    inject_faction_turn_styles(active_player_id)

    curr_round_top = int(st.session_state.get("current_round", 1))
    top_ev_id = st.session_state.get("selected_event_id")
    if top_ev_id and top_ev_id in EVENT_BY_ID:
        top_ev = EVENT_BY_ID[top_ev_id]
        ev_banner_txt = f"{top_ev['name']} ({top_ev.get('effect_summary', top_ev.get('effect_str', ''))})"
    else:
        ev_banner_txt = "Belum ada Event aktif — skor pemain murni"
    total_active_probs = sum(len(st.session_state.players[pid]["problems"]) for pid in range(1, 5))
    prob_banner_txt = f"{total_active_probs} Krisis Aktif di Meja" if total_active_probs > 0 else "0 Krisis Aktif"

    render_html(
        f"""
        <div class="eco-round-banner">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <span class="eco-hud-round-pill">RONDE {curr_round_top} / 13</span>
            <span style="display:inline-flex;align-items:center;gap:5px;font-size:0.84rem;font-weight:700;">
              {icon_img_html('icon_card_event.png', 18, 'Event', 0)}<span>Event: <b>{html.escape(ev_banner_txt)}</b></span>
            </span>
          </div>
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span class="eco-hud-status-pill" style="display:inline-flex;align-items:center;gap:5px;">
              {icon_img_html('icon_card_problem.png', 15, 'Krisis', 0)}<span>{prob_banner_txt}</span>
            </span>
          </div>
        </div>
        """
    )

    render_html(
        """
        <div class="eco-ribbon-wrap">
          <span class="eco-ribbon-header">TELEMETRI RONDE &amp; KENDALI MEJA</span>
          <span style="font-size:0.78rem;font-weight:700;color:#164E33;background:#FFFDF7;border:2px solid #164E33;border-radius:999px;padding:4px 12px;">
            Live Tabletop Scoreboard · 4 Faksi Kota
          </span>
        </div>
        """
    )
    with st.container(border=True, key="panel_tracker_topbar"):
        r_col1, r_col2, r_col3 = st.columns([3.8, 5.2, 3.0], gap="medium")
        with r_col1:
            curr_round = int(st.session_state.current_round)
            seg_cells = []
            for r_step in range(1, 14):
                if r_step < curr_round:
                    seg_style = "background:linear-gradient(135deg,#10B981,#059669);box-shadow:0 0 6px rgba(16,185,129,0.4);"
                elif r_step == curr_round:
                    seg_style = "background:linear-gradient(135deg,#0284C7,#06B6D4);box-shadow:0 0 8px rgba(6,182,212,0.7);transform:scaleY(1.22);"
                else:
                    seg_style = "background:rgba(148,163,184,0.28);"
                seg_cells.append(
                    f"<div title='Ronde {r_step}' style='flex:1;height:7px;border-radius:999px;{seg_style}transition:all 0.25s ease;'></div>"
                )
            round_track_html = "".join(seg_cells)

            render_html(
                f"""
                <div style="background:linear-gradient(180deg,rgba(255,255,255,0.96) 0%,rgba(236,253,245,0.75) 100%);border:1.5px solid rgba(5,150,105,0.38);border-radius:16px;padding:10px 14px;box-shadow:0 4px 16px rgba(5,150,105,0.08);text-align:center;">
                  <div style="font-family:'Outfit',sans-serif;font-size:0.72rem;font-weight:800;color:#047857;letter-spacing:0.06em;text-transform:uppercase;">
                    Telemetri Ronde Permainan
                  </div>
                  <div class="stat-outfit" style="font-size:1.85rem;font-weight:900;color:#0F2A1D;line-height:1.12;margin-top:2px;">
                    RONDE <span style="color:#059669;">{curr_round:02d}</span> <span style="font-size:1.1rem;color:#64748B;">/ 13</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:3px;margin:8px 0 6px 0;padding:3px 4px;background:rgba(255,255,255,0.85);border:1px solid #D6E4DA;border-radius:999px;">
                    {round_track_html}
                  </div>
                  <div style="font-size:0.72rem;color:#4A5D52;font-weight:700;display:flex;align-items:center;justify-content:center;gap:4px;">
                    {f"{icon_img_html('icon_trophy.png', 16, 'Final', 2)}Ronde Terakhir (Evaluasi Akhir)" if curr_round == 13 else f"Fase Pembangunan Kota · Progres {int((curr_round / 13) * 100)}%"}
                  </div>
                </div>
                """
            )

            nav_c1, nav_c2 = st.columns(2, gap="small")
            with nav_c1:
                st.button(
                    "← Prev",
                    key="btn_prev_round",
                    disabled=(curr_round <= 1),
                    width="stretch",
                    on_click=callback_prev_round,
                    help="Kembali ke ronde sebelumnya dan rollback koin serta efek event ronde terakhir.",
                )
            with nav_c2:
                st.button(
                    "Next Ronde →",
                    key="btn_next_round",
                    disabled=(curr_round >= 13),
                    type="primary",
                    width="stretch",
                    on_click=callback_next_round,
                    help="Lanjut ronde: komit efek & koin Event Card ke kas pemain, buang ke Discard, dan reset tombol Tech.",
                )

        with r_col2:
            used_events = st.session_state.get("used_events", [])
            available_events = [e["id"] for e in EVENT_CARDS if e["id"] not in used_events]
            event_picker_options: List[Optional[str]] = [None] + available_events

            current_sel = st.session_state.get("selected_event_id")
            if current_sel not in event_picker_options:
                current_sel = None
                st.session_state.selected_event_id = None
            if st.session_state.get("widget_event_picker") not in event_picker_options:
                st.session_state.widget_event_picker = current_sel

            st.selectbox(
                "Event Card Terbuka di Papan Fisik:",
                options=event_picker_options,
                format_func=format_event_selector,
                key="widget_event_picker",
                on_change=callback_event_picker_changed,
                help="Pilih Event Card yang sedang terbuka di papan fisik ronde ini. Kartu ronde lalu otomatis masuk Discard.",
            )

            active_event_id = st.session_state.selected_event_id
            if active_event_id and active_event_id in EVENT_BY_ID:
                active_event = EVENT_BY_ID[active_event_id]
                discount_badge = MARKET_DISCOUNT_BADGES.get(active_event_id, "")
                discount_html = (
                    f"<div style='margin-top:7px;padding:5px 10px;border-radius:10px;background:linear-gradient(135deg,rgba(245,158,11,0.18),rgba(251,191,36,0.12));border:1.5px solid rgba(217,119,6,0.5);color:#92400E;font-size:0.74rem;font-weight:800;display:flex;align-items:center;gap:6px;'>{icon_img_html('icon_coin.png', 16, 'Diskon', 0)}<span>{discount_badge}</span></div>"
                    if discount_badge
                    else ""
                )
                render_html(
                    f"""
                    <div style="background:linear-gradient(135deg,rgba(255,255,255,0.97) 0%,rgba(224,242,254,0.68) 100%);border:1.5px solid rgba(2,132,199,0.55);border-left:5px solid #0284C7;border-radius:14px;padding:11px 14px;box-shadow:0 6px 18px rgba(2,132,199,0.12);margin-top:4px;">
                      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                        <span class="eco-pill eco-pill-m" style="font-size:0.74rem;">
                          {icon_img_html('icon_card_event.png', 18, 'Event', 2)}{active_event['name']}
                        </span>
                        <span style="font-size:0.75rem;font-weight:800;color:#047857;background:rgba(16,185,129,0.14);border:1px solid rgba(16,185,129,0.35);padding:3px 9px;border-radius:999px;">
                          Efek Live: {active_event.get('effect_summary', active_event.get('effect_str', ''))}
                        </span>
                      </div>
                      <div style="font-size:0.76rem;color:#1E3A2B;line-height:1.4;margin-top:7px;font-weight:500;">
                        {active_event['description']}
                      </div>
                      {discount_html}
                    </div>
                    """
                )
            else:
                render_html(
                    f"""
                    <div style="background:#F4F1E1;border:1.5px dashed #94B8A4;border-radius:14px;padding:12px 14px;margin-top:4px;display:flex;align-items:center;gap:10px;">
                      <span style="display:inline-flex;align-items:center;gap:5px;background:#FFFDF7;color:#164E33;border:1px solid #B7D5C4;border-radius:10px;padding:5px 9px;font-size:0.72rem;font-weight:800;letter-spacing:0.04em;flex-shrink:0;">
                        {icon_img_html('icon_card_event.png', 18, 'Event Standby', 0)} STANDBY
                      </span>
                      <span style="color:#476656;font-size:0.77rem;line-height:1.35;font-weight:600;">
                        Belum ada Event Card dibuka di papan fisik ronde ini. Skor pemain tetap murni sampai kartu dipilih.
                      </span>
                    </div>
                    """
                )

        with r_col3:
            st.caption("Manajemen Discard & Permainan:")
            render_html(
                f"""
                <div style="background:rgba(255,255,255,0.88);border:1px solid #BAE6FD;border-radius:10px;padding:7px 10px;font-size:0.75rem;color:#0369A1;margin-bottom:6px;">
                  <b>Discard Deck:</b> {len(used_events)} Kartu Terpakai<br/>
                  <b>Event Tersedia:</b> {len(available_events)} Kartu di Deck
                </div>
                """
            )
            st.toggle(
                "Enable Nilai Poin Manual",
                key="enable_manual_points",
                help="Aktifkan tombol/input penambahan nilai poin manual untuk setiap pemain di dashboard.",
            )
            st.button(
                "Reset Permainan (Baseline 50)",
                width="stretch",
                key="btn_reset_empty_top",
                on_click=callback_reset_game,
                help="Reset semua nilai pemain ke awal (Skor 50, 5 Koin, tanpa kartu).",
            )

        act_faction = FACTION_THEMES[active_player_id]
        act_pl = st.session_state.players[active_player_id]
        with st.container(key="turn_switcher_shell"):
            turn_lbl_col, t_btn1, t_btn2, t_btn3, t_btn4 = st.columns([3.2, 2.2, 2.2, 2.2, 2.2], gap="small")
            with turn_lbl_col:
                render_html(
                    f"""
                    <div style="display:flex;align-items:center;gap:8px;padding:6px 12px;background:rgba(255,255,255,0.92);border:1.5px solid {act_faction['border']};border-radius:999px;box-shadow:0 2px 8px rgba(15,42,29,0.04);">
                      {icon_img_html(f'badge_faction_p{active_player_id}.png', 20, f'P{active_player_id}', 0)}
                      <div style="font-size:0.76rem;font-weight:800;color:{act_faction['dark']};line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        Giliran: P{active_player_id} · {html.escape(act_pl['city'])}
                      </div>
                    </div>
                    """
                )
            for t_pid, t_col in zip([1, 2, 3, 4], [t_btn1, t_btn2, t_btn3, t_btn4]):
                t_th = FACTION_THEMES[t_pid]
                t_pl = st.session_state.players[t_pid]
                is_curr = (t_pid == active_player_id)
                with t_col:
                    st.button(
                        f"{'▶ ' if is_curr else ''}P{t_pid} · {t_pl['city'][:11]}",
                        key=f"btn_turn_p{t_pid}",
                        type="primary" if is_curr else "secondary",
                        width="stretch",
                        on_click=callback_set_active_player,
                        args=(t_pid,),
                        help=f"Set giliran aktif ke Pemain {t_pid} ({t_th['name']}) & buka panel kelola kartu.",
                    )

    if st.session_state.get("enable_manual_points", False):
        render_html(
            f"""
            <div style="background:linear-gradient(90deg, rgba(2,132,199,0.12), rgba(5,150,105,0.12));border:1.5px solid rgba(2,132,199,0.35);border-radius:12px;padding:8px 14px;margin:8px 0 12px 0;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 10px rgba(2,132,199,0.06);">
              <span style="display:flex;align-items:center;gap:8px;font-size:0.82rem;font-weight:700;color:#0F2A1D;">
                {icon_img_html('icon_tools.png', 20, 'Manual', 0)}
                <span><b>Mode Penyesuaian Poin Manual Aktif:</b> Masukkan penambahan atau pengurangan poin (M, E, ENV, QoL) pada masing-masing kartu pemain di bawah.</span>
              </span>
              <span style="font-size:0.75rem;padding:3px 10px;border-radius:8px;background:rgba(2,132,199,0.2);color:#0284C7;font-weight:800;letter-spacing:0.02em;">
                MANUAL POINTS ON
              </span>
            </div>
            """
        )

    with st.container(border=True, key="panel_unified_card_deck"):
        deck_col1, deck_col2 = st.columns([5.6, 4.4], gap="large")
        with deck_col1:
            act_pl_deck = st.session_state.players[active_player_id]
            act_fac_deck = FACTION_THEMES[active_player_id]
            render_html(
                f"""
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:8px;padding-bottom:6px;border-bottom:2px solid #164E33;">
                  <span style="display:inline-flex;align-items:center;gap:6px;font-family:'Fredoka','Outfit',sans-serif;font-size:0.96rem;font-weight:800;color:#164E33;">
                    {icon_img_html('icon_card_project.png', 20, 'Kartu', 0)}<span>Meja Aksi Kartu Cepat</span>
                  </span>
                  <span style="display:inline-flex;align-items:center;gap:5px;background:{act_fac_deck['badge_bg']};color:{act_fac_deck['dark']};border:1.5px solid {act_fac_deck['border']};border-radius:999px;padding:2px 10px;font-size:0.74rem;font-weight:800;">
                    {icon_img_html(f'badge_faction_p{active_player_id}.png', 16, f'P{active_player_id}', 0)}Target: P{active_player_id} · {html.escape(act_pl_deck['city'])}
                  </span>
                </div>
                """
            )
            qc_c1, qc_c2 = st.columns([3.5, 6.5], gap="small")
            with qc_c1:
                q_cat = st.selectbox(
                    "Kategori Kartu:",
                    options=["Project", "Tech", "Skill", "Problem"],
                    key="quick_card_category",
                )
            cat_meta_map = {
                "Project": (project_id_options, PROJECT_BY_ID, format_project_label, "icon_card_project.png", act_pl_deck["projects"], "Terapkan Proyek ke Pemain"),
                "Tech": (tech_code_options, PERMANENT_TECH_BY_CODE, format_tech_label, "icon_card_tech.png", act_pl_deck["techs"], "Pasang Permanent Tech"),
                "Skill": (skill_code_options, SKILL_BY_CODE, format_skill_label, "icon_card_skill.png", act_pl_deck["skills"], "Tambah Skill ke Tangan"),
                "Problem": (problem_id_options, PROBLEM_BY_ID, format_problem_label, "icon_card_problem.png", act_pl_deck["problems"], "Catat Krisis ke Pemain"),
            }
            cat_opts, cat_dict, cat_fmt, cat_icon, owned_list, exec_btn_label = cat_meta_map[q_cat]
            if st.session_state.get("quick_card_picker") not in cat_opts:
                st.session_state["quick_card_picker"] = cat_opts[0]
            with qc_c2:
                q_cid = st.selectbox(
                    "Pilih Kartu:",
                    options=cat_opts,
                    format_func=cat_fmt,
                    key="quick_card_picker",
                )

            preview_card = cat_dict.get(q_cid, {})
            already_owned = q_cid in owned_list
            eff_sum = preview_card.get("effect_summary", preview_card.get("effect_str", "-"))
            cost_val = int(preview_card.get("cost", 0))
            dist_val = preview_card.get("district", q_cat)
            owned_badge = (
                '<span style="background:#FEF3C7;color:#92400E;border:1px solid #F59E0B;border-radius:999px;padding:1px 8px;font-size:0.68rem;font-weight:800;">Sudah Dimiliki</span>'
                if already_owned
                else ""
            )
            render_html(
                f"""
                <div class="eco-card-preview">
                  <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                    <span style="display:inline-flex;align-items:center;gap:6px;font-family:'Fredoka','Outfit',sans-serif;font-size:0.88rem;font-weight:800;color:#164E33;">
                      {icon_img_html(cat_icon, 18, q_cat, 0)}<span>[{html.escape(str(q_cid))}] {html.escape(str(preview_card.get('name', q_cid)))}</span>
                    </span>
                    <span style="display:inline-flex;align-items:center;gap:5px;">
                      {owned_badge}
                      <span style="background:#DCFCE7;color:#14532D;border:1px solid #16A34A;border-radius:999px;padding:2px 8px;font-size:0.71rem;font-weight:800;">
                        {html.escape(str(eff_sum))}
                      </span>
                    </span>
                  </div>
                  <div style="font-size:0.75rem;color:#3E5B4C;margin-top:4px;line-height:1.38;">
                    <b>{html.escape(str(dist_val))}</b> · Biaya Papan: <b>{cost_val} Koin</b> — {html.escape(str(preview_card.get('description', '')))}
                  </div>
                </div>
                """
            )
            st.button(
                f"{exec_btn_label} (P{active_player_id})" if not already_owned else f"Kartu {q_cid} Sudah Dimiliki P{active_player_id}",
                type="primary",
                width="stretch",
                key="btn_apply_quick_card",
                disabled=already_owned,
                on_click=callback_apply_quick_card,
                args=(active_player_id, q_cat, q_cid),
            )

        with deck_col2:
            curr_r_log = int(st.session_state.get("current_round", 1))
            all_hist = st.session_state.get("action_history", [])
            round_hist = [h for h in all_hist if int(h.get("round", 0)) == curr_r_log]
            display_hist = round_hist[-5:] if round_hist else all_hist[-4:]
            hist_header_note = f"{len(round_hist)} aksi di Ronde {curr_r_log}" if round_hist else (f"Menampilkan {len(display_hist)} aksi terakhir" if display_hist else "Belum ada aksi")

            render_html(
                f"""
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:8px;padding-bottom:6px;border-bottom:2px solid #164E33;">
                  <span style="display:inline-flex;align-items:center;gap:6px;font-family:'Fredoka','Outfit',sans-serif;font-size:0.96rem;font-weight:800;color:#164E33;">
                    {icon_img_html('icon_clipboard.png', 20, 'Log', 0)}<span>Log Kartu Ronde Ini</span>
                  </span>
                  <span style="background:#FFFDF7;color:#164E33;border:1.5px solid #164E33;border-radius:999px;padding:2px 9px;font-size:0.71rem;font-weight:800;">
                    {hist_header_note}
                  </span>
                </div>
                """
            )

            if display_hist:
                log_rows_html = []
                for h_item in reversed(display_hist):
                    h_cat = h_item.get("category", "")
                    h_icon_map = {
                        "Project": "icon_card_project.png",
                        "Tech": "icon_card_tech.png",
                        "Skill": "icon_card_skill.png",
                        "Problem": "icon_card_problem.png",
                        "Event": "icon_card_event.png",
                        "Ronde": "icon_trophy.png",
                    }
                    h_icon = h_icon_map.get(h_cat, "icon_clipboard.png")
                    log_rows_html.append(
                        f"""
                        <div class="eco-log-item">
                          <span style="display:inline-flex;align-items:center;gap:6px;min-width:0;">
                            {icon_img_html(h_icon, 16, h_cat, 0)}
                            <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                              <b>R{h_item['round']}</b> · {html.escape(str(h_item['player_name']))}: <b>{html.escape(str(h_item['card_name']))}</b>
                            </span>
                          </span>
                          <span style="flex-shrink:0;font-size:0.7rem;font-weight:800;color:#15803D;background:#DCFCE7;border:1px solid #16A34A;border-radius:999px;padding:1px 7px;">
                            {html.escape(str(h_item.get('delta_summary', '')))}
                          </span>
                        </div>
                        """
                    )
                render_html("".join(log_rows_html))
            else:
                render_html(
                    f"""
                    <div style="background:#FFFDF7;border:1.5px dashed #164E33;border-radius:12px;padding:14px 12px;text-align:center;font-size:0.78rem;color:#3E5B4C;font-weight:600;margin-bottom:8px;">
                      {icon_img_html('icon_clipboard.png', 20, 'Kosong', 4)}Belum ada aksi kartu tercatat. Pilih kartu di sebelah kiri atau di kartu pemain.
                    </div>
                    """
                )

            undo_help = (
                f"Batalkan: {all_hist[-1]['player_name']} — {all_hist[-1]['card_name']}"
                if all_hist
                else "Belum ada aksi yang bisa dibatalkan."
            )
            st.button(
                "Batalkan (Undo) Aksi Terakhir",
                type="secondary",
                width="stretch",
                key="btn_undo_last_action",
                disabled=not bool(all_hist),
                on_click=callback_undo_last_action,
                help=undo_help,
            )

    p_cols = st.columns(4, gap="medium")
    for idx in range(4):
        p_id = idx + 1
        pl = st.session_state.players[p_id]
        faction = FACTION_THEMES[p_id]
        is_active_turn = (p_id == active_player_id)

        with p_cols[idx]:
            with st.container(border=True, key=f"panel_tracker_p{p_id}"):
                live_audit = compute_player_score(
                    player_name=pl["name"],
                    city_name=pl["city"],
                    project_ids=pl["projects"],
                    tech_codes=pl["techs"],
                    failed_problem_ids=pl["problems"],
                    coins=pl["coins"],
                    used_skill_codes=pl["skills"],
                    include_events=False,
                    active_event_id=active_event_id,
                    skill_bonus=pl["bonus_stats"],
                    active_tech_codes=pl["active_techs_this_round"],
                    accumulated_event_delta=pl["accumulated_event_delta"],
                    accumulated_event_coins=0,
                    is_immune=pl.get("immune_this_round", False),
                    manual_delta=pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
                    accumulated_tech_stats=pl.get("accumulated_tech_stats", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
                )
                arch = live_audit["archetype"]

                turn_badge_html = (
                    f"<span style='background:{faction['accent']};color:#FFFFFF;font-size:0.66rem;font-weight:900;padding:3px 9px;border-radius:999px;letter-spacing:0.06em;box-shadow:0 2px 8px {faction['border']};'>ACTIVE TURN</span>"
                    if is_active_turn
                    else "<span style='background:rgba(148,163,184,0.16);color:#64748B;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:999px;'>Standby</span>"
                )

                safe_city = html.escape(pl["city"])
                safe_name = html.escape(pl["name"])

                live_ev_coins = int(live_audit.get("live_event_coins", 0))
                effective_coins = int(live_audit.get("coins", pl["coins"]))
                ev_coin_tag = (
                    f" <span style='color:#047857;font-weight:800;'>({live_ev_coins:+d} Event)</span>"
                    if live_ev_coins != 0
                    else ""
                )

                faction_badge_uri = get_asset_uri(f"badge_faction_p{p_id}.png")
                faction_icon_html = (
                    f'<img src="{faction_badge_uri}" alt="{faction["name"]}" style="width:34px;height:34px;object-fit:contain;flex-shrink:0;" />'
                    if faction_badge_uri
                    else ""
                )
                arch_badge_uri = get_asset_uri(ARCHETYPE_BADGE_FILES.get(arch["name"], ""))
                arch_icon_html = (
                    f'<img src="{arch_badge_uri}" alt="{arch["name"]}" style="width:18px;height:18px;object-fit:contain;vertical-align:middle;flex-shrink:0;" />'
                    if arch_badge_uri
                    else ""
                )

                render_html(
                    f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:8px;">
                      <span style="display:inline-flex;align-items:center;gap:6px;background:{faction['badge_bg']};color:{faction['dark']};border:1px solid {faction['border']};font-family:'Outfit',sans-serif;font-size:0.72rem;font-weight:800;padding:3px 10px;border-radius:999px;letter-spacing:0.03em;">
                        {faction['short']}
                      </span>
                      {turn_badge_html}
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;">
                      <div style="display:flex;align-items:center;gap:8px;min-width:0;">
                        {faction_icon_html}
                        <div style="min-width:0;">
                          <div style="font-family:'Fredoka','Outfit',sans-serif;font-size:1.15rem;font-weight:800;color:#0F2A1D;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                            {safe_city}
                          </div>
                          <div style="font-size:0.76rem;font-weight:600;color:#4A5D52;margin-top:2px;">
                            Wali Kota: <b style="color:{faction['dark']};">{safe_name}</b>
                          </div>
                        </div>
                      </div>
                      <span class="tabular-num" style="flex-shrink:0;display:inline-flex;align-items:center;gap:4px;background:rgba(245,158,11,0.16);border:1px solid rgba(217,119,6,0.45);color:#B45309;font-family:'Outfit',sans-serif;font-size:0.75rem;font-weight:800;padding:4px 9px;border-radius:999px;">
                        {icon_img_html('icon_coin.png', 16, 'Koin', 0)}{effective_coins} Koin{ev_coin_tag}
                      </span>
                    </div>
                    """
                )
                rating = get_overall_rating_grade(live_audit["avg_score"])
                render_html(
                    f"""
                    <div style="background:linear-gradient(135deg,#FFFDF7 0%,{faction['tint']} 100%);border:1.5px solid {faction['border']};border-top:4px solid {faction['accent']};border-radius:16px;padding:10px 12px 9px 12px;margin:4px 0 8px 0;box-shadow:0 4px 12px rgba(22,78,51,0.07);">
                      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
                        <div style="text-align:left;min-width:0;">
                          <div style="font-family:'Outfit',sans-serif;font-size:0.68rem;color:#3E5B4C;font-weight:800;text-transform:uppercase;letter-spacing:0.05em;">Live Average Score</div>
                          <div class="stat-outfit" style="font-size:2.1rem;font-weight:900;color:{faction['dark']};line-height:1.05;">{live_audit['avg_score']:.2f}</div>
                          <div style="display:flex;align-items:center;gap:5px;font-size:0.74rem;font-weight:700;color:{arch['color']};margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                            {arch_icon_html}<span>{arch['name']}</span>
                          </div>
                        </div>
                        <div class="eco-rating-badge" title="Overall Rating: {rating['grade']} ({rating['label']})" style="background:{rating['bg']};color:{rating['fg']};border-color:#FFFDF7;box-shadow:0 4px 0 rgba(22,78,51,0.22), 0 0 0 2px {rating['ring']};">
                          <span style="font-size:0.52rem;font-weight:800;letter-spacing:0.06em;opacity:0.92;text-transform:uppercase;">GRADE</span>
                          <span style="font-size:1.32rem;font-weight:900;margin-top:1px;">{rating['grade']}</span>
                        </div>
                      </div>
                      <div style="margin-top:7px;padding-top:6px;border-top:1px dashed rgba(22,78,51,0.16);font-size:0.72rem;font-weight:700;color:#164E33;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;">
                        <span style="display:inline-flex;align-items:center;gap:3px;">{icon_img_html('icon_card_project.png', 15, 'Proyek', 0)}{len(pl['projects'])} Proyek</span>
                        <span>|</span>
                        <span style="display:inline-flex;align-items:center;gap:3px;">{icon_img_html('icon_card_tech.png', 15, 'Tech', 0)}{len(pl['techs'])} Tech</span>
                        <span>|</span>
                        <span style="display:inline-flex;align-items:center;gap:3px;">{icon_img_html('icon_card_problem.png', 15, 'Krisis', 0)}{len(pl['problems'])} Krisis</span>
                      </div>
                    </div>
                    """
                )

                p_last_delta = st.session_state.get("last_deltas", {}).get(p_id, {})
                delta_vals = p_last_delta.get("deltas", {}) if isinstance(p_last_delta, dict) else {}
                if delta_vals:
                    delta_pills = []
                    for dk in ("M", "E", "ENV", "QoL", "coins"):
                        dv = int(delta_vals.get(dk, 0))
                        if dv == 0:
                            continue
                        d_label = "Koin" if dk == "coins" else dk
                        if dv > 0:
                            d_cls = "eco-delta-gold" if dk in ("E", "coins") else "eco-delta-pos"
                        else:
                            d_cls = "eco-delta-neg"
                        delta_pills.append(f'<span class="eco-delta-badge {d_cls}">{dv:+d} {d_label}</span>')
                    if delta_pills:
                        d_card_name = html.escape(str(p_last_delta.get("card", "Aksi")))
                        render_html(
                            f"""
                            <div class="eco-delta-row">
                              <span style="font-size:0.68rem;font-weight:800;color:#3E5B4C;margin-right:2px;" title="{d_card_name}">Delta Terakhir:</span>
                              {"".join(delta_pills)}
                            </div>
                            """
                        )

                st.markdown(
                    build_aspect_progress_html("Mobility (M)", "M", live_audit["M"], live_audit["delta_M"], "#0284C7"),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    build_aspect_progress_html("Energy (E)", "E", live_audit["E"], live_audit["delta_E"], "#EAB308"),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    build_aspect_progress_html("Environment (ENV)", "ENV", live_audit["ENV"], live_audit["delta_ENV"], "#16A34A"),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    build_aspect_progress_html("Quality of Life", "QoL", live_audit["QoL"], live_audit["delta_QoL"], "#E11D48"),
                    unsafe_allow_html=True,
                )

                if pl.get("immune_this_round", False):
                    render_html(
                        f"""
                        <div style="display:flex;align-items:center;gap:6px;font-size:0.72rem;color:#047857;background:rgba(16,185,129,0.15);border:1px solid #10B981;border-radius:8px;padding:4px 8px;margin-top:4px;font-weight:700;">
                          {icon_img_html('icon_shield.png', 16, 'Shield', 0)}<span>S5 Cyber Shield Aktif: Kebal Semua Penalti Event Ronde Ini</span>
                        </div>
                        """
                    )

                if active_event_id and active_event_id in EVENT_BY_ID:
                    ev_mod = live_audit.get("live_event_modifier", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                    if any(ev_mod.values()):
                        ev_name = EVENT_BY_ID[active_event_id]["name"]
                        render_html(
                            f"""
                            <div style="font-size:0.72rem;color:#0284C7;background:rgba(2,132,199,0.1);border:1px solid rgba(2,132,199,0.3);border-radius:8px;padding:4px 8px;margin-top:4px;">
                              <b>Event Live ({ev_name}):</b> M:{ev_mod['M']:+d} | E:{ev_mod['E']:+d} | ENV:{ev_mod['ENV']:+d} | QoL:{ev_mod['QoL']:+d}
                            </div>
                            """
                        )

                if any(pl["bonus_stats"].values()):
                    sb = pl["bonus_stats"]
                    render_html(
                        f"""
                        <div style="font-size:0.72rem;color:#7C3AED;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.3);border-radius:8px;padding:4px 8px;margin-top:4px;">
                          <b>Akumulasi Bonus Skill:</b> M:+{sb['M']} | E:+{sb['E']} | ENV:+{sb['ENV']} | QoL:+{sb['QoL']}
                        </div>
                        """
                    )

                acc_tech = pl.get("accumulated_tech_stats", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                if any(acc_tech.values()):
                    render_html(
                        f"""
                        <div style="font-size:0.72rem;color:#0369A1;background:rgba(2,132,199,0.1);border:1px solid rgba(2,132,199,0.3);border-radius:8px;padding:4px 8px;margin-top:4px;">
                          <b>Akumulasi Tech Permanen:</b> M:+{acc_tech['M']} | E:+{acc_tech['E']} | ENV:+{acc_tech['ENV']} | QoL:+{acc_tech['QoL']}
                        </div>
                        """
                    )

                if pl["techs"]:
                    render_html(
                        f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 2px 5px 2px;margin-top:8px;border-bottom:1.5px solid #CFE2D4;">
                          <span style="display:inline-flex;align-items:center;gap:5px;font-family:'Outfit',sans-serif;font-size:0.72rem;font-weight:800;color:#164E33;letter-spacing:0.04em;text-transform:uppercase;">{icon_img_html('icon_card_tech.png', 16, 'Tech', 0)}AKSI TECH CARD · 1X / RONDE</span>
                          <span style="font-size:0.66rem;padding:2px 8px;border-radius:999px;background:#E0F2FE;border:1px solid #7DD3FC;color:#075985;font-weight:800;">Tetap Dimiliki</span>
                        </div>
                        """
                    )
                    t_cols = st.columns(len(pl["techs"]) if len(pl["techs"]) <= 2 else 2, gap="small")
                    for t_idx, tc in enumerate(pl["techs"]):
                        t_clean = get_card_clean_name(tc)
                        is_used = tc in pl["active_techs_this_round"]
                        resolvable_probs = get_resolvable_problems_for_tech(tc, pl["techs"], pl["problems"])
                        prob_hint = (
                            f" & selesaikan krisis {resolvable_probs[0]}"
                            if resolvable_probs
                            else ""
                        )

                        with t_cols[t_idx % len(t_cols)]:
                            if is_used:
                                st.button(
                                    f"{tc} [Sudah Dipakai]",
                                    key=f"btn_tech_{p_id}_{tc}",
                                    disabled=True,
                                    width="stretch",
                                    help=f"{tc} ({t_clean}) dipakai ronde ini & kartu tetap dimiliki. Reset di ronde berikutnya.",
                                )
                            else:
                                st.button(
                                    f"Pakai {t_clean}",
                                    key=f"btn_tech_{p_id}_{tc}",
                                    disabled=False,
                                    width="stretch",
                                    help=f"Aktifkan {t_clean} ronde ini{prob_hint}. Dapat dipakai tiap ronde & kartu tetap dimiliki.",
                                    on_click=callback_activate_tech,
                                    args=(p_id, tc),
                                )

                if pl["skills"]:
                    render_html(
                        f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 2px 5px 2px;margin-top:8px;border-bottom:1.5px solid #E5D9F2;">
                          <span style="display:inline-flex;align-items:center;gap:5px;font-family:'Outfit',sans-serif;font-size:0.72rem;font-weight:800;color:#5B21B6;letter-spacing:0.04em;text-transform:uppercase;">{icon_img_html('icon_card_skill.png', 16, 'Skill', 0)}PAKAI SKILL · SEKALI PAKAI</span>
                          <span style="font-size:0.66rem;padding:2px 8px;border-radius:999px;background:#FEF3C7;border:1px solid #F59E0B;color:#92400E;font-weight:800;">Consumed</span>
                        </div>
                        """
                    )

                    if "S1" in pl["skills"]:
                        if pl["problems"]:
                            s1_target = st.selectbox(
                                "Pilih Problem Card yang Dihapus via S1:",
                                options=pl["problems"],
                                format_func=format_problem_label,
                                key=f"sel_s1_target_{p_id}",
                            )
                            st.button(
                                "Pakai S1 (Hapus Problem)",
                                key=f"btn_use_s1_{p_id}",
                                width="stretch",
                                type="primary",
                                on_click=callback_use_s1,
                                args=(p_id, s1_target),
                            )
                        else:
                            st.caption("Pemain tidak memiliki Problem Card. Pakai S1 untuk Dana Darurat (+2 Semua Aspek):")
                            st.button(
                                "Pakai S1 (Dana Darurat +2 All)",
                                key=f"btn_use_s1_fb_{p_id}",
                                width="stretch",
                                on_click=callback_use_s1_fallback,
                                args=(p_id,),
                            )

                    other_skills = [s for s in pl["skills"] if s != "S1"]
                    if other_skills:
                        s_cols = st.columns(len(other_skills) if len(other_skills) <= 2 else 2, gap="small")
                        for s_idx, sc in enumerate(other_skills):
                            s_clean = get_card_clean_name(sc)
                            matching_probs = get_resolvable_problems_for_skill(sc, pl["problems"])
                            with s_cols[s_idx % len(s_cols)]:
                                if sc == "S5":
                                    st.button(
                                        f"Pakai {s_clean} (Kebal Event)",
                                        key=f"btn_use_s5_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s5,
                                        args=(p_id,),
                                    )
                                elif sc == "S2":
                                    st.button(
                                        f"Pakai {s_clean} (+5 ENV)",
                                        key=f"btn_use_s2_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s2,
                                        args=(p_id,),
                                    )
                                elif sc == "S3":
                                    st.button(
                                        f"Pakai {s_clean} (+5 M)",
                                        key=f"btn_use_s3_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s3,
                                        args=(p_id,),
                                    )
                                elif sc == "S4":
                                    st.button(
                                        f"Pakai {s_clean} (+5 QoL)",
                                        key=f"btn_use_s4_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s4,
                                        args=(p_id,),
                                    )

                                for mp_id in matching_probs:
                                    mp_name = get_card_clean_name(mp_id)
                                    st.button(
                                        f"Pakai {sc} (Amankan {mp_id})",
                                        key=f"btn_solve_{sc}_{mp_id}_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_skill_solve_problem,
                                        args=(p_id, sc, mp_id),
                                        help=f"Gunakan {s_clean} untuk mengamankan [{mp_name}] dan hapus kartu {sc}.",
                                    )

                cur_mp = pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                if st.session_state.get("enable_manual_points", False):
                    render_html(
                        f"""
                        <div style="background:rgba(255,255,255,0.92);border:1.5px solid rgba(2,132,199,0.3);border-radius:10px;padding:5px 10px;margin-top:6px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="display:inline-flex;align-items:center;gap:5px;font-size:0.76rem;color:#0F2A1D;">{icon_img_html('icon_tools.png', 15, 'Manual', 0)}Tambah Nilai Poin Manual</b>
                            <span style="font-size:0.66rem;padding:2px 6px;border-radius:6px;background:rgba(2,132,199,0.12);color:#0284C7;font-weight:700;">Live Mod</span>
                          </div>
                        </div>
                        """
                    )
                    mc1, mc2 = st.columns(2, gap="small")
                    with mc1:
                        st.number_input(
                            "Tambah M:",
                            min_value=-50,
                            max_value=50,
                            step=1,
                            key=f"widget_man_M_{p_id}",
                            on_change=callback_sync_manual_points,
                            args=(p_id, "M"),
                        )
                        st.number_input(
                            "Tambah ENV:",
                            min_value=-50,
                            max_value=50,
                            step=1,
                            key=f"widget_man_ENV_{p_id}",
                            on_change=callback_sync_manual_points,
                            args=(p_id, "ENV"),
                        )
                    with mc2:
                        st.number_input(
                            "Tambah E:",
                            min_value=-50,
                            max_value=50,
                            step=1,
                            key=f"widget_man_E_{p_id}",
                            on_change=callback_sync_manual_points,
                            args=(p_id, "E"),
                        )
                        st.number_input(
                            "Tambah QoL:",
                            min_value=-50,
                            max_value=50,
                            step=1,
                            key=f"widget_man_QoL_{p_id}",
                            on_change=callback_sync_manual_points,
                            args=(p_id, "QoL"),
                        )
                    if any(cur_mp.values()):
                        st.button(
                            "Reset Poin Manual",
                            key=f"btn_reset_man_{p_id}",
                            width="stretch",
                            on_click=callback_reset_manual_points,
                            args=(p_id,),
                        )
                elif any(cur_mp.values()):
                    render_html(
                        f"""
                        <div style="font-size:0.72rem;color:#0284C7;background:rgba(2,132,199,0.1);border:1px solid rgba(2,132,199,0.3);border-radius:8px;padding:4px 8px;margin-top:4px;">
                          <b>Poin Manual Aktif:</b> M:{cur_mp['M']:+d} | E:{cur_mp['E']:+d} | ENV:{cur_mp['ENV']:+d} | QoL:{cur_mp['QoL']:+d}
                        </div>
                        """
                    )

                with st.expander("Kelola Kartu & Kas", expanded=(p_id == active_player_id)):
                    with st.container(key=f"wrap_identity_sec_{p_id}"):
                        render_html(
                            f"""
                            <div class="eco-drawer-hdr">
                              <span class="eco-drawer-title">{icon_img_html('icon_city_identity.png', 17, 'Identitas', 2)}Identitas Kota</span>
                              <span class="eco-drawer-chip" style="background:{faction['badge_bg']};color:{faction['dark']};border-color:{faction['border']};">
                                {faction['short']}
                              </span>
                            </div>
                            """
                        )
                        c1, c2 = st.columns(2, gap="small")
                        with c1:
                            render_html(f'<div class="eco-field-cap">{icon_img_html("icon_mayor.png", 14, "Wali Kota", 2)}Wali Kota</div>')
                            st.text_input(
                                "Wali Kota:",
                                key=f"widget_name_{p_id}",
                                placeholder="Nama wali kota...",
                                label_visibility="collapsed",
                                on_change=callback_sync_name,
                                args=(p_id,),
                            )
                        with c2:
                            render_html(f'<div class="eco-field-cap">{icon_img_html("icon_city.png", 14, "Kota", 2)}Nama Kota</div>')
                            st.text_input(
                                "Nama Kota:",
                                key=f"widget_city_{p_id}",
                                placeholder="Nama kota...",
                                label_visibility="collapsed",
                                on_change=callback_sync_city,
                                args=(p_id,),
                            )

                    with st.container(key=f"wrap_proj_sec_{p_id}"):
                        render_html(
                            f"""
                            <div class="eco-drawer-hdr">
                              <span class="eco-drawer-title">{icon_img_html('icon_card_project.png', 17, 'Proyek', 2)}Proyek Dibangun <span class="eco-drawer-sub">(120)</span></span>
                              <span class="eco-drawer-chip" style="background:#DCFCE7;color:#14532D;border-color:#86EFAC;">
                                {len(pl['projects'])} / 120
                              </span>
                            </div>
                            """
                        )
                        st.multiselect(
                            "Proyek Dibangun (120):",
                            options=project_id_options,
                            format_func=format_project_label,
                            placeholder="Pilih kartu proyek...",
                            label_visibility="collapsed",
                            key=f"widget_projects_{p_id}",
                            on_change=callback_sync_projects,
                            args=(p_id,),
                        )

                    with st.container(key=f"wrap_tech_sec_{p_id}"):
                        render_html(
                            f"""
                            <div class="eco-drawer-hdr">
                              <span class="eco-drawer-title">{icon_img_html('icon_card_tech.png', 17, 'Tech', 2)}Permanent Tech <span class="eco-drawer-sub">(T1–T5)</span></span>
                              <span class="eco-drawer-chip" style="background:#E0F2FE;color:#075985;border-color:#7DD3FC;">
                                {len(pl['techs'])} / 5
                              </span>
                            </div>
                            """
                        )
                        st.multiselect(
                            "Permanent Tech Dimiliki (T1–T5):",
                            options=tech_code_options,
                            format_func=format_tech_label,
                            placeholder="Pilih tech T1–T5...",
                            label_visibility="collapsed",
                            key=f"widget_techs_{p_id}",
                            on_change=callback_sync_techs,
                            args=(p_id,),
                        )

                    with st.container(key=f"wrap_skill_sec_{p_id}"):
                        render_html(
                            f"""
                            <div class="eco-drawer-hdr">
                              <span class="eco-drawer-title">{icon_img_html('icon_card_skill.png', 17, 'Skill', 2)}Skill Card di Tangan <span class="eco-drawer-sub">(S1–S5)</span></span>
                              <span class="eco-drawer-chip" style="background:#FEF3C7;color:#92400E;border-color:#FCD34D;">
                                {len(pl['skills'])} / 5
                              </span>
                            </div>
                            """
                        )
                        st.multiselect(
                            "Skill Card di Tangan (S1–S5):",
                            options=skill_code_options,
                            format_func=format_skill_label,
                            placeholder="Pilih skill S1–S5...",
                            label_visibility="collapsed",
                            key=f"widget_skills_{p_id}",
                            on_change=callback_sync_skills,
                            args=(p_id,),
                        )

                    with st.container(key=f"wrap_prob_sec_{p_id}"):
                        render_html(
                            f"""
                            <div class="eco-drawer-hdr">
                              <span class="eco-drawer-title">{icon_img_html('icon_card_problem.png', 17, 'Krisis', 2)}Krisis Gagal <span class="eco-drawer-sub">(Penalti)</span></span>
                              <span class="eco-drawer-chip" style="background:#FFE4E6;color:#9F1239;border-color:#FDA4AF;">
                                {len(pl['problems'])} Krisis
                              </span>
                            </div>
                            """
                        )
                        st.multiselect(
                            "Krisis Gagal (Penalti):",
                            options=problem_id_options,
                            format_func=format_problem_label,
                            placeholder="Pilih kartu krisis...",
                            label_visibility="collapsed",
                            key=f"widget_problems_{p_id}",
                            on_change=callback_sync_problems,
                            args=(p_id,),
                        )

                    coin_bonus_val = calculate_coin_bonus(effective_coins)
                    coin_chip_txt = (
                        f"+{coin_bonus_val} Pt/Aspek"
                        if coin_bonus_val > 0
                        else f"{effective_coins % 20}/20 → +5 Pt"
                    )
                    with st.container(key=f"wrap_coin_sec_{p_id}"):
                        render_html(
                            f"""
                            <div class="eco-drawer-hdr">
                              <span class="eco-drawer-title">{icon_img_html('icon_coin.png', 17, 'Koin', 2)}Kas Koin Saat Ini</span>
                              <span class="eco-drawer-chip" style="background:#FFFFFF;color:#92400E;border-color:#F59E0B;">
                                {coin_chip_txt}
                              </span>
                            </div>
                            """
                        )
                        st.number_input(
                            "Kas Koin Saat Ini:",
                            min_value=0,
                            max_value=300,
                            step=1,
                            label_visibility="collapsed",
                            key=f"widget_coins_{p_id}",
                            on_change=callback_sync_coins,
                            args=(p_id,),
                        )
                        if live_ev_coins != 0:
                            render_html(
                                f"""
                                <div style="font-size:0.69rem;font-weight:700;color:#92400E;text-align:center;margin-top:2px;">
                                  Termasuk Event aktif {live_ev_coins:+d} → Total efektif {effective_coins} Koin
                                </div>
                                """
                            )

                if pl["tech_log"]:
                    last_act = pl["tech_log"][-1]
                    render_html(
                        f"""
                        <div style="font-size:0.71rem;color:#047857;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:4px 8px;margin-top:6px;">
                          <b>Riwayat Aksi:</b> {last_act}
                        </div>
                        """
                    )

    # --------------------------------------------------------------------------
    # FOOTER KONTROL TAB 1: KUNCI SIMULASI & OTOMATIS PINDAH KE TAB 2
    # --------------------------------------------------------------------------
    st.write("")
    f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
    with f_col2:
        st.button(
            "Kunci Simulasi & Buka Final Audit",
            type="primary",
            width="stretch",
            key="btn_lock_and_audit",
            on_click=callback_lock_and_open_audit,
            help="Kunci seluruh skor ronde dan langsung buka halaman Final AI Audit & Sertifikat 2075.",
        )


# ==============================================================================
# TAB 2: FINAL AI AUDIT (VICTORY PODIUM, RADAR & OFFICIAL DIPLOMA 2075)
# ==============================================================================
def render_tab_audit() -> None:
    """Merender Tab 2: Final AI Audit, Leaderboard, Radar & Sertifikat Diploma Kota 2075."""
    audit_mode_options = [
        "Gunakan Riwayat Event Ronde Aktual",
        "Gunakan Simulasi Otomatis 13 Event",
    ]

    if not st.session_state.get("audit_triggered", False):
        logo_uri = get_econova_logo_uri()
        pre_logo_badge = (
            f'<div style="background:#164E33;padding:5px 12px;border-radius:10px;display:inline-flex;align-items:center;"><img src="{logo_uri}" alt="EcoNova" style="height:26px;width:auto;display:block;" /></div>'
            if logo_uri
            else ""
        )
        render_html(
            f"""
            <div class="cert-diploma" style="text-align:center;margin:10px 0 18px 0;">
              <div style="display:inline-flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:12px;">
                {pre_logo_badge}
                <span class="eco-ribbon-header" style="font-size:0.78rem;padding:6px 16px;">AKREDITASI RESMI ECONOVA 2075 · MODE SIAGA</span>
              </div>
              <h2 style="font-family:'Fredoka','Outfit',sans-serif;font-size:2.15rem;color:#164E33;margin:0 0 8px 0;font-weight:900;">
                Evaluasi Performa Kota &amp; Sertifikasi EcoNova 2075
              </h2>
              <div style="max-width:740px;margin:0 auto;color:#3E5B4C;font-size:0.95rem;line-height:1.6;">
                Setelah permainan selesai di papan fisik, verifikasi kas koin akhir keempat wali kota di bawah ini lalu
                jalankan audit untuk menerbitkan Podium Juara, Radar Keseimbangan, dan Diploma Tata Kota 2075.
              </div>
            </div>
            """
        )

        with st.container(border=True, key="panel_audit_coins_pre"):
            render_html(
                """
                <div class="eco-ribbon-wrap" style="margin-top:0;">
                  <span class="eco-ribbon-header" style="font-size:0.78rem;padding:5px 16px;">KONFIGURASI EVENT &amp; VERIFIKASI KAS KOIN AKHIR</span>
                  <span style="font-size:0.76rem;font-weight:700;color:#B45309;background:#FEF3C7;border:1px solid #F59E0B;border-radius:999px;padding:3px 11px;">
                    Rulebook Bab VI.1: Tiap 20 Koin = +5 ke 4 Pilar
                  </span>
                </div>
                """
            )
            st.radio(
                "Sumber Evaluasi Event Card untuk Final Audit:",
                options=audit_mode_options,
                horizontal=True,
                key="audit_event_mode",
            )
            c_cols = st.columns(4, gap="medium")
            for idx in range(4):
                p_id = idx + 1
                pl = st.session_state.players[p_id]
                f_th = FACTION_THEMES[p_id]
                curr_c = int(pl["coins"])
                b_pts = calculate_coin_bonus(curr_c)
                next_tier = ((curr_c // 20) + 1) * 20
                need = next_tier - curr_c
                with c_cols[idx]:
                    render_html(
                        f"""
                        <div style="background:linear-gradient(180deg,#FFFDF7 0%,{f_th['tint']} 100%);border:2px solid {f_th['border']};border-top:4px solid {f_th['accent']};border-radius:16px;padding:14px;text-align:center;box-shadow:0 4px 0 rgba(22,78,51,0.10);">
                          <span style="background:{f_th['badge_bg']};color:{f_th['dark']};font-size:0.7rem;font-weight:800;padding:2px 9px;border-radius:999px;">{f_th['short']}</span>
                          <div style="font-family:'Fredoka',sans-serif;font-size:1.05rem;color:#164E33;font-weight:800;margin-top:5px;">{html.escape(pl['city'])}</div>
                          <div style="font-size:0.76rem;color:#4A5D52;font-weight:600;">{html.escape(pl['name'])}</div>
                          <div class="stat-outfit" style="font-size:1.95rem;font-weight:900;color:#B45309;line-height:1.15;margin:6px 0;display:flex;align-items:center;justify-content:center;gap:6px;">
                            {icon_img_html('icon_coin.png', 24, 'Koin', 0)}<span>{curr_c} Koin</span>
                          </div>
                          <div style="display:inline-block;background:#DCFCE7;color:#15803D;border:1px solid #86EFAC;border-radius:999px;padding:2px 10px;font-size:0.76rem;font-weight:800;">
                            Bonus Akhir: +{b_pts} Semua Pilar
                          </div>
                          <div style="font-size:0.71rem;color:#476656;margin-top:5px;font-weight:600;">
                            +{need} Koin menuju tier +{b_pts + 5}
                          </div>
                        </div>
                        """
                    )

        st.write("")
        exec_c1, exec_c2, exec_c3 = st.columns([1, 2, 1])
        with exec_c2:
            if st.button(
                "JALANKAN AUDIT SIMULASI KOTA MASA DEPAN",
                type="primary",
                width="stretch",
                key="btn_run_audit_strict_lazy",
            ):
                st.session_state.audit_triggered = True
                st.rerun()

    else:
        with st.container(border=True, key="panel_audit_topctrl"):
            top_ctrl_c1, top_ctrl_c2 = st.columns([7, 3])
            with top_ctrl_c1:
                render_html(
                    f"""
                    <div class="eco-ribbon-wrap" style="margin:0;">
                      <span class="eco-ribbon-header">FINAL AI AUDIT · HASIL RESMI 2075</span>
                      <span style="display:inline-flex;align-items:center;gap:5px;font-size:0.76rem;font-weight:800;color:#15803D;background:#DCFCE7;border:1px solid #86EFAC;border-radius:999px;padding:4px 12px;">
                        {icon_img_html('icon_check.png', 16, 'Terverifikasi', 0)}<span>Terverifikasi Rulebook EcoNova v1.0</span>
                      </span>
                    </div>
                    """
                )
            with top_ctrl_c2:
                if st.button(
                    "Kembali ke Live Tracker",
                    width="stretch",
                    key="btn_unlock_audit",
                ):
                    st.session_state.audit_triggered = False
                    st.session_state.active_tab = "Tab 1: Live Tracker"
                    st.rerun()

            use_auto_13 = st.radio(
                "Mode Evaluasi Event Audit:",
                options=audit_mode_options,
                horizontal=True,
                key="audit_event_mode",
            ) == "Gunakan Simulasi Otomatis 13 Event"

        active_ev_for_audit = st.session_state.get("selected_event_id")

        final_player_audits = []
        for idx in range(4):
            p_id = idx + 1
            pl = st.session_state.players[p_id]
            if use_auto_13:
                base_coins_for_sim = max(0, int(pl["coins"]) - int(pl.get("committed_event_coins", 0)))
                f_aud = compute_player_score(
                    player_name=pl["name"],
                    city_name=pl["city"],
                    project_ids=pl["projects"],
                    tech_codes=pl["techs"],
                    failed_problem_ids=pl["problems"],
                    coins=base_coins_for_sim,
                    used_skill_codes=pl["skills"],
                    include_events=True,
                    skill_bonus=pl["bonus_stats"],
                    manual_delta=pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
                    accumulated_tech_stats=pl.get("accumulated_tech_stats", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
                )
            else:
                f_aud = compute_player_score(
                    player_name=pl["name"],
                    city_name=pl["city"],
                    project_ids=pl["projects"],
                    tech_codes=pl["techs"],
                    failed_problem_ids=pl["problems"],
                    coins=pl["coins"],
                    used_skill_codes=pl["skills"],
                    include_events=False,
                    active_event_id=active_ev_for_audit,
                    skill_bonus=pl["bonus_stats"],
                    active_tech_codes=None,
                    accumulated_event_delta=pl["accumulated_event_delta"],
                    accumulated_event_coins=0,
                    is_immune=pl.get("immune_this_round", False),
                    manual_delta=pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
                    accumulated_tech_stats=pl.get("accumulated_tech_stats", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
                )
            final_player_audits.append(f_aud)

        ranked_players = rank_players_audit(final_player_audits)
        winner = ranked_players[0]
        win_grade = get_overall_rating_grade(winner["avg_score"])

        # Champion Victory Banner
        win_rank_uri = get_asset_uri("badge_rank_1.png")
        win_arch_uri = get_asset_uri(ARCHETYPE_BADGE_FILES.get(winner["archetype"]["name"], ""))
        win_rank_img = (
            f'<img src="{win_rank_uri}" alt="Juara 1" style="width:52px;height:52px;object-fit:contain;vertical-align:middle;" />'
            if win_rank_uri
            else ""
        )
        win_arch_img = (
            f'<img src="{win_arch_uri}" alt="{winner["archetype"]["name"]}" style="width:22px;height:22px;object-fit:contain;vertical-align:middle;" />'
            if win_arch_uri
            else ""
        )
        render_html(
            f"""
            <div class="eco-card-champion" style="text-align:center;margin:8px 0 20px 0;padding:24px;">
              <div style="display:inline-flex;align-items:center;gap:10px;justify-content:center;">
                {win_rank_img}
                <span class="badge-champion">{icon_img_html('icon_trophy.png', 18, 'Trophy', 2)}CITY PERFORMANCE LEADER · JUARA 1 TATA KOTA 2075</span>
              </div>
              <h2 style="margin:10px 0 4px 0;font-size:2.45rem;color:#164E33;font-family:'Fredoka','Outfit',sans-serif;font-weight:900;">
                <span style="color:#B45309;">{html.escape(winner['city_name'])}</span> — {html.escape(winner['player_name'])}
              </h2>
              <div style="display:inline-flex;align-items:center;gap:14px;flex-wrap:wrap;justify-content:center;margin-top:8px;background:#FFFDF7;border:1.5px solid #F59E0B;border-radius:999px;padding:7px 20px;">
                <span style="font-size:0.95rem;font-weight:700;color:#164E33;">
                  Skor Rata-Rata: <b class="tabular-num" style="color:#B45309;font-size:1.25rem;">{winner['avg_score']:.2f} / 100</b>
                </span>
                <span style="color:#CBD5E1;">|</span>
                <span style="display:inline-flex;align-items:center;gap:6px;font-size:0.92rem;font-weight:800;color:{winner['archetype']['color']};">
                  {win_arch_img}<span>{winner['archetype']['name']}</span>
                </span>
                <span style="color:#CBD5E1;">|</span>
                <span style="background:{win_grade['bg']};color:#FFFFFF;font-family:'Fredoka',sans-serif;font-weight:900;font-size:0.86rem;padding:2px 11px;border-radius:999px;">
                  Grade {win_grade['grade']}
                </span>
              </div>
            </div>
            """
        )

        # 4 Podium Cards dengan Warna Medali Distinct per Peringkat
        podium_cols = st.columns(4, gap="medium")
        medal_styles = [
            {"title": "JUARA 1", "accent": "#D97706", "bg": "#FEF3C7", "fg": "#92400E", "border": "#F59E0B"},
            {"title": "PERINGKAT 2", "accent": "#0284C7", "bg": "#E0F2FE", "fg": "#075985", "border": "#38BDF8"},
            {"title": "PERINGKAT 3", "accent": "#16A34A", "bg": "#DCFCE7", "fg": "#14532D", "border": "#4ADE80"},
            {"title": "PERINGKAT 4", "accent": "#E11D48", "bg": "#FFE4E6", "fg": "#9F1239", "border": "#FB7185"},
        ]

        for r_idx, p_res in enumerate(ranked_players):
            is_champ = r_idx == 0
            card_cls = "eco-card-champion" if is_champ else "eco-card"
            arch = p_res["archetype"]
            m_st = medal_styles[r_idx]
            pod_rating = get_overall_rating_grade(p_res["avg_score"])
            rank_badge_uri = get_asset_uri(f"badge_rank_{p_res['rank']}.png")
            rank_badge_img = (
                f'<img src="{rank_badge_uri}" alt="Rank {p_res["rank"]}" style="width:34px;height:34px;object-fit:contain;flex-shrink:0;" />'
                if rank_badge_uri
                else ""
            )
            pod_arch_uri = get_asset_uri(ARCHETYPE_BADGE_FILES.get(arch["name"], ""))
            pod_arch_img = (
                f'<img src="{pod_arch_uri}" alt="{arch["name"]}" style="width:18px;height:18px;object-fit:contain;vertical-align:middle;flex-shrink:0;" />'
                if pod_arch_uri
                else ""
            )

            tb_note = ""
            if p_res.get("tie_breaker_reason"):
                tb_note = (
                    f'<div style="display:flex;align-items:center;gap:6px;background:rgba(234,179,8,0.18);border:1px solid #EAB308;color:#92400E;'
                    f'border-radius:10px;padding:6px 10px;font-size:0.75rem;font-weight:700;margin-top:8px;">'
                    f'{icon_img_html("icon_scale.png", 16, "Tie-Breaker", 0)}<span>{html.escape(p_res["tie_breaker_reason"])}</span></div>'
                )

            with podium_cols[r_idx]:
                b_m = build_aspect_progress_html("Mobility", "M", p_res["M"], p_res["delta_M"], "#0284C7")
                b_e = build_aspect_progress_html("Energy", "E", p_res["E"], p_res["delta_E"], "#EAB308")
                b_env = build_aspect_progress_html("Environment", "ENV", p_res["ENV"], p_res["delta_ENV"], "#16A34A")
                b_qol = build_aspect_progress_html("Quality of Life", "QoL", p_res["QoL"], p_res["delta_QoL"], "#E11D48")

                render_html(
                    f"""
                    <div class="{card_cls}" style="margin-bottom:12px;border-top:5px solid {m_st['accent']};">
                      <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;">
                        <span style="display:inline-flex;align-items:center;gap:5px;background:{m_st['bg']};color:{m_st['fg']};font-family:'Fredoka',sans-serif;font-size:0.75rem;font-weight:800;padding:3px 10px;border-radius:999px;border:1.5px solid {m_st['border']};">
                          {icon_img_html(f"badge_rank_{p_res['rank']}.png", 16, f"Rank {p_res['rank']}", 0)}{m_st['title']}
                        </span>
                        {rank_badge_img}
                      </div>
                      <h4 style="margin:8px 0 2px 0;font-size:1.24rem;color:#164E33;font-family:'Fredoka','Outfit',sans-serif;font-weight:800;">
                        {html.escape(p_res['city_name'])}
                      </h4>
                      <div style="font-size:0.84rem;color:#3E5B4C;font-weight:600;margin-bottom:8px;">
                        Wali Kota: <b>{html.escape(p_res['player_name'])}</b>
                      </div>
                      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;background:#FFFDF7;border:1.5px solid {m_st['border']};border-radius:14px;padding:8px 12px;margin-bottom:10px;">
                        <div style="text-align:left;min-width:0;">
                          <div style="font-family:'Outfit',sans-serif;font-size:0.66rem;color:#3E5B4C;font-weight:800;text-transform:uppercase;">Average Score</div>
                          <div class="stat-outfit" style="font-size:1.85rem;font-weight:900;color:#164E33;line-height:1.1;">{p_res['avg_score']:.2f}</div>
                          <div style="display:flex;align-items:center;gap:5px;font-size:0.73rem;font-weight:700;color:{arch['color']};margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                            {pod_arch_img}<span>{arch['name']}</span>
                          </div>
                        </div>
                        <div class="eco-rating-badge" style="width:48px;height:48px;min-width:48px;background:{pod_rating['bg']};color:{pod_rating['fg']};border-color:#FFFDF7;box-shadow:0 3px 0 rgba(22,78,51,0.2), 0 0 0 2px {pod_rating['ring']};">
                          <span style="font-size:0.48rem;font-weight:800;letter-spacing:0.05em;">GRADE</span>
                          <span style="font-size:1.15rem;font-weight:900;">{pod_rating['grade']}</span>
                        </div>
                      </div>
                      {b_m}
                      {b_e}
                      {b_env}
                      {b_qol}
                      <div class="tabular-num" style="margin-top:10px;padding-top:8px;border-top:1px dashed rgba(22,78,51,0.18);font-size:0.76rem;color:#164E33;font-weight:700;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;">
                        <span style="display:inline-flex;align-items:center;gap:3px;">{icon_img_html('icon_card_project.png', 15, 'Proyek', 0)}{p_res['project_count']} Proyek</span>
                        <span>·</span>
                        <span style="display:inline-flex;align-items:center;gap:3px;">{icon_img_html('icon_card_tech.png', 15, 'Tech', 0)}{p_res['tech_count']} Tech</span>
                        <span>·</span>
                        <span style="display:inline-flex;align-items:center;gap:3px;">{icon_img_html('icon_coin.png', 15, 'Koin', 0)}{p_res['coins']} Koin</span>
                      </div>
                      {tb_note}
                    </div>
                    """
                )

        # Matriks Perbandingan & Radar Chart
        mat_col, rad_col = st.columns([6.2, 3.8], gap="large")
        with mat_col:
            with st.container(border=True, key="panel_audit_matrix"):
                render_html(
                    """
                    <div class="eco-ribbon-wrap" style="margin-top:0;">
                      <span class="eco-ribbon-header" style="font-size:0.76rem;padding:5px 15px;">MATRIKS PERBANDINGAN &amp; TIE-BREAKER</span>
                    </div>
                    """
                )
                st.caption("Urutan Resmi Rulebook (Bab VI.3): Average Score → Proyek Terbangun → Permanent Tech → Sisa Koin.")

                matrix_rows_html = ""
                for idx_m, p_m in enumerate(ranked_players):
                    m_st = medal_styles[idx_m]
                    g_m = get_overall_rating_grade(p_m["avg_score"])
                    m_rank_uri = get_asset_uri(f"badge_rank_{p_m['rank']}.png")
                    m_rank_img = (
                        f'<img src="{m_rank_uri}" alt="Rank {p_m["rank"]}" style="width:20px;height:20px;object-fit:contain;vertical-align:middle;" />'
                        if m_rank_uri
                        else ""
                    )
                    matrix_rows_html += f"""
                    <tr style="border-bottom:1px solid #E2ECE5;">
                      <td style="padding:10px 8px;">
                        <span style="display:inline-flex;align-items:center;gap:4px;background:{m_st['bg']};color:{m_st['fg']};border:1px solid {m_st['border']};font-weight:800;font-size:0.76rem;padding:2px 8px;border-radius:999px;">
                          {m_rank_img} #{p_m['rank']}
                        </span>
                      </td>
                      <td style="padding:10px 8px;font-weight:800;color:#164E33;">
                        {html.escape(p_m['city_name'])}<br/>
                        <span style="font-size:0.75rem;color:#476656;font-weight:600;">{html.escape(p_m['player_name'])}</span>
                      </td>
                      <td class="tabular-num" style="padding:10px 8px;text-align:center;">
                        <span style="font-family:'Fredoka',sans-serif;font-weight:900;color:#164E33;font-size:1.05rem;">{p_m['avg_score']:.2f}</span>
                        <span style="background:{g_m['bg']};color:#FFFFFF;font-size:0.68rem;font-weight:800;padding:1px 6px;border-radius:999px;margin-left:4px;">{g_m['grade']}</span>
                      </td>
                      <td class="tabular-num" style="padding:10px 8px;text-align:center;font-weight:700;">{p_m['project_count']}</td>
                      <td class="tabular-num" style="padding:10px 8px;text-align:center;font-weight:700;">{p_m['tech_count']}</td>
                      <td class="tabular-num" style="padding:10px 8px;text-align:center;">
                        <span style="display:inline-flex;align-items:center;gap:4px;background:#FEF3C7;color:#B45309;border:1px solid #F59E0B;border-radius:999px;padding:2px 8px;font-weight:800;font-size:0.78rem;">{icon_img_html('icon_coin.png', 15, 'Koin', 0)}{p_m['coins']}</span>
                      </td>
                      <td style="padding:10px 8px;font-size:0.76rem;color:#3E5B4C;font-weight:600;">{html.escape(p_m.get('tie_breaker_reason') or 'Skor Rata-Rata Tertinggi')}</td>
                    </tr>
                    """

                render_html(
                    f"""
                    <div style="overflow-x:auto;">
                      <table style="width:100%;border-collapse:collapse;font-size:0.85rem;color:#164E33;">
                        <thead>
                          <tr style="background:#F4F1E1;border-bottom:2px solid #B7D5C4;text-align:left;">
                            <th style="padding:9px 8px;">Rank</th>
                            <th style="padding:9px 8px;">Kota &amp; Wali Kota</th>
                            <th style="padding:9px 8px;text-align:center;">Avg &amp; Grade</th>
                            <th style="padding:9px 8px;text-align:center;">Proyek</th>
                            <th style="padding:9px 8px;text-align:center;">Tech</th>
                            <th style="padding:9px 8px;text-align:center;">Koin</th>
                            <th style="padding:9px 8px;">Status Peringkat</th>
                          </tr>
                        </thead>
                        <tbody>
                          {matrix_rows_html}
                        </tbody>
                      </table>
                    </div>
                    """
                )

                with st.expander("Rincian Dampak Global Event per Pemain", expanded=False):
                    ev_cols = st.columns(4, gap="small")
                    for idx in range(4):
                        aud = final_player_audits[idx]
                        pl = st.session_state.players[idx + 1]
                        with ev_cols[idx]:
                            ev_d = aud.get("event_delta", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                            ev_c = aud.get("event_coins", 0) if use_auto_13 else int(pl.get("committed_event_coins", 0)) + int(aud.get("live_event_coins", 0))
                            render_html(
                                f"""
                                <div style="background:#F9F6E8;border:1px solid #B7D5C4;border-radius:12px;padding:9px;font-size:0.75rem;">
                                  <b style="color:#164E33;">{html.escape(aud['player_name'])}</b><br/>
                                  <span style="color:#B45309;font-weight:700;">Koin Event: +{ev_c}</span><br/>
                                  <span style="color:#15803D;font-weight:700;">M:{ev_d.get('M',0):+d} E:{ev_d.get('E',0):+d} ENV:{ev_d.get('ENV',0):+d} QoL:{ev_d.get('QoL',0):+d}</span>
                                </div>
                                """
                            )

        with rad_col:
            with st.container(border=True, key="panel_audit_radar"):
                render_html(
                    """
                    <div class="eco-ribbon-wrap" style="margin-top:0;">
                      <span class="eco-ribbon-header" style="font-size:0.76rem;padding:5px 15px;">RADAR 4 PILAR KOTA</span>
                    </div>
                    """
                )
                st.caption("Profil keseimbangan Mobility, Energy, Environment, dan Quality of Life.")

                if go is not None:
                    categories = ["Mobility (M)", "Energy (E)", "Environment (ENV)", "Quality of Life (QoL)"]
                    radar_colors = ["#D97706", "#0284C7", "#16A34A", "#E11D48"]
                    fig = go.Figure()
                    for idx, p_rad in enumerate(ranked_players):
                        vals = [p_rad["M"], p_rad["E"], p_rad["ENV"], p_rad["QoL"]]
                        vals.append(vals[0])
                        fig.add_trace(
                            go.Scatterpolar(
                                r=vals,
                                theta=categories + [categories[0]],
                                fill="toself",
                                name=f"#{p_rad['rank']} {p_rad['city_name']}",
                                line=dict(color=radar_colors[idx % len(radar_colors)], width=2.5),
                                fillcolor=radar_colors[idx % len(radar_colors)],
                                opacity=0.28,
                            )
                        )
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100],
                                gridcolor="#CBE3D4",
                                linecolor="#B7D5C4",
                                tickfont=dict(size=10, color="#3E5B4C"),
                            ),
                            angularaxis=dict(
                                gridcolor="#CBE3D4",
                                linecolor="#B7D5C4",
                                tickfont=dict(size=11, color="#164E33", family="Plus Jakarta Sans"),
                            ),
                            bgcolor="#FFFDF7",
                        ),
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
                        margin=dict(l=35, r=35, t=22, b=42),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=330,
                    )
                    st.plotly_chart(fig, width="stretch")

        # ----------------------------------------------------------------------
        # SERTIFIKAT DIPLOMA TATA KOTA MASA DEPAN (TAHUN 2075)
        # ----------------------------------------------------------------------
        st.markdown("---")
        with st.container(border=True, key="panel_narrative_reports"):
            nar_hdr1, nar_hdr2 = st.columns([7, 3])
            with nar_hdr1:
                render_html(
                    """
                    <div class="eco-ribbon-wrap" style="margin-top:0;">
                      <span class="eco-ribbon-header">SERTIFIKAT AKREDITASI &amp; VISI KOTA 2075</span>
                    </div>
                    """
                )
                st.caption("Diploma resmi tata kota berkelanjutan: 4 pilar evaluasi AI Auditor, kekuatan infrastruktur, mitigasi krisis, dan visi tahun 2075.")
            with nar_hdr2:
                st.checkbox(
                    "Perkaya narasi dengan AI LLM (Groq)",
                    value=False,
                    key="use_llm_narrative",
                )

            report_tabs = st.tabs(
                [f"#{p['rank']} {p['city_name']} ({p['player_name']})" for p in ranked_players]
            )

            for r_idx, r_tab in enumerate(report_tabs):
                p_res = ranked_players[r_idx]
                arch = p_res["archetype"]
                tiers = arch.get("tiers", {})
                nar = generate_llm_enhanced_narrative(p_res)
                is_first = (r_idx == 0)
                cert_grade = get_overall_rating_grade(p_res["avg_score"])

                with r_tab:
                    logo_uri = get_econova_logo_uri()
                    seal_uri = get_asset_uri("seal_diploma_2075.png")
                    cert_arch_uri = get_asset_uri(ARCHETYPE_BADGE_FILES.get(arch["name"], ""))
                    cert_rank_uri = get_asset_uri(f"badge_rank_{p_res['rank']}.png")
                    p_e_uri = get_asset_uri("badge_pillar_e.png")
                    p_m_uri = get_asset_uri("badge_pillar_m.png")
                    p_env_uri = get_asset_uri("badge_pillar_env.png")
                    p_qol_uri = get_asset_uri("badge_pillar_qol.png")

                    cert_logo_badge = (
                        f'<div style="background:#164E33;padding:5px 12px;border-radius:10px;display:inline-flex;align-items:center;"><img src="{logo_uri}" alt="EcoNova" style="height:26px;width:auto;display:block;" /></div>'
                        if logo_uri
                        else ""
                    )
                    cert_rank_img = (
                        f'<img src="{cert_rank_uri}" alt="Peringkat {p_res["rank"]}" style="width:30px;height:30px;object-fit:contain;vertical-align:middle;" />'
                        if cert_rank_uri
                        else ""
                    )
                    cert_arch_img = (
                        f'<img src="{cert_arch_uri}" alt="{arch["name"]}" style="width:22px;height:22px;object-fit:contain;vertical-align:middle;margin-right:4px;" />'
                        if cert_arch_uri
                        else ""
                    )
                    cert_seal_img = (
                        f'<img src="{seal_uri}" alt="EcoNova Certified 2075 Seal" style="width:76px;height:76px;object-fit:contain;flex-shrink:0;" />'
                        if seal_uri
                        else ""
                    )
                    e_icon_tag = icon_img_html("badge_pillar_e.png", 18, "E", 4)
                    m_icon_tag = icon_img_html("badge_pillar_m.png", 18, "M", 4)
                    env_icon_tag = icon_img_html("badge_pillar_env.png", 18, "ENV", 4)
                    qol_icon_tag = icon_img_html("badge_pillar_qol.png", 18, "QoL", 4)

                    cert_kop_html = f"""
                    <div class="eco-cert-kop-wrap">
                      {cert_logo_badge}
                      {cert_rank_img}
                      <span class="eco-ribbon-header" style="font-size:0.74rem;padding:5px 15px;">AKREDITASI RESMI TATA KOTA 2075 · PERINGKAT #{p_res["rank"]}</span>
                    </div>
                    """
                    champ_banner = (
                        f'<div style="margin-bottom:8px;"><span class="badge-champion">{icon_img_html("icon_trophy.png", 16, "Juara", 2)}CITY PERFORMANCE LEADER · TATA KOTA TERBAIK 2075</span></div>'
                        if is_first
                        else ""
                    )

                    render_html(
                        f"""
                        <div class="cert-diploma">
                          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
                            <div>
                              {cert_kop_html}
                              {champ_banner}
                              <h2 style="font-family:'Fredoka','Outfit',sans-serif;font-size:2.2rem;color:#164E33;margin:4px 0;font-weight:900;">
                                {html.escape(p_res['city_name'])}
                              </h2>
                              <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;font-size:1.02rem;color:#3E5B4C;font-weight:600;">
                                <span>Wali Kota: <b style="color:#164E33;">{html.escape(p_res['player_name'])}</b></span>
                                <span>·</span>
                                <span style="display:inline-flex;align-items:center;">
                                  Archetype:&nbsp;{cert_arch_img}<b style="color:{arch['color']};">{arch['name']}</b>
                                </span>
                              </div>
                              <div style="font-size:0.86rem;color:#476656;font-style:italic;margin-top:4px;">
                                "{arch['tagline']}"
                              </div>
                            </div>
                            <div style="display:flex;align-items:center;gap:14px;background:#FFFDF7;border:2px solid {arch['color']};border-radius:18px;padding:12px 18px;box-shadow:0 5px 0 rgba(22,78,51,0.14);">
                              <div style="text-align:center;">
                                <div style="font-family:'Outfit',sans-serif;font-size:0.72rem;color:#3E5B4C;font-weight:800;text-transform:uppercase;letter-spacing:0.05em;">Skor Rata-Rata Akhir</div>
                                <div class="stat-outfit" style="font-size:2.4rem;font-weight:900;color:{arch['color']};line-height:1.05;margin:4px 0;">{p_res['avg_score']:.2f}</div>
                                <div style="font-size:0.75rem;font-weight:700;color:#164E33;display:inline-flex;align-items:center;gap:4px;">Kas Akhir: {icon_img_html('icon_coin.png', 15, 'Koin', 0)}{p_res['coins']} Koin</div>
                              </div>
                              <div class="eco-rating-badge" style="width:62px;height:62px;min-width:62px;background:{cert_grade['bg']};color:{cert_grade['fg']};border-color:#FFFDF7;box-shadow:0 4px 0 rgba(22,78,51,0.22), 0 0 0 2px {cert_grade['ring']};">
                                <span style="font-size:0.55rem;font-weight:800;letter-spacing:0.06em;">GRADE</span>
                                <span style="font-size:1.45rem;font-weight:900;">{cert_grade['grade']}</span>
                              </div>
                              {cert_seal_img}
                            </div>
                          </div>

                          <div class="pillar-grid-4">
                            <div class="pillar-tile" style="background:#FEF3C7;border-color:#EAB308;">
                              <div class="pillar-tile-title" style="color:#B45309;">{e_icon_tag}Energy (E)</div>
                              <div class="pillar-tile-val" style="color:#92400E;">{p_res['E']}</div>
                              <span class="pillar-tile-tier" style="background:#FFFDF7;color:#B45309;">{tiers.get('Energy', {}).get('tier', '-')}</span>
                            </div>
                            <div class="pillar-tile" style="background:#E0F2FE;border-color:#0284C7;">
                              <div class="pillar-tile-title" style="color:#0369A1;">{m_icon_tag}Mobility (M)</div>
                              <div class="pillar-tile-val" style="color:#075985;">{p_res['M']}</div>
                              <span class="pillar-tile-tier" style="background:#FFFDF7;color:#0369A1;">{tiers.get('Mobility', {}).get('tier', '-')}</span>
                            </div>
                            <div class="pillar-tile" style="background:#DCFCE7;border-color:#16A34A;">
                              <div class="pillar-tile-title" style="color:#15803D;">{env_icon_tag}Environment (ENV)</div>
                              <div class="pillar-tile-val" style="color:#14532D;">{p_res['ENV']}</div>
                              <span class="pillar-tile-tier" style="background:#FFFDF7;color:#15803D;">{tiers.get('Environment', {}).get('tier', '-')}</span>
                            </div>
                            <div class="pillar-tile" style="background:#FFE4E6;border-color:#E11D48;">
                              <div class="pillar-tile-title" style="color:#BE123C;">{qol_icon_tag}Quality of Life</div>
                              <div class="pillar-tile-val" style="color:#9F1239;">{p_res['QoL']}</div>
                              <span class="pillar-tile-tier" style="background:#FFFDF7;color:#BE123C;">{tiers.get('Quality of Life', {}).get('tier', '-')}</span>
                            </div>
                          </div>

                          <div style="display:flex;align-items:flex-start;gap:7px;font-size:0.84rem;color:#1E3A2B;line-height:1.5;background:rgba(255,253,247,0.85);border:1px solid #CFE2D4;border-radius:12px;padding:9px 14px;">
                            {icon_img_html('icon_clipboard.png', 18, 'Audit', 0)}<span><b>Dasar Klasifikasi AI Auditor:</b> {html.escape(arch['reason'])}</span>
                          </div>
                        </div>
                        """
                    )

                    nc1, nc2 = st.columns(2, gap="medium")
                    with nc1:
                        with st.container(border=True, key=f"panel_nar_str_{r_idx}"):
                            render_html(f'<div class="diag-card-hdr" style="color:#15803D;">{icon_img_html("icon_city_identity.png", 22, "Infrastruktur", 0)}<span>Kekuatan Infrastruktur Kota</span></div>')
                            st.markdown(nar["strengths"])
                        with st.container(border=True, key=f"panel_nar_vis_{r_idx}"):
                            render_html(f'<div class="diag-card-hdr" style="color:#0284C7;">{icon_img_html("icon_city.png", 22, "Visi 2075", 0)}<span>Visi Tata Kota Masa Depan (Tahun 2075)</span></div>')
                            st.markdown(nar["future_simulation"])

                    with nc2:
                        with st.container(border=True, key=f"panel_nar_chl_{r_idx}"):
                            render_html(f'<div class="diag-card-hdr" style="color:#D97706;">{icon_img_html("icon_card_problem.png", 22, "Krisis", 0)}<span>Evaluasi Krisis &amp; Mitigasi Risiko</span></div>')
                            st.markdown(nar["challenges"])
                        with st.container(border=True, key=f"panel_nar_rec_{r_idx}"):
                            render_html(f'<div class="diag-card-hdr" style="color:#164E33;">{icon_img_html("icon_clipboard.png", 22, "Rekomendasi", 0)}<span>Rekomendasi Tata Ruang Terpadu</span></div>')
                            st.markdown(nar["recommendations"])


# ==============================================================================
# TAB 3: AI GAME MASTER (ECOBOT ROBOT PEMANDU & KONSULTAN TATA KOTA)
# ==============================================================================
def render_tab_game_master() -> None:
    """Merender Tab 3: EcoBot AI Game Master & Ruang Konsultasi Rulebook."""
    render_html(
        """
        <div class="eco-ribbon-wrap">
          <span class="eco-ribbon-header">ECOBOT · AI GAME MASTER</span>
          <span style="font-size:0.78rem;font-weight:700;color:#164E33;background:#FFFDF7;border:1.5px solid #B7D5C4;border-radius:999px;padding:4px 12px;">
            Teman Cek Aturan &amp; Strategi Board Game EcoNova
          </span>
        </div>
        """
    )
    col_gm_side, col_gm_chat = st.columns([3.5, 6.5], gap="large")

    robot_avatar_uri = get_asset_uri("avatar_robot_gm.png")
    robot_persona_avatar = (
        f'<img src="{robot_avatar_uri}" alt="EcoBot" style="width:62px;height:62px;min-width:62px;object-fit:contain;filter:drop-shadow(0 3px 6px rgba(22,78,51,0.22));" />'
        if robot_avatar_uri
        else '<div class="ai-avatar-3d" style="font-size:0.95rem;font-weight:900;color:#FFFFFF;letter-spacing:0.04em;">BOT</div>'
    )
    robot_chat_avatar = (
        f'<img src="{robot_avatar_uri}" alt="EcoBot" style="width:42px;height:42px;min-width:42px;object-fit:contain;filter:drop-shadow(0 2px 4px rgba(22,78,51,0.18));" />'
        if robot_avatar_uri
        else '<div class="chat-avatar-badge chat-avatar-ai" style="font-size:0.8rem;font-weight:900;">BOT</div>'
    )

    with col_gm_side:
        with st.container(border=True, key="panel_gm_sidebar"):
            llm_active = bool(get_groq_api_key())
            engine_badge = (
                "Groq AI Aktif"
                if llm_active
                else "Smart Rulebook Aktif"
            )
            render_html(
                f"""
                <div class="ai-persona-box">
                  <div style="display:flex;align-items:center;gap:12px;">
                    {robot_persona_avatar}
                    <div>
                      <div style="font-family:'Fredoka','Outfit',sans-serif;font-size:1.15rem;font-weight:800;color:#164E33;">
                        EcoBot
                      </div>
                      <div style="font-size:0.78rem;font-weight:800;color:#15803D;margin-top:2px;">
                        <span class="ai-status-dot"></span>{engine_badge}
                      </div>
                    </div>
                  </div>
                  <div style="margin-top:10px;padding-top:9px;border-top:1px dashed #B7D5C4;font-size:0.82rem;color:#1E3A2B;font-weight:600;line-height:1.45;">
                    Robot pemandu <b>EcoNova</b>: tanya cepat soal AP, kombo Tech, diskon Event, atau itungan skor akhir!
                  </div>
                </div>
                """
            )

            render_html(
                f"""
                <div style="display:flex;align-items:center;gap:6px;font-family:'Fredoka','Outfit',sans-serif;font-size:0.96rem;font-weight:800;color:#164E33;margin:6px 0 8px 0;">
                  {icon_img_html('icon_card_skill.png', 18, 'Cepat', 0)}<span>Tanya Cepat (1-Klik)</span>
                </div>
                """
            )
            quick_q = None
            qc1, qc2 = st.columns(2, gap="small")
            if qc1.button("Aturan 3 AP", width="stretch", key="qp_ap"):
                quick_q = "Gimana aturan pakai 3 Action Points (AP) dan pindah ke City Center?"
            if qc2.button("Bonus Koin", width="stretch", key="qp_tb"):
                quick_q = "Gimana cara ngitung Bonus Koin per 20 koin dan urutan Tie-Breaker?"

            qc3, qc4 = st.columns(2, gap="small")
            if qc3.button("Tech & Skill", width="stretch", key="qp_tech"):
                quick_q = "Apa aja efek Permanent Tech T1-T5 dan Skill S1-S5?"
            if qc4.button("Solusi Krisis", width="stretch", key="qp_prob"):
                quick_q = "Gimana cara beresin Problem Card pakai koin vs Tech/Skill?"

            qc5, qc6 = st.columns(2, gap="small")
            if qc5.button("13 Event", width="stretch", key="qp_ev"):
                quick_q = "Apa aja efek Event Card Round 1 sampai 13 dan diskon distriknya?"
            if qc6.button("Panduan Skor", width="stretch", key="qp_strat"):
                quick_q = "Tips biar kota bisa tembus archetype Balanced Sustainable Metropolis (>=75)?"

            st.markdown("---")
            render_html(
                f"""
                <div style="display:flex;align-items:center;gap:6px;font-family:'Fredoka','Outfit',sans-serif;font-size:0.96rem;font-weight:800;color:#164E33;margin:4px 0 8px 0;">
                  {icon_img_html('icon_clipboard.png', 18, 'Rulebook', 0)}<span>Ringkasan Cepat Rulebook</span>
                </div>
                <div class="rule-tile" style="border-left-color:#16A34A;display:flex;align-items:flex-start;gap:8px;">
                  {icon_img_html('icon_card_project.png', 18, 'AP', 0)}<span><b>3 AP di Papan:</b> Pindah distrik = <b>1 AP</b> · Beli Proyek/Tech = <b>1 AP</b> · Krisis via Tech = <b>2 AP</b> / Koin = <b>1 AP</b>.</span>
                </div>
                <div class="rule-tile" style="border-left-color:#D97706;display:flex;align-items:flex-start;gap:8px;">
                  {icon_img_html('icon_coin.png', 18, 'Koin', 0)}<span><b>City Center &amp; Bonus:</b> Tiba di City Center = <b>+3 Koin</b> (1x/ronde). Tiap <b>20 Koin</b> di akhir = <b>+5 ke 4 pilar</b>.</span>
                </div>
                <div class="rule-tile" style="border-left-color:#0284C7;display:flex;align-items:flex-start;gap:8px;">
                  {icon_img_html('icon_card_tech.png', 18, 'Tech', 0)}<span><b>Tech vs Skill:</b> Tech T1–T5 awet &amp; dipakai 1x/ronde; Skill S1–S5 sekali pakai lalu hilang.</span>
                </div>
                <div class="rule-tile" style="border-left-color:#E11D48;display:flex;align-items:flex-start;gap:8px;">
                  {icon_img_html('icon_scale.png', 18, 'Tie-Breaker', 0)}<span><b>Tie-Breaker:</b> Average Score → Jumlah Proyek → Jumlah Tech → Sisa Koin.</span>
                </div>
                """
            )

            act_c1, act_c2 = st.columns(2)
            with act_c1:
                if st.button("Reset Chat", width="stretch", key="btn_clear_chat"):
                    st.session_state.chat_history = [
                        {"role": "assistant", "content": WELCOME_CHAT_MESSAGE}
                    ]
                    st.rerun()
            with act_c2:
                st.caption(f"{len(st.session_state.chat_history)} pesan")

    with col_gm_chat:
        with st.container(border=True, key="panel_gm_chat_main"):
            render_html(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px;padding-bottom:10px;border-bottom:1.5px solid #CFE2D4;">
                  <div>
                    <div style="font-family:'Fredoka','Outfit',sans-serif;font-size:1.2rem;font-weight:800;color:#164E33;">
                      Obrolan Bareng EcoBot
                    </div>
                    <div style="font-size:0.8rem;color:#3E5B4C;font-weight:600;">
                      Tanya singkat aturan main, kode kartu (P001–P120, T1–T5, S1–S5, PR01–PR20), atau tips skor
                    </div>
                  </div>
                  <span class="eco-pill eco-pill-env">{icon_img_html('icon_check.png', 15, 'Verified', 2)}Sesuai Rulebook</span>
                </div>
                """
            )

            chat_stream = st.container(height=540, border=True, key="panel_gm_stream")
            with chat_stream:
                for msg in st.session_state.chat_history:
                    role = msg["role"]
                    content_html = format_chat_markdown_to_html(msg["content"])

                    if role == "user":
                        render_html(
                            f"""
                            <div class="chat-row-user">
                              <div class="chat-bubble-user">
                                <div class="chat-sender-tag" style="color:#DCFCE7;justify-content:flex-end;">
                                  <span>ANDA (WALI KOTA)</span>
                                </div>
                                <div>{content_html}</div>
                              </div>
                              <div class="chat-avatar-badge chat-avatar-user" style="font-size:0.85rem;font-weight:900;">W</div>
                            </div>
                            """
                        )
                    else:
                        render_html(
                            f"""
                            <div class="chat-row-ai">
                              {robot_chat_avatar}
                              <div class="chat-bubble-ai">
                                <div class="chat-sender-tag" style="color:#164E33;">
                                  <span>ECOBOT · AI GAME MASTER</span>
                                </div>
                                <div>{content_html}</div>
                              </div>
                            </div>
                            """
                        )

            user_input = st.chat_input(
                "Tanya EcoBot (misal: syarat beresin PR08 atau efek P015)...",
                key="chat_input_gm",
            )
            active_query = quick_q or user_input

            if active_query:
                st.session_state.chat_history.append({"role": "user", "content": active_query})
                answer = query_llm_game_master(active_query, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()