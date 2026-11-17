"""
ui_components.py — Komponen UI Modular Bright Glass 3D Solarpunk
Berisi helper rendering HTML/Markdown, Hero Banner, Tab 1 Live Tracker,
Tab 2 Final Audit & Sertifikat 2075, dan Tab 3 AI Game Master.
"""

import html
import re
from typing import Any, Dict, List, Optional

import streamlit as st

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
    TECH_ACTION_META,
    WELCOME_CHAT_MESSAGE,
    callback_activate_tech,
    callback_event_picker_changed,
    callback_next_round,
    callback_prev_round,
    callback_reset_game,
    callback_reset_manual_points,
    callback_set_active_player,
    callback_sync_city,
    callback_sync_coins,
    callback_sync_manual_points,
    callback_sync_name,
    callback_sync_problems,
    callback_sync_projects,
    callback_sync_skills,
    callback_sync_techs,
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


# ==============================================================================
# PILIHAN & FORMATTER LABEL KARTU (CLEAN DISPLAY NAMES)
# ==============================================================================
project_id_options = list(PROJECT_BY_ID.keys())
tech_code_options = list(PERMANENT_TECH_BY_CODE.keys())
skill_code_options = list(SKILL_BY_CODE.keys())
problem_id_options = list(PROBLEM_BY_ID.keys())

MARKET_DISCOUNT_BADGES: Dict[str, str] = {
    "EV03": "🏷️ DISKON PASAR: -2 Koin Project Card di Energy District",
    "EV05": "🏷️ DISKON PASAR: -2 Koin Tech Card di City Center",
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


# ==============================================================================
# UI RENDERING HELPERS
# ==============================================================================
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


def build_aspect_progress_html(label: str, icon: str, val: int, delta: int, color: str) -> str:
    """Membangun HTML progress bar 3D glossy dengan indikator delta dan kontras tajam."""
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

    return f"""
    <div class="eco-prog-wrap">
      <div class="eco-prog-hdr">
        <span style="display:flex;align-items:center;gap:7px;font-family:'Outfit',sans-serif;color:#0F2A1D;">
          <span style="background:{color}22;color:{text_color};font-size:0.75rem;padding:2px 7px;border-radius:6px;font-weight:800;border:1px solid {color}44;">{icon}</span> <b>{label}</b>
        </span>
        <span style="font-family:'Outfit',sans-serif;">
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


def format_chat_markdown_to_html(md_text: str) -> str:
    """Mengonversi Markdown sederhana dari jawaban AI menjadi HTML bersih."""
    escaped = html.escape(md_text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b style='color:#0F2A1D;font-weight:700;'>\1</b>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(
        r"(?m)^###\s+(.+)$",
        r"<div style='font-family:\"Outfit\",sans-serif;font-size:1.06rem;font-weight:700;color:#047857;margin:12px 0 6px 0;border-left:3.5px solid #10B981;padding-left:10px;'>\1</div>",
        escaped,
    )
    escaped = re.sub(
        r"(?m)^-\s+(.+)$",
        r"<div style='margin:4px 0 4px 8px;color:#1E3A2B;display:flex;align-items:flex-start;gap:6px;'><span style='color:#06B6D4;'>•</span><span>\1</span></div>",
        escaped,
    )
    escaped = escaped.replace("\n", "<br>")
    return escaped


def render_hero_banner() -> None:
    """Merender Hero Banner bergaya EcoNova Official Poster (Tactile Eco-Solarpunk Command Deck)."""
    render_html(
        """
        <div class="eco-hero-banner">
          <div class="eco-hero-top">
            <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
              <div class="eco-ribbon-header" style="font-size:0.74rem;padding:5px 15px;">ECONOVA · AI AUDITOR</div>
              <h1 class="eco-hero-title">
                EcoNova <span style="color:#16A34A;">Sustainable City</span> <span style="color:#0284C7;">Planner</span>
              </h1>
              <span style="color:#3E5B4C;font-size:0.80rem;font-weight:700;border-left:2px solid #B7D5C4;padding-left:10px;">
                Tactile Tabletop HUD &amp; City Performance Evaluator
              </span>
            </div>
            <div class="eco-legend-row">
              <span class="eco-legend-pill pill-env"><b>ENV</b> Environment</span>
              <span class="eco-legend-pill pill-m"><b>M</b> Mobility</span>
              <span class="eco-legend-pill pill-e"><b>E</b> Energy</span>
              <span class="eco-legend-pill pill-qol"><b>QoL</b> Quality of Life</span>
            </div>
          </div>
        </div>
        """
    )


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

    # --------------------------------------------------------------------------
    # TOP TELEMETRY BAR: RONDE, GLOBAL EVENT AKTIF & ACTIVE TURN TRACKER
    # --------------------------------------------------------------------------
    render_html(
        """
        <div class="eco-ribbon-wrap">
          <span class="eco-ribbon-header">TELEMETRI RONDE &amp; KENDALI MEJA</span>
          <span style="font-size:0.78rem;font-weight:700;color:#164E33;background:#FFFDF7;border:1.5px solid #B7D5C4;border-radius:999px;padding:4px 12px;">
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
                  <div style="font-size:0.72rem;color:#4A5D52;font-weight:700;">
                    {'🏁 Ronde Terakhir (Evaluasi Akhir)' if curr_round == 13 else f'Fase Pembangunan Kota · Progres {int((curr_round / 13) * 100)}%'}
                  </div>
                </div>
                """
            )

            nav_c1, nav_c2 = st.columns(2, gap="small")
            with nav_c1:
                st.button(
                    "⬅️ Prev",
                    key="btn_prev_round",
                    disabled=(curr_round <= 1),
                    width="stretch",
                    on_click=callback_prev_round,
                    help="Kembali ke ronde sebelumnya dan rollback koin serta efek event ronde terakhir.",
                )
            with nav_c2:
                st.button(
                    "Next Ronde ➡️",
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
                    f"<div style='margin-top:7px;padding:5px 10px;border-radius:10px;background:linear-gradient(135deg,rgba(245,158,11,0.18),rgba(251,191,36,0.12));border:1.5px solid rgba(217,119,6,0.5);color:#92400E;font-size:0.74rem;font-weight:800;'>{discount_badge}</div>"
                    if discount_badge
                    else ""
                )
                render_html(
                    f"""
                    <div style="background:linear-gradient(135deg,rgba(255,255,255,0.97) 0%,rgba(224,242,254,0.68) 100%);border:1.5px solid rgba(2,132,199,0.55);border-left:5px solid #0284C7;border-radius:14px;padding:11px 14px;box-shadow:0 6px 18px rgba(2,132,199,0.12);margin-top:4px;">
                      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                        <span class="eco-pill eco-pill-m" style="font-size:0.74rem;">
                          ⚡ {active_event['name']}
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
                    """
                    <div style="background:rgba(255,255,255,0.58);backdrop-filter:blur(12px);border:1.5px dashed rgba(148,163,184,0.58);border-radius:14px;padding:12px 14px;margin-top:4px;box-shadow:inset 0 1px 4px rgba(15,42,29,0.03);display:flex;align-items:center;gap:10px;">
                      <span style="background:rgba(148,163,184,0.16);color:#475569;border:1px solid rgba(148,163,184,0.35);border-radius:10px;padding:5px 9px;font-size:0.72rem;font-weight:800;letter-spacing:0.04em;flex-shrink:0;">
                        🕊️ STANDBY
                      </span>
                      <span style="color:#64748B;font-size:0.77rem;line-height:1.35;font-weight:600;">
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
                "🛠️ Enable Nilai Poin Manual",
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

        # Active Turn Selector Bar (Segmented Pill Switcher per Faksi)
        act_faction = FACTION_THEMES[active_player_id]
        act_pl = st.session_state.players[active_player_id]
        with st.container(key="turn_switcher_shell"):
            turn_lbl_col, t_btn1, t_btn2, t_btn3, t_btn4 = st.columns([3.2, 2.2, 2.2, 2.2, 2.2], gap="small")
            with turn_lbl_col:
                render_html(
                    f"""
                    <div style="display:flex;align-items:center;gap:8px;padding:6px 12px;background:rgba(255,255,255,0.92);border:1.5px solid {act_faction['border']};border-radius:999px;box-shadow:0 2px 8px rgba(15,42,29,0.04);">
                      <span style="width:9px;height:9px;border-radius:50%;background:{act_faction['accent']};display:inline-block;box-shadow:0 0 8px {act_faction['accent']};flex-shrink:0;"></span>
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
            """
            <div style="background:linear-gradient(90deg, rgba(2,132,199,0.12), rgba(5,150,105,0.12));border:1.5px solid rgba(2,132,199,0.35);border-radius:12px;padding:8px 14px;margin:8px 0 12px 0;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 10px rgba(2,132,199,0.06);">
              <span style="font-size:0.82rem;font-weight:700;color:#0F2A1D;">
                🛠️ <b>Mode Penyesuaian Poin Manual Aktif:</b> Masukkan penambahan atau pengurangan poin (M, E, ENV, QoL) pada masing-masing kartu pemain di bawah.
              </span>
              <span style="font-size:0.75rem;padding:3px 10px;border-radius:8px;background:rgba(2,132,199,0.2);color:#0284C7;font-weight:800;letter-spacing:0.02em;">
                MANUAL POINTS ON
              </span>
            </div>
            """
        )

    # --------------------------------------------------------------------------
    # 4 LIVE PLAYER WHITE GLASS CARDS (GRID BERSAMA 4 KOLOM)
    # --------------------------------------------------------------------------
    p_cols = st.columns(4, gap="medium")
    live_audits_tab1 = []

    for idx in range(4):
        p_id = idx + 1
        pl = st.session_state.players[p_id]
        faction = FACTION_THEMES[p_id]
        is_active_turn = (p_id == active_player_id)

        with p_cols[idx]:
            with st.container(border=True, key=f"panel_tracker_p{p_id}"):
                # Live Scoring Calculation: accumulated_event_coins=0 agar tidak terjadi penghitungan ganda
                # karena koin Event ronde lalu sudah dikomit ke pl["coins"].
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
                live_audits_tab1.append(live_audit)
                arch = live_audit["archetype"]

                # ==============================================================
                # DISPLAY ZONE (SELALU TERLIHAT & RINGKAS DI ATAS KARTU)
                # ==============================================================
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

                render_html(
                    f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:8px;">
                      <span style="background:{faction['badge_bg']};color:{faction['dark']};border:1px solid {faction['border']};font-family:'Outfit',sans-serif;font-size:0.72rem;font-weight:800;padding:3px 10px;border-radius:999px;letter-spacing:0.03em;">
                        {faction['short']}
                      </span>
                      {turn_badge_html}
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px;">
                      <div style="min-width:0;">
                        <div style="font-family:'Fredoka','Outfit',sans-serif;font-size:1.18rem;font-weight:800;color:#0F2A1D;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                          {safe_city}
                        </div>
                        <div style="font-size:0.76rem;font-weight:600;color:#4A5D52;margin-top:2px;">
                          Wali Kota: <b style="color:{faction['dark']};">{safe_name}</b>
                        </div>
                      </div>
                      <span style="flex-shrink:0;background:rgba(245,158,11,0.16);border:1px solid rgba(217,119,6,0.45);color:#B45309;font-family:'Outfit',sans-serif;font-size:0.75rem;font-weight:800;padding:4px 9px;border-radius:999px;">
                        🪙 {effective_coins} Koin{ev_coin_tag}
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
                          <div style="font-size:0.74rem;font-weight:700;color:{arch['color']};margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{arch['name']}</div>
                        </div>
                        <div class="eco-rating-badge" title="Overall Rating: {rating['grade']} ({rating['label']})" style="background:{rating['bg']};color:{rating['fg']};border-color:#FFFDF7;box-shadow:0 4px 0 rgba(22,78,51,0.22), 0 0 0 2px {rating['ring']};">
                          <span style="font-size:0.52rem;font-weight:800;letter-spacing:0.06em;opacity:0.92;text-transform:uppercase;">GRADE</span>
                          <span style="font-size:1.32rem;font-weight:900;margin-top:1px;">{rating['grade']}</span>
                        </div>
                      </div>
                      <div style="margin-top:7px;padding-top:6px;border-top:1px dashed rgba(22,78,51,0.16);font-size:0.72rem;font-weight:700;color:#164E33;text-align:center;">
                        🏗️ {len(pl['projects'])} Proyek &nbsp;|&nbsp; ⚡ {len(pl['techs'])} Tech &nbsp;|&nbsp; ⚠️ {len(pl['problems'])} Krisis
                      </div>
                    </div>
                    """
                )

                # Telemetry Bar 4 Aspek (M, E, ENV, QoL) sesuai skema warna poster EcoNova
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
                    build_aspect_progress_html("Quality of Life (QoL)", "QoL", live_audit["QoL"], live_audit["delta_QoL"], "#E11D48"),
                    unsafe_allow_html=True,
                )

                # Indikator Imunitas S5, Event Live & Akumulasi Bonus
                if pl.get("immune_this_round", False):
                    render_html(
                        """
                        <div style="font-size:0.72rem;color:#047857;background:rgba(16,185,129,0.15);border:1px solid #10B981;border-radius:8px;padding:4px 8px;margin-top:4px;font-weight:700;">
                          🛡️ S5 Cyber Shield Aktif: Kebal Semua Penalti Event Ronde Ini
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

                # ==============================================================
                # TOMBOL AKSI CEPAT (TEPAT DI ATAS EXPANDER — 1 LANGKAH KLIK)
                # ==============================================================
                if pl["techs"]:
                    render_html(
                        """
                        <div style="background:rgba(255,255,255,0.9);border:1.5px solid rgba(2,132,199,0.3);border-radius:10px;padding:5px 10px;margin-top:6px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="font-size:0.76rem;color:#0F2A1D;">Aksi Tech Card (Tetap Dimiliki)</b>
                            <span style="font-size:0.66rem;padding:2px 6px;border-radius:6px;background:rgba(2,132,199,0.12);color:#0284C7;font-weight:700;">1x / Ronde</span>
                          </div>
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
                                    f"⚡ {tc} [Sudah Dipakai]",
                                    key=f"btn_tech_{p_id}_{tc}",
                                    disabled=True,
                                    width="stretch",
                                    help=f"{tc} ({t_clean}) dipakai ronde ini (AP dihitung fisik di meja) & kartu tetap dimiliki. Reset di ronde berikutnya.",
                                )
                            else:
                                st.button(
                                    f"⚡ Pakai {t_clean}",
                                    key=f"btn_tech_{p_id}_{tc}",
                                    disabled=False,
                                    width="stretch",
                                    help=f"Aktifkan {t_clean} ronde ini{prob_hint}. Dapat dipakai tiap ronde (AP dihitung fisik di meja) & kartu tetap dimiliki.",
                                    on_click=callback_activate_tech,
                                    args=(p_id, tc),
                                )

                if pl["skills"]:
                    render_html(
                        """
                        <div style="background:rgba(255,255,255,0.9);border:1.5px solid rgba(124,58,237,0.3);border-radius:10px;padding:5px 10px;margin-top:6px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="font-size:0.76rem;color:#0F2A1D;">Pakai Skill (Sekali Pakai / Hilang)</b>
                            <span style="font-size:0.66rem;padding:2px 6px;border-radius:6px;background:rgba(124,58,237,0.12);color:#7C3AED;font-weight:700;">Consumed</span>
                          </div>
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
                                "✨ Pakai S1 (Hapus Problem)",
                                key=f"btn_use_s1_{p_id}",
                                width="stretch",
                                type="primary",
                                on_click=callback_use_s1,
                                args=(p_id, s1_target),
                                help="Hapus Problem Card terpilih dan kartu S1 langsung terhapus (consumed).",
                            )
                        else:
                            st.caption("Pemain tidak memiliki Problem Card. Pakai S1 untuk Dana Darurat (+2 Semua Aspek):")
                            st.button(
                                "✨ Pakai S1 (Dana Darurat +2 All)",
                                key=f"btn_use_s1_fb_{p_id}",
                                width="stretch",
                                on_click=callback_use_s1_fallback,
                                args=(p_id,),
                                help="Aktifkan dana darurat +2 semua aspek dan kartu S1 langsung terhapus.",
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
                                        f"✨ Pakai {s_clean} (Kebal Event)",
                                        key=f"btn_use_s5_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s5,
                                        args=(p_id,),
                                        help="Aktifkan imunitas penalti Event ronde ini & hapus kartu S5.",
                                    )
                                elif sc == "S2":
                                    st.button(
                                        f"✨ Pakai {s_clean} (+5 ENV)",
                                        key=f"btn_use_s2_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s2,
                                        args=(p_id,),
                                        help="Tambah +5 ENV & hapus kartu S2.",
                                    )
                                elif sc == "S3":
                                    st.button(
                                        f"✨ Pakai {s_clean} (+5 M)",
                                        key=f"btn_use_s3_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s3,
                                        args=(p_id,),
                                        help="Tambah +5 Mobility & hapus kartu S3.",
                                    )
                                elif sc == "S4":
                                    st.button(
                                        f"✨ Pakai {s_clean} (+5 QoL)",
                                        key=f"btn_use_s4_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s4,
                                        args=(p_id,),
                                        help="Tambah +5 Quality of Life & hapus kartu S4.",
                                    )

                                # Opsi cepat pakai Skill untuk mengamankan Problem Card yang sesuai
                                for mp_id in matching_probs:
                                    mp_name = get_card_clean_name(mp_id)
                                    st.button(
                                        f"🛡️ Pakai {sc} (Amankan {mp_id})",
                                        key=f"btn_solve_{sc}_{mp_id}_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_skill_solve_problem,
                                        args=(p_id, sc, mp_id),
                                        help=f"Gunakan {s_clean} untuk mengamankan [{mp_name}] dan hapus kartu {sc}.",
                                    )

                # Panel Penyesuaian Nilai Poin Manual (Tampil di atas expander jika Enable aktif)
                cur_mp = pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                if st.session_state.get("enable_manual_points", False):
                    render_html(
                        """
                        <div style="background:rgba(255,255,255,0.92);border:1.5px solid rgba(2,132,199,0.3);border-radius:10px;padding:5px 10px;margin-top:6px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="font-size:0.76rem;color:#0F2A1D;">🛠️ Tambah Nilai Poin Manual</b>
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
                            help="Penyesuaian manual nilai Mobility (+/-)",
                        )
                        st.number_input(
                            "Tambah ENV:",
                            min_value=-50,
                            max_value=50,
                            step=1,
                            key=f"widget_man_ENV_{p_id}",
                            on_change=callback_sync_manual_points,
                            args=(p_id, "ENV"),
                            help="Penyesuaian manual nilai Environment (+/-)",
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
                            help="Penyesuaian manual nilai Energy (+/-)",
                        )
                        st.number_input(
                            "Tambah QoL:",
                            min_value=-50,
                            max_value=50,
                            step=1,
                            key=f"widget_man_QoL_{p_id}",
                            on_change=callback_sync_manual_points,
                            args=(p_id, "QoL"),
                            help="Penyesuaian manual nilai Quality of Life (+/-)",
                        )
                    if any(cur_mp.values()):
                        st.button(
                            "Reset Poin Manual",
                            key=f"btn_reset_man_{p_id}",
                            width="stretch",
                            on_click=callback_reset_manual_points,
                            args=(p_id,),
                            help="Kembalikan penyesuaian poin manual pemain ini ke 0.",
                        )
                elif any(cur_mp.values()):
                    render_html(
                        f"""
                        <div style="font-size:0.72rem;color:#0284C7;background:rgba(2,132,199,0.1);border:1px solid rgba(2,132,199,0.3);border-radius:8px;padding:4px 8px;margin-top:4px;">
                          <b>Poin Manual Aktif:</b> M:{cur_mp['M']:+d} | E:{cur_mp['E']:+d} | ENV:{cur_mp['ENV']:+d} | QoL:{cur_mp['QoL']:+d}
                        </div>
                        """
                    )

                # ==============================================================
                # INPUT ZONE (ANTI-VERTICAL BLOAT — TERBUNGKUS EXPANDER)
                # ==============================================================
                with st.expander("🎛️ Kelola Kartu & Kas", expanded=(p_id == active_player_id)):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.text_input(
                            "Wali Kota:",
                            key=f"widget_name_{p_id}",
                            on_change=callback_sync_name,
                            args=(p_id,),
                        )
                    with c2:
                        st.text_input(
                            "Nama Kota:",
                            key=f"widget_city_{p_id}",
                            on_change=callback_sync_city,
                            args=(p_id,),
                        )

                    st.multiselect(
                        "Proyek Dibangun (120):",
                        options=project_id_options,
                        format_func=format_project_label,
                        key=f"widget_projects_{p_id}",
                        on_change=callback_sync_projects,
                        args=(p_id,),
                        help="Pilih kartu proyek yang telah dibangun di papan kota fisik.",
                    )

                    if pl["projects"]:
                        p_badges_html = '<div style="display:flex;flex-wrap:wrap;gap:5px;margin:4px 0 8px 0;">'
                        for pid in pl["projects"]:
                            p_card = PROJECT_BY_ID.get(pid, {})
                            theme = get_card_color_theme(pid)
                            clean_name = get_card_clean_name(pid)
                            dist_name = p_card.get("district", "Proyek")
                            badge_bg = theme.get("badge_bg", theme.get("bg", "rgba(255, 255, 255, 0.85)"))
                            badge_border = theme.get("border_glass", theme.get("border", "rgba(5, 150, 105, 0.35)"))
                            badge_accent = theme.get("accent", "#059669")
                            p_badges_html += f"""
                            <div style="background:{badge_bg};border:1.5px solid {badge_border};border-radius:9px;padding:3px 8px;box-shadow:0 2px 6px rgba(0,0,0,0.04);display:inline-flex;align-items:center;gap:5px;">
                              <span style="font-size:0.65rem;font-weight:800;color:{badge_accent};text-transform:uppercase;">{dist_name}</span>
                              <span style="font-size:0.74rem;font-weight:700;color:#0F2A1D;">{clean_name}</span>
                            </div>
                            """
                        p_badges_html += "</div>"
                        render_html(p_badges_html)

                    st.multiselect(
                        "Permanent Tech Dimiliki (T1–T5):",
                        options=tech_code_options,
                        format_func=format_tech_label,
                        key=f"widget_techs_{p_id}",
                        on_change=callback_sync_techs,
                        args=(p_id,),
                        help="Teknologi permanen yang dimiliki. Tetap ada di area pemain & bisa diaktifkan 1x per ronde.",
                    )

                    st.multiselect(
                        "Skill Card di Tangan (S1–S5):",
                        options=skill_code_options,
                        format_func=format_skill_label,
                        key=f"widget_skills_{p_id}",
                        on_change=callback_sync_skills,
                        args=(p_id,),
                        help="Kartu skill sekali pakai. Saat tombol aksi ditekan, kartu langsung terhapus (consumed).",
                    )

                    st.multiselect(
                        "Krisis Gagal (Penalti):",
                        options=problem_id_options,
                        format_func=format_problem_label,
                        key=f"widget_problems_{p_id}",
                        on_change=callback_sync_problems,
                        args=(p_id,),
                        help="Problem card yang gagal diselesaikan hingga batas waktu.",
                    )

                    if pl["problems"]:
                        prob_badges_html = '<div style="display:flex;flex-wrap:wrap;gap:5px;margin:4px 0 8px 0;">'
                        for pid in pl["problems"]:
                            p_obj = PROBLEM_BY_ID.get(pid, {})
                            p_name = get_card_clean_name(pid)
                            pen = p_obj.get("pen_str", "")
                            prob_badges_html += f"""
                            <div style="background:rgba(239,68,68,0.12);border:1.5px solid rgba(239,68,68,0.4);border-radius:9px;padding:3px 8px;box-shadow:0 2px 6px rgba(220,38,38,0.06);display:inline-flex;align-items:center;gap:5px;">
                              <span style="font-size:0.65rem;font-weight:800;color:#DC2626;">KRISIS</span>
                              <span style="font-size:0.74rem;font-weight:700;color:#7F1D1D;">{p_name}</span>
                              <span style="font-size:0.68rem;color:#B91C1C;font-weight:600;">({pen})</span>
                            </div>
                            """
                        prob_badges_html += "</div>"
                        render_html(prob_badges_html)

                    st.number_input(
                        "Kas Koin Saat Ini:",
                        min_value=0,
                        max_value=300,
                        step=1,
                        key=f"widget_coins_{p_id}",
                        on_change=callback_sync_coins,
                        args=(p_id,),
                        help="Kas koin pemain. Tiap 20 koin penuh menghasilkan +5 bonus di akhir permainan.",
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
    # FOOTER KONTROL TAB 1: KUNCI SIMULASI & PROSES FINAL AUDIT
    # --------------------------------------------------------------------------
    st.write("")
    f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
    with f_col2:
        if st.button(
            "🏁 Kunci Simulasi & Buka Final Audit",
            type="primary",
            width="stretch",
            key="btn_lock_and_audit",
        ):
            st.session_state.audit_triggered = True
            st.toast("Simulasi Berhasil Dikunci! Silakan periksa Tab 2 untuk Laporan Audit Akhir dan Leaderboard.")
            st.rerun()


# ==============================================================================
# TAB 2: FINAL AI AUDIT (STRICT LAZY LOADING ON-CLICK, TANPA MAKET 3D)
# ==============================================================================
def render_tab_audit() -> None:
    """Merender Tab 2: Final AI Audit, Leaderboard, Radar & Sertifikat Kota 2075."""
    audit_mode_options = [
        "Gunakan Riwayat Event Ronde Aktual",
        "Gunakan Simulasi Otomatis 13 Event",
    ]

    if not st.session_state.get("audit_triggered", False):
        render_html(
            """
            <div style="background:#FFFDF7;border:2px solid #B7D5C4;border-radius:22px;padding:30px;text-align:center;box-shadow:0 6px 0 rgba(22,78,51,0.14), 0 12px 24px rgba(0,0,0,0.06);margin:14px 0 18px 0;">
              <div class="eco-ribbon-header" style="margin-bottom:12px;">
                FINAL AI AUDIT &amp; SERTIFIKAT 2075
              </div>
              <h2 style="font-family:'Fredoka','Outfit',sans-serif;font-size:2.2rem;color:#164E33;margin:0 0 10px 0;font-weight:800;">
                Evaluasi Performa Kota &amp; Sertifikasi EcoNova 2075
              </h2>
              <div style="max-width:760px;margin:0 auto 14px auto;color:#3E5B4C;font-size:0.96rem;line-height:1.6;">
                Setelah permainan berlangsung di papan fisik, pilih mode evaluasi Event di bawah lalu jalankan audit untuk
                menghitung bonus tier sisa koin, menentukan peringkat dan tie-breaker resmi, serta menerbitkan Sertifikat Penghargaan Tata Kota 2075.
              </div>
            </div>
            """
        )

        with st.container(border=True, key="panel_audit_mode_pre"):
            st.radio(
                "Sumber Evaluasi Event Card untuk Final Audit:",
                options=audit_mode_options,
                horizontal=True,
                key="audit_event_mode",
                help="Riwayat Event Ronde Aktual memakai akumulasi ronde yang dimainkan di Tab 1 (bebas duplikasi koin). Simulasi Otomatis 13 Event mengevaluasi seluruh EV01–EV13 secara teoretis.",
            )

        with st.container(border=True, key="panel_audit_coins_pre"):
            st.markdown("#### Verifikasi Kas Koin Akhir 4 Pemain")
            st.caption("Sesuai Rulebook Bab VI.2: Tiap 20 koin penuh memberikan bonus +5 ke keempat pilar kota (M, E, ENV, QoL).")
            c_cols = st.columns(4, gap="medium")
            for idx in range(4):
                p_id = idx + 1
                pl = st.session_state.players[p_id]
                curr_c = int(pl["coins"])
                b_pts = calculate_coin_bonus(curr_c)
                next_tier = ((curr_c // 20) + 1) * 20
                need = next_tier - curr_c
                with c_cols[idx]:
                    render_html(
                        f"""
                        <div style="background:linear-gradient(135deg,rgba(245,158,11,0.12) 0%,rgba(255,255,255,0.95) 100%);border:1px solid rgba(245,158,11,0.35);border-radius:14px;padding:12px;text-align:center;">
                          <div style="font-size:0.82rem;color:#4A5D52;font-weight:700;">{pl['name']}</div>
                          <div style="font-family:'Outfit',sans-serif;font-size:2.0rem;font-weight:900;color:#B45309;line-height:1.2;margin:4px 0;">
                            {curr_c} Koin
                          </div>
                          <div style="font-size:0.82rem;font-weight:700;color:#047857;">
                            Bonus Akhir: +{b_pts} ke 4 Aspek
                          </div>
                          <div style="font-size:0.72rem;color:#64748B;margin-top:2px;">
                            +{need} Koin menuju tier +{b_pts + 5}
                          </div>
                        </div>
                        """
                    )

        st.write("")
        exec_c1, exec_c2, exec_c3 = st.columns([1, 2, 1])
        with exec_c2:
            if st.button(
                "🚀 JALANKAN AUDIT SIMULASI KOTA MASA DEPAN",
                type="primary",
                width="stretch",
                key="btn_run_audit_strict_lazy",
            ):
                st.session_state.audit_triggered = True
                st.toast("Audit Berhasil Dieksekusi! Menghasilkan Leaderboard dan Sertifikat 2075...")
                st.rerun()

    else:
        top_ctrl_c1, top_ctrl_c2 = st.columns([7, 3])
        with top_ctrl_c1:
            render_html(
                """
                <div class="eco-ribbon-wrap" style="margin:0;">
                  <span class="eco-ribbon-header">FINAL AI AUDIT &amp; SERTIFIKAT 2075</span>
                </div>
                """
            )
        with top_ctrl_c2:
            if st.button(
                "🔄 Buka Kunci / Kembali ke Mode Live Tracker",
                width="stretch",
                key="btn_unlock_audit",
            ):
                st.session_state.audit_triggered = False
                st.rerun()

        use_auto_13 = st.radio(
            "Mode Evaluasi Event Audit:",
            options=audit_mode_options,
            horizontal=True,
            key="audit_event_mode",
            help="Pilih riwayat ronde aktual dari Tab 1 atau simulasi penuh 13 Global Event Rulebook.",
        ) == "Gunakan Simulasi Otomatis 13 Event"

        active_ev_for_audit = st.session_state.get("selected_event_id")

        final_player_audits = []
        for idx in range(4):
            p_id = idx + 1
            pl = st.session_state.players[p_id]
            if use_auto_13:
                # Kurangi committed_event_coins agar simulasi 13 Event (+7 koin) tidak menghitung ganda koin Event Tab 1
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
                # Gunakan riwayat aktual: koin Event ronde lalu sudah ada di pl["coins"] (accumulated_event_coins=0)
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

        with st.container(border=True, key="panel_audit_events_auto"):
            ev_hdr1, ev_hdr2 = st.columns([7, 3])
            with ev_hdr1:
                if use_auto_13:
                    st.markdown("#### Evaluasi Otomatis 13 Global Event (Round 1–13)")
                    st.caption("Engine EcoNova menghitung dampak kumulatif seluruh 13 Event Card Rulebook berdasarkan proyek dan teknologi tiap pemain.")
                else:
                    played_cnt = len(st.session_state.get("used_events", []))
                    st.markdown(f"#### Ringkasan Dampak Event Ronde Aktual ({played_cnt} Ronde Terkunci)")
                    st.caption("Menggunakan akumulasi dampak Event dari ronde yang benar-benar dimainkan di Tab 1 tanpa duplikasi poin maupun koin.")
            with ev_hdr2:
                badge_txt = "Auto-Evaluated 13 Events" if use_auto_13 else "Actual Round History"
                render_html(f"<div style='text-align:right;padding-top:8px;'><span class='eco-pill eco-pill-env'>{badge_txt}</span></div>")

            ev_cols = st.columns(4, gap="medium")
            for idx in range(4):
                aud = final_player_audits[idx]
                pl = st.session_state.players[idx + 1]
                with ev_cols[idx]:
                    ev_d = aud.get("event_delta", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                    ev_c = aud.get("event_coins", 0) if use_auto_13 else int(pl.get("committed_event_coins", 0)) + int(aud.get("live_event_coins", 0))
                    render_html(
                        f"""
                        <div style="background:rgba(255,255,255,0.85);border:1px solid #D6E4DA;border-radius:12px;padding:10px;font-size:0.78rem;">
                          <b style="color:#0F2A1D;">{aud['player_name']}</b> ({aud['city_name']})<br/>
                          <span style="color:#0369A1;font-weight:600;">Koin Event Terkumpul: +{ev_c}</span><br/>
                          <span style="color:#15803D;font-weight:600;">Dampak Stat Event: M:{ev_d.get('M',0):+d} E:{ev_d.get('E',0):+d} ENV:{ev_d.get('ENV',0):+d} QoL:{ev_d.get('QoL',0):+d}</span>
                        </div>
                        """
                    )

            with st.expander("Detail Aturan & Log 13 Ronde Global Event", expanded=False):
                for round_no in range(1, 14):
                    ev = EVENT_BY_ROUND.get(round_no, EVENT_CARDS[0])
                    st.markdown(
                        f"**Ronde {round_no}: {ev['name']}** — *{ev['description']}* (Efek: `{ev.get('effect_summary', ev.get('effect_str', ''))}`)"
                    )

        ranked_players = rank_players_audit(final_player_audits)
        winner = ranked_players[0]

        st.markdown("---")
        render_html(
            f"""
            <div class="eco-card-champion" style="text-align:center;margin:12px 0 22px 0;padding:26px;">
              <span class="badge-champion">CITY PERFORMANCE LEADER · JUARA 1 AUDIT TATA KOTA</span>
              <h2 style="margin:10px 0 4px 0;font-size:2.5rem;color:#0F2A1D;font-family:'Fredoka','Outfit',sans-serif;font-weight:900;">
                <span style="color:#B45309;text-shadow:0 1px 6px rgba(245,158,11,0.5);">{winner['city_name']}</span> — {winner['player_name']}
              </h2>
              <div style="color:#3F5247;font-size:1.05rem;font-weight:600;">
                Skor Rata-Rata Akhir: <b style="color:#B45309;font-size:1.3rem;">{winner['avg_score']:.2f} / 100</b> &nbsp;·&nbsp;
                Profil Kota: <b style="color:{winner['archetype']['color']};">{winner['archetype']['name']}</b>
              </div>
            </div>
            """
        )

        podium_cols = st.columns(4, gap="medium")
        medal_titles = ["JUARA 1", "PERINGKAT 2", "PERINGKAT 3", "PERINGKAT 4"]
        podium_accents = ["#EAB308", "#0284C7", "#16A34A", "#E11D48"]

        for r_idx, p_res in enumerate(ranked_players):
            is_champ = r_idx == 0
            card_cls = "eco-card-champion" if is_champ else "eco-card"
            arch = p_res["archetype"]
            accent_pod = podium_accents[r_idx]
            pod_rating = get_overall_rating_grade(p_res["avg_score"])

            tb_note = ""
            if p_res.get("tie_breaker_reason"):
                tb_note = (
                    f'<div style="background:rgba(234,179,8,0.18);border:1px solid #EAB308;color:#B45309;'
                    f'border-radius:10px;padding:6px 10px;font-size:0.76rem;font-weight:700;margin-top:8px;">'
                    f'Tie-Breaker: {p_res["tie_breaker_reason"]}</div>'
                )

            with podium_cols[r_idx]:
                b_m = build_aspect_progress_html("Mobility", "M", p_res["M"], p_res["delta_M"], "#0284C7")
                b_e = build_aspect_progress_html("Energy", "E", p_res["E"], p_res["delta_E"], "#EAB308")
                b_env = build_aspect_progress_html("Environment", "ENV", p_res["ENV"], p_res["delta_ENV"], "#16A34A")
                b_qol = build_aspect_progress_html("Quality of Life", "QoL", p_res["QoL"], p_res["delta_QoL"], "#E11D48")

                render_html(
                    f"""
                    <div class="{card_cls}" style="margin-bottom:12px;border-top:4px solid {accent_pod};">
                      <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span class="eco-pill" style="background:rgba(234,179,8,0.16);color:#B45309;font-weight:800;border:1px solid rgba(234,179,8,0.5);">
                          {medal_titles[r_idx]}
                        </span>
                        <span style="font-family:'Outfit',sans-serif;font-size:0.75rem;font-weight:700;color:#3E5B4C;">
                          Rank #{p_res['rank']}
                        </span>
                      </div>
                      <h4 style="margin:10px 0 2px 0;font-size:1.25rem;color:#164E33;font-family:'Outfit',sans-serif;font-weight:800;">
                        {p_res['city_name']}
                      </h4>
                      <div style="font-size:0.86rem;color:#3E5B4C;font-weight:600;margin-bottom:8px;">
                        {p_res['player_name']}
                      </div>
                      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;background:linear-gradient(135deg,#FFFDF7 0%,rgba(22,163,74,0.10) 100%);border:1.5px solid #B7D5C4;border-radius:14px;padding:8px 12px;margin-bottom:10px;">
                        <div style="text-align:left;">
                          <div style="font-family:'Outfit',sans-serif;font-size:0.68rem;color:#3E5B4C;font-weight:800;text-transform:uppercase;">Average Score</div>
                          <div class="stat-outfit" style="font-size:1.85rem;font-weight:900;color:#164E33;line-height:1.1;">{p_res['avg_score']:.2f}</div>
                          <div style="font-size:0.74rem;font-weight:700;color:{arch['color']};margin-top:2px;">{arch['name']}</div>
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
                      <div style="margin-top:10px;padding-top:8px;border-top:1px dashed rgba(15,42,29,0.15);font-size:0.76rem;color:#4A5D52;">
                        <b>{p_res['project_count']}</b> Proyek &nbsp;·&nbsp;
                        <b>{p_res['tech_count']}</b> Tech &nbsp;·&nbsp;
                        <b>{p_res['coins']}</b> Koin
                      </div>
                      {tb_note}
                    </div>
                    """
                )

        mat_col, rad_col = st.columns([6, 4], gap="large")
        with mat_col:
            with st.container(border=True, key="panel_audit_matrix"):
                st.markdown("#### Matriks Perbandingan & Transparansi Tie-Breaker")
                st.caption("Penentuan peringkat resmi Rulebook (Bab VI.3): Skor Rata-Rata → Proyek Terbangun → Permanent Tech → Sisa Koin.")

                matrix_rows_html = ""
                for p_m in ranked_players:
                    matrix_rows_html += f"""
                    <tr style="border-bottom:1px solid rgba(15,42,29,0.08);">
                      <td style="padding:10px;font-weight:800;color:#0F2A1D;">#{p_m['rank']}</td>
                      <td style="padding:10px;font-weight:700;color:#0F2A1D;">{p_m['city_name']}<br/><span style="font-size:0.76rem;color:#4A5D52;font-weight:500;">{p_m['player_name']}</span></td>
                      <td style="padding:10px;text-align:center;font-weight:900;color:#047857;font-family:'Outfit',sans-serif;font-size:1.05rem;">{p_m['avg_score']:.2f}</td>
                      <td style="padding:10px;text-align:center;">{p_m['project_count']}</td>
                      <td style="padding:10px;text-align:center;">{p_m['tech_count']}</td>
                      <td style="padding:10px;text-align:center;font-weight:700;color:#B45309;">{p_m['coins']}</td>
                      <td style="padding:10px;font-size:0.78rem;color:#3F5247;">{p_m.get('tie_breaker_reason') or 'Skor Rata-Rata Tertinggi'}</td>
                    </tr>
                    """

                render_html(
                    f"""
                    <div style="overflow-x:auto;">
                      <table style="width:100%;border-collapse:collapse;font-size:0.86rem;color:#0F2A1D;">
                        <thead>
                          <tr style="background:rgba(21,128,61,0.08);border-bottom:2px solid #D6E4DA;text-align:left;">
                            <th style="padding:8px 10px;">Rank</th>
                            <th style="padding:8px 10px;">Kota &amp; Pemain</th>
                            <th style="padding:8px 10px;text-align:center;">Average</th>
                            <th style="padding:8px 10px;text-align:center;">Proyek</th>
                            <th style="padding:8px 10px;text-align:center;">Tech</th>
                            <th style="padding:8px 10px;text-align:center;">Koin</th>
                            <th style="padding:8px 10px;">Alasan Peringkat</th>
                          </tr>
                        </thead>
                        <tbody>
                          {matrix_rows_html}
                        </tbody>
                      </table>
                    </div>
                    """
                )

        with rad_col:
            with st.container(border=True, key="panel_audit_radar"):
                st.markdown("#### Radar Keseimbangan 4 Aspek Kota")
                st.caption("Perbandingan polygon profil 4 kota pada aspek Mobility, Energy, Environment, dan Quality of Life.")

                if go is not None:
                    categories = ["Mobility (M)", "Energy (E)", "Environment (ENV)", "Quality of Life (QoL)"]
                    radar_colors = ["#F59E0B", "#06B6D4", "#10B981", "#8B5CF6"]
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
                                opacity=0.35,
                            )
                        )
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, color="#4A5D52")),
                            angularaxis=dict(tickfont=dict(size=11, color="#0F2A1D", family="Plus Jakarta Sans")),
                            bgcolor="rgba(255,255,255,0.7)",
                        ),
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                        margin=dict(l=35, r=35, t=25, b=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=320,
                    )
                    st.plotly_chart(fig, width="stretch")

        st.markdown("---")
        with st.container(border=True, key="panel_narrative_reports"):
            nar_hdr1, nar_hdr2 = st.columns([7, 3])
            with nar_hdr1:
                st.markdown("### Sertifikat Audit & Laporan Naratif Kota Masa Depan (Tahun 2075)")
                st.caption("Penghargaan resmi akreditasi tata kota berkelanjutan: kekuatan infrastruktur, mitigasi risiko, rekomendasi tata ruang, dan simulasi jangka panjang 2075.")
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
                nar = generate_llm_enhanced_narrative(p_res)
                is_first = (r_idx == 0)

                with r_tab:
                    champ_banner = """
                    <div style="background:linear-gradient(90deg,#F59E0B,#D97706);color:#FFFFFF;padding:6px 18px;border-radius:999px;font-size:0.78rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;display:inline-flex;align-items:center;gap:6px;box-shadow:0 4px 14px rgba(245,158,11,0.35);margin-bottom:12px;">
                      <span>CITY PERFORMANCE LEADER · TATA KOTA TERBAIK 2075</span>
                    </div>
                    """ if is_first else f"""
                    <div style="background:rgba(2,132,199,0.12);border:1px solid rgba(2,132,199,0.35);color:#0284C7;padding:5px 14px;border-radius:999px;font-size:0.75rem;font-weight:800;letter-spacing:0.04em;text-transform:uppercase;display:inline-flex;align-items:center;gap:6px;margin-bottom:12px;">
                      <span>AKREDITASI TATA KOTA RESMI · PERINGKAT #{p_res['rank']}</span>
                    </div>
                    """

                    render_html(
                        f"""
                        <div style="background:linear-gradient(135deg,rgba(255,255,255,0.96) 0%,rgba(240,250,245,0.96) 100%);border:2px solid {arch['color']};border-radius:22px;padding:28px 32px;box-shadow:0 12px 36px rgba(15,42,29,0.08);margin-bottom:20px;position:relative;">
                          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
                            <div>
                              {champ_banner}
                              <h2 style="font-family:'Fredoka','Outfit',sans-serif;font-size:2.2rem;color:#0F2A1D;margin:4px 0;font-weight:900;">
                                {p_res['city_name']}
                              </h2>
                              <div style="font-size:1.05rem;color:#3F5247;font-weight:600;">
                                Wali Kota: <b style="color:#0F2A1D;">{p_res['player_name']}</b> &nbsp;·&nbsp;
                                Archetype: <b style="color:{arch['color']};">{arch['name']}</b>
                              </div>
                              <div style="font-size:0.86rem;color:#64748B;font-style:italic;margin-top:4px;">
                                "{arch['tagline']}"
                              </div>
                            </div>
                            <div style="display:flex;align-items:center;gap:14px;background:#FFFDF7;border:2px solid {arch['color']};border-radius:18px;padding:12px 20px;box-shadow:0 5px 0 rgba(22,78,51,0.12);">
                              <div style="text-align:center;">
                                <div style="font-family:'Outfit',sans-serif;font-size:0.72rem;color:#3E5B4C;font-weight:800;text-transform:uppercase;letter-spacing:0.05em;">Skor Rata-Rata Akhir</div>
                                <div class="stat-outfit" style="font-size:2.4rem;font-weight:900;color:{arch['color']};line-height:1.05;margin:4px 0;">{p_res['avg_score']:.2f}</div>
                                <div style="font-size:0.75rem;font-weight:700;color:#164E33;">Skala 0 – 100</div>
                              </div>
                              <div class="eco-rating-badge" style="width:62px;height:62px;min-width:62px;background:{get_overall_rating_grade(p_res['avg_score'])['bg']};color:{get_overall_rating_grade(p_res['avg_score'])['fg']};border-color:#FFFDF7;box-shadow:0 4px 0 rgba(22,78,51,0.22), 0 0 0 2px {get_overall_rating_grade(p_res['avg_score'])['ring']};">
                                <span style="font-size:0.55rem;font-weight:800;letter-spacing:0.06em;">GRADE</span>
                                <span style="font-size:1.45rem;font-weight:900;">{get_overall_rating_grade(p_res['avg_score'])['grade']}</span>
                              </div>
                            </div>
                          </div>

                          <div style="display:flex;gap:14px;flex-wrap:wrap;margin:18px 0 12px 0;padding:12px 0;border-top:1px dashed #D6E4DA;border-bottom:1px dashed #D6E4DA;">
                            <span class="eco-pill eco-pill-m" style="font-size:0.85rem;padding:6px 14px;">Mobility: <b>{p_res['M']}</b></span>
                            <span class="eco-pill eco-pill-e" style="font-size:0.85rem;padding:6px 14px;">Energy: <b>{p_res['E']}</b></span>
                            <span class="eco-pill eco-pill-env" style="font-size:0.85rem;padding:6px 14px;">Environment: <b>{p_res['ENV']}</b></span>
                            <span class="eco-pill eco-pill-qol" style="font-size:0.85rem;padding:6px 14px;">QoL: <b>{p_res['QoL']}</b></span>
                            <span class="eco-pill" style="font-size:0.85rem;padding:6px 14px;background:rgba(245,158,11,0.14);color:#B45309;border:1px solid rgba(245,158,11,0.4);">Kas: <b>{p_res['coins']} Koin</b></span>
                          </div>

                          <div style="font-size:0.85rem;color:#3F5247;line-height:1.5;">
                            <b>Dasar Klasifikasi Tata Kota:</b> {arch['reason']}
                          </div>
                        </div>
                        """
                    )

                    nc1, nc2 = st.columns(2, gap="medium")
                    with nc1:
                        with st.container(border=True, key=f"panel_nar_str_{r_idx}"):
                            st.markdown("#### Kekuatan Infrastruktur Kota")
                            st.markdown(nar["strengths"])
                        with st.container(border=True, key=f"panel_nar_vis_{r_idx}"):
                            st.markdown("#### Visi Tata Kota Masa Depan (Tahun 2075)")
                            st.markdown(nar["future_simulation"])

                    with nc2:
                        with st.container(border=True, key=f"panel_nar_chl_{r_idx}"):
                            st.markdown("#### Evaluasi Krisis & Mitigasi Risiko")
                            st.markdown(nar["challenges"])
                        with st.container(border=True, key=f"panel_nar_rec_{r_idx}"):
                            st.markdown("#### Rekomendasi Tata Ruang Terpadu")
                            st.markdown(nar["recommendations"])


# ==============================================================================
# TAB 3: AI GAME MASTER (ASISTEN ATURAN & KONSULTAN TATA KOTA)
# ==============================================================================
def render_tab_game_master() -> None:
    """Merender Tab 3: Profesor Terra AI Game Master & Ruang Konsultasi Rulebook."""
    render_html(
        """
        <div class="eco-ribbon-wrap">
          <span class="eco-ribbon-header">PROFESOR TERRA · AI GAME MASTER</span>
          <span style="font-size:0.78rem;font-weight:700;color:#164E33;background:#FFFDF7;border:1.5px solid #B7D5C4;border-radius:999px;padding:4px 12px;">
            Asisten Rulebook Resmi &amp; Konsultan Tata Kota EcoNova
          </span>
        </div>
        """
    )
    col_gm_side, col_gm_chat = st.columns([3.3, 6.7], gap="large")

    with col_gm_side:
        with st.container(border=True, key="panel_gm_sidebar"):
            llm_active = bool(get_groq_api_key())
            engine_badge = (
                "Groq AI Aktif"
                if llm_active
                else "Smart Rulebook Engine Aktif"
            )
            render_html(
                f"""
                <div class="ai-persona-box">
                  <div style="display:flex;align-items:center;gap:12px;">
                    <div class="ai-avatar-3d" style="font-size:1.1rem;font-weight:900;color:#FFFFFF;letter-spacing:0.05em;">AI</div>
                    <div>
                      <div style="font-family:'Outfit',sans-serif;font-size:1.15rem;font-weight:700;color:#0F2A1D;">
                        Profesor Terra (AI Game Master)
                      </div>
                      <div style="font-size:0.8rem;font-weight:700;color:#047857;margin-top:2px;">
                        <span class="ai-status-dot"></span>{engine_badge}
                      </div>
                    </div>
                  </div>
                  <div style="margin-top:12px;padding-top:10px;border-top:1px dashed rgba(15,42,29,0.15);font-size:0.84rem;color:#3F5247;font-weight:500;">
                    Menjawab aturan <b>AP</b>, <b>Syarat Tech</b>, <b>Diskon Event</b>, <b>Solusi Problem</b>, &amp; <b>Rumus Skor Akhir</b> secara instan.
                  </div>
                </div>
                """
            )

            st.markdown("##### Topik Pertanyaan Cepat (1-Klik)")
            quick_q = None
            qc1, qc2 = st.columns(2)
            if qc1.button("Aturan 3 AP", width="stretch", key="qp_ap"):
                quick_q = "Bagaimana aturan penggunaan 3 Action Points (AP) dan Movement menuju City Center?"
            if qc2.button("Bonus Koin", width="stretch", key="qp_tb"):
                quick_q = "Bagaimana cara menghitung Bonus Koin Akhir per 20 koin dan urutan Tie-Breaker resmi?"

            qc3, qc4 = st.columns(2)
            if qc3.button("Tech T1–T5", width="stretch", key="qp_tech"):
                quick_q = "Sebutkan efek Permanent Technology T1 sampai T5 dan Consumable Skill S1 sampai S5!"
            if qc4.button("Solusi Krisis", width="stretch", key="qp_prob"):
                quick_q = "Bagaimana aturan menyelesaikan Problem Card dengan koin vs kombinasi teknologi/skill dan penaltinya?"

            qc5, qc6 = st.columns(2)
            if qc5.button("13 Event", width="stretch", key="qp_ev"):
                quick_q = "Apa saja efek Global Event Card dari Round 1 sampai Round 13 beserta diskon distriknya?"
            if qc6.button("Panduan Skor", width="stretch", key="qp_strat"):
                quick_q = "Bagaimana strategi membangun kota agar mencapai archetype Balanced Sustainable Metropolis (>=75)?"

            st.markdown("---")
            act_c1, act_c2 = st.columns(2)
            with act_c1:
                if st.button("Reset Chat", width="stretch", key="btn_clear_chat"):
                    st.session_state.chat_history = [
                        {"role": "assistant", "content": WELCOME_CHAT_MESSAGE}
                    ]
                    st.rerun()
            with act_c2:
                st.caption(f"{len(st.session_state.chat_history)} pesan")

            with st.expander("Cheat-Sheet Aturan Cepat", expanded=False):
                st.markdown(
                    """
                    - **3 Action Points (AP di Papan Fisik):** Pindah distrik = `1 AP`, Bangun Proyek / Ambil Tech = `1 AP`, Selesaikan Krisis via Tech = `2 AP`, Bayar Koin = `1 AP`.
                    - **City Center:** Tiba di City Center = `+3 Koin` (maks 1x per ronde).
                    - **Permanent Tech (T1–T5):** Tetap dimiliki sepanjang game, aktif 1x/ronde, menyelesaikan Problem Card sesuai syarat kombinasi (`+`).
                    - **Consumable Skill (S1–S5):** Sekali pakai lalu terhapus (`consumed`).
                    - **Bonus Koin Akhir:** Tiap `20 Koin penuh` = `+5 poin ke 4 aspek`.
                    - **Tie-Breaker:** `Skor Rata-Rata` → `Jumlah Proyek` → `Tech Dimiliki` → `Sisa Koin`.
                    """
                )

    with col_gm_chat:
        with st.container(border=True, key="panel_gm_chat_main"):
            render_html(
                """
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid rgba(15,42,29,0.13);">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div>
                      <div style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;color:#0F2A1D;">
                        Ruang Konsultasi AI Game Master EcoNova
                      </div>
                      <div style="font-size:0.82rem;color:#4A5D52;font-weight:500;">
                        Tanyakan aturan permainan, simulasi giliran, syarat kartu, atau kombo pembangunan kota
                      </div>
                    </div>
                  </div>
                  <span class="eco-pill eco-pill-env">Terverifikasi Rulebook</span>
                </div>
                """
            )

            chat_stream = st.container(height=520, border=True, key="panel_gm_stream")
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
                              <div class="chat-avatar-badge chat-avatar-user" style="font-size:0.85rem;font-weight:900;color:#78350F;">W</div>
                            </div>
                            """
                        )
                    else:
                        render_html(
                            f"""
                            <div class="chat-row-ai">
                              <div class="chat-avatar-badge chat-avatar-ai" style="font-size:0.8rem;font-weight:900;color:#065F46;">AI</div>
                              <div class="chat-bubble-ai">
                                <div class="chat-sender-tag" style="color:#047857;">
                                  <span>PROFESOR TERRA · AI GAME MASTER</span>
                                </div>
                                <div>{content_html}</div>
                              </div>
                            </div>
                            """
                        )

            user_input = st.chat_input(
                "Ketik pertanyaan Anda di sini (contoh: Bagaimana mekanisme 3 AP atau aturan bonus koin?)...",
                key="chat_input_gm",
            )
            active_query = quick_q or user_input

            if active_query:
                st.session_state.chat_history.append({"role": "user", "content": active_query})
                answer = query_llm_game_master(active_query, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
