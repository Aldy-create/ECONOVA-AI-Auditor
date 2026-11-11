"""
app.py — EcoNova: Sustainable City Planner & AI Auditor
Tema Desain: Bright Glass 3D Full-Color Solarpunk Simulation HUD
Fitur Utama:
- Real-Time Physical Board Tracker (Ronde 1-13) dengan sistem Discard Event Card manual
- Manajemen Kepemilikan Kartu & Tombol Aksi Khusus Tech (1x/Ronde) dan Consumable Skill (S1-S5)
- Logika Khusus S1 (Penghapus Problem Card via Dropdown) & S5 (Imunitas Penalti Event Negatif)
- Zero Truncation, Zero Crash, & Defensive State Architecture
- Tab 2: Final AI Audit (Strict Lazy Loading) dengan Sertifikat Tata Kota 2075 (Tanpa Maket 3D)
- Tab 3: AI Game Master & Rulebook Consultant (Silent Background API Key Loading)
"""

import base64
import html
import json
import os
import re
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

# Redam deprecation warning internal Streamlit agar terminal tetap bersih
warnings.filterwarnings("ignore")
try:
    import streamlit.deprecation_util as _sdu
    _sdu.show_deprecation_warning = lambda *args, **kwargs: None
except Exception:
    pass

# Auto-launch Streamlit jika dieksekusi langsung via 'python app.py' atau VS Code Run Button
if __name__ == "__main__":
    try:
        from streamlit.runtime import exists as _st_exists
        if not _st_exists():
            import subprocess
            print("🚀 Meluncurkan EcoNova AI Auditor via Streamlit server di browser...")
            subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
            sys.exit(0)
    except Exception:
        pass

import pandas as pd
import streamlit as st

from cards_data import (
    ALL_CARDS,
    ALL_CARDS_197,
    CATEGORY_COLOR_THEMES,
    CONSUMABLE_SKILL_CARDS,
    DISTRICT_META,
    EVENT_BY_ID,
    EVENT_BY_ROUND,
    EVENT_CARDS,
    PERMANENT_TECH_BY_CODE,
    PERMANENT_TECH_CARDS,
    PROBLEM_BY_ID,
    PROBLEM_BY_LABEL,
    PROBLEM_CARDS,
    PROJECT_BY_ID,
    PROJECT_BY_LABEL,
    PROJECT_CARDS,
    REFERENCE_CARDS,
    RULEBOOK_SECTIONS,
    SKILL_BY_CODE,
    TECH_CARDS_40,
    TECH_CARDS_UNIQUE,
    TECH_UNIQUE_BY_CODE,
    calculate_coin_bonus,
    classify_city_archetype,
    compute_player_score,
    evaluate_events_for_player,
    evaluate_single_event_live,
    generate_city_narrative_report,
    get_card_clean_name,
    get_card_color_theme,
    rank_players_audit,
    smart_rulebook_search,
)

try:
    import plotly.graph_objects as go
except ImportError:
    go = None

try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None


# ==============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="EcoNova — Sustainable City Planner & AI Auditor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
SECRETS_PATH = BASE_DIR / ".streamlit" / "secrets.toml"


def render_html(html_str: str) -> None:
    """Merender HTML multi-baris secara aman tanpa terpotong parser Markdown code-block."""
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ==============================================================================
# 2. MANAJEMEN API KEY LLM (SILENT BACKGROUND LOADING)
# ==============================================================================
def get_groq_api_key() -> Optional[str]:
    """Mencari GROQ_API_KEY secara senyap dari session_state, secrets.toml, atau environment variable."""
    session_key = st.session_state.get("custom_groq_key", "").strip()
    if session_key:
        return session_key

    if SECRETS_PATH.exists():
        try:
            raw = SECRETS_PATH.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r'GROQ_API_KEY\s*=\s*["\']([^"\']+)["\']', raw)
            if match and match.group(1).strip():
                return match.group(1).strip()
        except Exception:
            pass

    try:
        if "GROQ_API_KEY" in st.secrets and str(st.secrets["GROQ_API_KEY"]).strip():
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass

    env_key = os.getenv("GROQ_API_KEY", "").strip()
    if env_key:
        return env_key
    return None


def query_llm_game_master(user_question: str, chat_history: List[Dict[str, str]]) -> str:
    """
    Menjawab pertanyaan Rulebook & Kartu menggunakan Groq LLM jika API Key tersedia,
    atau otomatis beralih ke Smart Keyword Search Engine lokal jika tanpa API Key / offline.
    """
    local_context = smart_rulebook_search(user_question)
    api_key = get_groq_api_key()

    if not api_key or ChatGroq is None:
        return local_context

    rules_summary = "\n\n".join(
        f"### {sec['title']}\n{sec['content']}" for sec in RULEBOOK_SECTIONS
    )
    sys_prompt = (
        "Kamu adalah Profesor Terra, AI Game Master & Official Rulebook Assistant untuk board game "
        "'EcoNova: Sustainable City Builder'. Jawablah dalam Bahasa Indonesia yang ramah, terstruktur, "
        "dan akurat 100% sesuai Rulebook resmi berikut.\n\n"
        f"RINGKASAN RULEBOOK RESMI:\n{rules_summary}\n\n"
        f"DATA KARTU & ATURAN TERKAIT PERTANYAAN:\n{local_context}\n\n"
        "Jangan pernah mengarang aturan di luar Rulebook. Sebutkan kode ID kartu (misal P001, T1, S1, PR01, EV01), "
        "angka AP, harga koin, syarat Tech (T1-T5), dan perubahan stat (M, E, ENV, QoL) secara presisi."
    )
    msgs = [SystemMessage(content=sys_prompt)]
    for msg in chat_history[-6:]:
        if msg["role"] == "user":
            msgs.append(HumanMessage(content=msg["content"]))
        else:
            msgs.append(AIMessage(content=msg["content"]))
    msgs.append(HumanMessage(content=user_question))

    for candidate_model in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
        try:
            llm = ChatGroq(
                model=candidate_model,
                temperature=0.2,
                groq_api_key=api_key,
                max_tokens=950,
            )
            resp = llm.invoke(msgs)
            content = getattr(resp, "content", "")
            if content and str(content).strip():
                return str(content).strip()
        except Exception:
            continue

    return local_context


def generate_llm_enhanced_narrative(audit: Dict[str, Any]) -> Dict[str, str]:
    """
    Menghasilkan 4 bagian narasi kota masa depan.
    Jika mode AI LLM aktif dan API Key tersedia, memperkaya narasi dengan LLM;
    jika tidak atau gagal, menggunakan Template Generator Dinamis Berbasis Data.
    """
    base_report = generate_city_narrative_report(audit)
    if not st.session_state.get("use_llm_narrative", False):
        return base_report

    api_key = get_groq_api_key()
    if not api_key or ChatGroq is None:
        return base_report

    proj_str = ", ".join(p["name"] for p in audit["projects"]) or "Belum ada proyek"
    tech_str = ", ".join(f"{t['code']} ({t['name']})" for t in audit["techs"]) or "Tanpa Tech"
    prob_str = ", ".join(f"{p['name']} ({p['pen_str']})" for p in audit["failed_problems"]) or "0 Krisis Gagal"

    prompt = (
        f"Buat narasi masa depan visi kota berkelanjutan tahun 2075 (3-4 kalimat imersif dalam Bahasa Indonesia) "
        f"untuk kota '{audit['city_name']}' yang dipimpin Wali Kota '{audit['player_name']}'.\n"
        f"Archetype: {audit['archetype']['name']}.\n"
        f"Skor Akhir: Mobility={audit['M']}, Energy={audit['E']}, Environment={audit['ENV']}, "
        f"Quality of Life={audit['QoL']} (Average={audit['avg_score']:.2f}).\n"
        f"Proyek terbangun: {proj_str}.\n"
        f"Teknologi Permanen: {tech_str}.\n"
        f"Sejarah Krisis Gagal: {prob_str}.\n"
        "Tuliskan langsung paragraf narasinya tanpa judul tambahan."
    )

    for candidate_model in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
        try:
            llm = ChatGroq(
                model=candidate_model,
                temperature=0.45,
                groq_api_key=api_key,
                max_tokens=700,
            )
            resp = llm.invoke([HumanMessage(content=prompt)])
            text = str(getattr(resp, "content", "")).strip()
            if len(text) > 60:
                base_report["future_simulation"] = text
                return base_report
        except Exception:
            continue

    return base_report


# ==============================================================================
# 3. STATE PERSISTENCE (st.session_state.players) & CALLBACKS
# ==============================================================================
WELCOME_CHAT_MESSAGE = (
    "Halo Wali Kota! Saya **Profesor Terra — AI Game Master EcoNova**.\n\n"
    "Saya siap membantu Anda mengecek aturan resmi maupun strategi kartu secara real-time:\n"
    "- **Mekanisme 3 Action Points (AP)** & bonus transit City Center (+3 Koin)\n"
    "- **Efek Pasif Permanent Tech (T1–T5)** & Consumable Skill (S1–S5)\n"
    "- **Solusi Problem Card (PR01–PR20)** via Koin vs Teknologi\n"
    "- **Rumus Bonus Koin Akhir (per 20 Koin)** & urutan Tie-Breaker resmi\n\n"
    "Silakan klik topik pertanyaan cepat atau ketik pertanyaan Anda di bawah."
)


def init_session_state() -> None:
    """Inisialisasi session state murni baseline dengan struktur st.session_state.players."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": WELCOME_CHAT_MESSAGE}]

    if "current_round" not in st.session_state:
        st.session_state.current_round = 1

    if "used_events" not in st.session_state:
        st.session_state.used_events = []

    # Dropdown Event Card dimulai kosong (None / placeholder)
    if "selected_event_id" not in st.session_state:
        st.session_state.selected_event_id = None

    if "audit_triggered" not in st.session_state:
        st.session_state.audit_triggered = False

    if "enable_manual_points" not in st.session_state:
        st.session_state.enable_manual_points = False

    if "players" not in st.session_state:
        st.session_state.players = {}

    if "tech_used_this_round" not in st.session_state:
        st.session_state.tech_used_this_round = {
            p_id: {t: False for t in ["T1", "T2", "T3", "T4", "T5"]} for p_id in range(1, 5)
        }

    if "widget_event_picker" not in st.session_state:
        st.session_state.widget_event_picker = None

    for p_id in range(1, 5):
        if p_id not in st.session_state.players:
            st.session_state.players[p_id] = {
                "name": f"Pemain {p_id}",
                "city": f"Kota {p_id}",
                "projects": [],
                "techs": [],
                "skills": [],
                "problems": [],
                "coins": 5,
                "manual_points": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "active_techs_this_round": [],
                "bonus_stats": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "accumulated_event_delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "accumulated_event_coins": 0,
                "immune_this_round": False,
                "tech_log": [],
            }
        if "manual_points" not in st.session_state.players[p_id]:
            st.session_state.players[p_id]["manual_points"] = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}

        if f"widget_name_{p_id}" not in st.session_state:
            st.session_state[f"widget_name_{p_id}"] = st.session_state.players[p_id]["name"]
        if f"widget_city_{p_id}" not in st.session_state:
            st.session_state[f"widget_city_{p_id}"] = st.session_state.players[p_id]["city"]
        if f"widget_projects_{p_id}" not in st.session_state:
            st.session_state[f"widget_projects_{p_id}"] = list(st.session_state.players[p_id]["projects"])
        if f"widget_techs_{p_id}" not in st.session_state:
            st.session_state[f"widget_techs_{p_id}"] = list(st.session_state.players[p_id]["techs"])
        if f"widget_skills_{p_id}" not in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(st.session_state.players[p_id]["skills"])
        if f"widget_problems_{p_id}" not in st.session_state:
            st.session_state[f"widget_problems_{p_id}"] = list(st.session_state.players[p_id]["problems"])
        if f"widget_coins_{p_id}" not in st.session_state:
            st.session_state[f"widget_coins_{p_id}"] = st.session_state.players[p_id]["coins"]

        for stat_key in ["M", "E", "ENV", "QoL"]:
            w_mkey = f"widget_man_{stat_key}_{p_id}"
            if w_mkey not in st.session_state:
                st.session_state[w_mkey] = st.session_state.players[p_id]["manual_points"].get(stat_key, 0)


init_session_state()


# ------------------------------------------------------------------------------
# CALLBACKS WIDGET SYNC & GAME ACTION (ZERO-CRASH STATE ARCHITECTURE)
# ------------------------------------------------------------------------------
def callback_sync_name(p_id: int) -> None:
    val = st.session_state.get(f"widget_name_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["name"] = str(val).strip() or f"Pemain {p_id}"


def callback_sync_city(p_id: int) -> None:
    val = st.session_state.get(f"widget_city_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["city"] = str(val).strip() or f"Kota {p_id}"


def callback_sync_projects(p_id: int) -> None:
    val = st.session_state.get(f"widget_projects_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["projects"] = list(val)


def callback_sync_techs(p_id: int) -> None:
    val = st.session_state.get(f"widget_techs_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["techs"] = list(val)


def callback_sync_skills(p_id: int) -> None:
    val = st.session_state.get(f"widget_skills_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["skills"] = list(val)


def callback_sync_problems(p_id: int) -> None:
    val = st.session_state.get(f"widget_problems_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["problems"] = list(val)


def callback_sync_coins(p_id: int) -> None:
    val = st.session_state.get(f"widget_coins_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["coins"] = int(val)


def callback_sync_manual_points(p_id: int, stat_key: str) -> None:
    val = st.session_state.get(f"widget_man_{stat_key}_{p_id}")
    if val is not None:
        if "manual_points" not in st.session_state.players[p_id]:
            st.session_state.players[p_id]["manual_points"] = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
        st.session_state.players[p_id]["manual_points"][stat_key] = int(val)


def callback_reset_manual_points(p_id: int) -> None:
    if "manual_points" in st.session_state.players[p_id]:
        st.session_state.players[p_id]["manual_points"] = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    for stat_key in ["M", "E", "ENV", "QoL"]:
        w_mkey = f"widget_man_{stat_key}_{p_id}"
        st.session_state[w_mkey] = 0


def callback_event_picker_changed() -> None:
    """Callback saat pemain memilih event fisik dari dropdown."""
    st.session_state.selected_event_id = st.session_state.get("widget_event_picker")


def callback_next_round() -> None:
    """
    Callback navigasi ronde berikutnya:
    1. Simpan efek Event Card ronde tersebut secara permanen ke akumulator skor pemain (kecuali jika kebal via S5).
    2. Masukkan Event Card yang baru saja dipakai ke used_events (Discard Pile).
    3. Kosongkan kembali selector Event Card ke None / placeholder.
    4. Reset status pemakaian Tech Card (tech_used_this_round) dan status imunitas S5 (immune_this_round).
    """
    curr_ev = st.session_state.selected_event_id
    if curr_ev and curr_ev in EVENT_BY_ID:
        for p_id in range(1, 5):
            pl = st.session_state.players[p_id]
            is_imm = pl.get("immune_this_round", False)
            single_ev = evaluate_single_event_live(
                curr_ev, pl["projects"], pl["techs"], is_immune=is_imm
            )
            for k in ("M", "E", "ENV", "QoL"):
                pl["accumulated_event_delta"][k] += single_ev["delta"][k]
            pl["accumulated_event_coins"] += single_ev["coins"]

        if curr_ev not in st.session_state.used_events:
            st.session_state.used_events.append(curr_ev)

    if st.session_state.current_round < 13:
        st.session_state.current_round += 1

    # Kosongkan kembali selector Event Card
    st.session_state.selected_event_id = None
    if "widget_event_picker" in st.session_state:
        st.session_state.widget_event_picker = None

    # Reset status tombol tech dan status imunitas S5 untuk ronde baru
    st.session_state.tech_used_this_round = {
        p_id: {t: False for t in ["T1", "T2", "T3", "T4", "T5"]} for p_id in range(1, 5)
    }
    for p_id in range(1, 5):
        st.session_state.players[p_id]["active_techs_this_round"] = []
        st.session_state.players[p_id]["immune_this_round"] = False


def callback_prev_round() -> None:
    """Callback navigasi ronde sebelumnya & kembalikan kartu event ke pool."""
    if st.session_state.current_round > 1:
        st.session_state.current_round -= 1
        if st.session_state.used_events:
            restored = st.session_state.used_events.pop()
            st.session_state.selected_event_id = restored
            st.session_state.widget_event_picker = restored


def callback_reset_game() -> None:
    """Mereset seluruh data ke baseline awal (Skor 50, Koin 5, Tanpa Kartu)."""
    st.session_state.current_round = 1
    st.session_state.used_events = []
    st.session_state.selected_event_id = None
    if "widget_event_picker" in st.session_state:
        st.session_state.widget_event_picker = None
    st.session_state.audit_triggered = False

    st.session_state.tech_used_this_round = {
        p_id: {t: False for t in ["T1", "T2", "T3", "T4", "T5"]} for p_id in range(1, 5)
    }
    for p_id in range(1, 5):
        st.session_state.players[p_id] = {
            "name": f"Pemain {p_id}",
            "city": f"Kota {p_id}",
            "projects": [],
            "techs": [],
            "skills": [],
            "problems": [],
            "coins": 5,
            "manual_points": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "active_techs_this_round": [],
            "bonus_stats": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "accumulated_event_delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "accumulated_event_coins": 0,
            "immune_this_round": False,
            "tech_log": [],
        }
        st.session_state[f"widget_projects_{p_id}"] = []
        st.session_state[f"widget_techs_{p_id}"] = []
        st.session_state[f"widget_skills_{p_id}"] = []
        st.session_state[f"widget_problems_{p_id}"] = []
        st.session_state[f"widget_coins_{p_id}"] = 5
        for stat_key in ["M", "E", "ENV", "QoL"]:
            st.session_state[f"widget_man_{stat_key}_{p_id}"] = 0


def callback_activate_tech(p_id: int, t_code: str) -> None:
    """Aksi khusus kartu teknologi permanen dengan cooldown 1x per ronde."""
    pl = st.session_state.players[p_id]
    if t_code not in pl["active_techs_this_round"]:
        pl["active_techs_this_round"].append(t_code)

    st.session_state.tech_used_this_round[p_id][t_code] = True
    curr_r = st.session_state.current_round
    cur_probs = list(pl["problems"])
    meta = TECH_ACTION_META.get(t_code, {})
    solves = meta.get("solves_problems", [])

    solved_pid = None
    if solves == "ALL" and cur_probs:
        solved_pid = cur_probs[0]
    elif isinstance(solves, list):
        for pid in cur_probs:
            if pid in solves:
                solved_pid = pid
                break

    if solved_pid:
        pl["problems"].remove(solved_pid)
        if f"widget_problems_{p_id}" in st.session_state:
            st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])
        p_name = PROBLEM_BY_ID.get(solved_pid, {}).get("name", solved_pid)
        pl["tech_log"].append(f"R{curr_r}: Aksi {t_code} netralkan krisis [{p_name}]")
    else:
        pl["tech_log"].append(f"R{curr_r}: Aksi {t_code} diaktifkan ({meta.get('short_label', '')})")


def callback_use_s1(p_id: int, prob_to_remove: str) -> None:
    """Logika khusus S1: Menghapus 1 Problem Card terpilih dan kartu S1 langsung dikonsumsi (hilang)."""
    pl = st.session_state.players[p_id]
    curr_r = st.session_state.current_round

    if prob_to_remove in pl["problems"]:
        pl["problems"].remove(prob_to_remove)
        if f"widget_problems_{p_id}" in st.session_state:
            st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])

    if "S1" in pl["skills"]:
        pl["skills"].remove("S1")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])

    p_name = PROBLEM_BY_ID.get(prob_to_remove, {}).get("name", prob_to_remove)
    pl["tech_log"].append(f"R{curr_r}: S1 dipakai (Hapus Krisis [{p_name}])")


def callback_use_s1_fallback(p_id: int) -> None:
    """Fallback S1 jika pemain tidak memiliki problem card: Memberi dana darurat +2 ke semua pilar."""
    pl = st.session_state.players[p_id]
    curr_r = st.session_state.current_round
    if "S1" in pl["skills"]:
        pl["skills"].remove("S1")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    for k in ["M", "E", "ENV", "QoL"]:
        pl["bonus_stats"][k] += 2
    pl["tech_log"].append(f"R{curr_r}: S1 dipakai (Dana Darurat +2 Semua Aspek)")


def callback_use_s2(p_id: int) -> None:
    """Logika S2: +5 ENV, kartu S2 terkonsumsi."""
    pl = st.session_state.players[p_id]
    curr_r = st.session_state.current_round
    if "S2" in pl["skills"]:
        pl["skills"].remove("S2")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["bonus_stats"]["ENV"] += 5
    pl["tech_log"].append(f"R{curr_r}: S2 dipakai (+5 ENV)")


def callback_use_s3(p_id: int) -> None:
    """Logika S3: +5 M, kartu S3 terkonsumsi."""
    pl = st.session_state.players[p_id]
    curr_r = st.session_state.current_round
    if "S3" in pl["skills"]:
        pl["skills"].remove("S3")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["bonus_stats"]["M"] += 5
    pl["tech_log"].append(f"R{curr_r}: S3 dipakai (+5 M)")


def callback_use_s4(p_id: int) -> None:
    """Logika S4: +5 QoL, kartu S4 terkonsumsi."""
    pl = st.session_state.players[p_id]
    curr_r = st.session_state.current_round
    if "S4" in pl["skills"]:
        pl["skills"].remove("S4")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["bonus_stats"]["QoL"] += 5
    pl["tech_log"].append(f"R{curr_r}: S4 dipakai (+5 QoL)")


def callback_use_s5(p_id: int) -> None:
    """Logika khusus S5: Mengaktifkan imunitas penalti event ronde ini, kartu S5 terkonsumsi."""
    pl = st.session_state.players[p_id]
    curr_r = st.session_state.current_round
    if "S5" in pl["skills"]:
        pl["skills"].remove("S5")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["immune_this_round"] = True
    pl["tech_log"].append(f"R{curr_r}: S5 Cyber Shield aktif (Kebal penalti Event ronde ini)")


# ==============================================================================
# 4. BRIGHT GLASS 3D FULL-COLOR SOLARUNK DESIGN SYSTEM (CSS)
# ==============================================================================
render_html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700;800;900&family=Outfit:wght@500;600;700;800;900&family=Plus+Jakarta+Sans:ital,wght@0,500;0,600;0,700;0,800;1,500&display=swap');

:root {
    --bg-sky-top: #C8E8F8;
    --bg-sky-mid: #E3F2F6;
    --bg-sky-bot: #F5F9F6;
    --text-primary: #0F2A1D;
    --text-secondary: #4A5D52;
    --glass-bg: rgba(255, 255, 255, 0.78);
    --glass-border: rgba(255, 255, 255, 0.92);
    --shadow-3d: 0 10px 30px rgba(15, 42, 29, 0.06), 0 2px 6px rgba(0, 0, 0, 0.02);
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
    background-image: linear-gradient(180deg, #C2E5F9 0%, #DFF1F7 28%, #ECF7F0 60%, #F8F6ED 100%) !important;
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

/* Glass Panels */
div[data-testid="stVerticalBlockBorderWrapper"] > div,
div[class*="st-key-panel_"],
.eco-card {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1.5px solid var(--glass-border) !important;
    border-radius: 20px !important;
    box-shadow: var(--shadow-3d) !important;
    padding: 18px 20px !important;
    margin-bottom: 14px !important;
    transition: all 0.22s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div:hover,
div[class*="st-key-panel_"]:hover,
.eco-card:hover {
    border-color: rgba(2, 132, 199, 0.35) !important;
    box-shadow: 0 12px 34px rgba(2, 132, 199, 0.09) !important;
}

/* Champion Card */
.eco-card-champion {
    background: linear-gradient(135deg, rgba(255, 251, 235, 0.92) 0%, rgba(254, 243, 199, 0.82) 55%, rgba(255, 255, 255, 0.92) 100%) !important;
    backdrop-filter: blur(18px) !important;
    border: 2px solid rgba(245, 158, 11, 0.6) !important;
    border-radius: 22px !important;
    box-shadow: 0 14px 40px rgba(245, 158, 11, 0.16) !important;
    padding: 24px 28px !important;
    margin-bottom: 18px !important;
}
.badge-champion {
    display: inline-flex;
    align-items: center;
    background: linear-gradient(180deg, #FBBF24 0%, #F59E0B 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3) !important;
    color: #FFFFFF !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.8rem !important;
    padding: 5px 14px !important;
    border-radius: 999px !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
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

/* Hero Banner */
.eco-hero-banner {
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: blur(18px);
    border: 1.5px solid rgba(255, 255, 255, 0.95);
    border-radius: 22px;
    padding: 22px 28px;
    margin-bottom: 18px;
    box-shadow: var(--shadow-3d);
}
.eco-hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
.eco-hero-title {
    font-family: 'Fredoka', 'Outfit', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 900 !important;
    margin: 0 !important;
    line-height: 1.15;
}
.eco-pill-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    background: rgba(5, 150, 105, 0.12);
    border: 1px solid rgba(5, 150, 105, 0.3);
    color: #047857;
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.eco-legend-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.eco-legend-pill {
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
}
.pill-env { background: rgba(5, 150, 105, 0.12); border: 1px solid rgba(5, 150, 105, 0.3); color: #047857 !important; }
.pill-m { background: rgba(2, 132, 199, 0.12); border: 1px solid rgba(2, 132, 199, 0.3); color: #0284C7 !important; }
.pill-e { background: rgba(217, 119, 6, 0.12); border: 1px solid rgba(217, 119, 6, 0.3); color: #B45309 !important; }
.pill-qol { background: rgba(225, 29, 72, 0.12); border: 1px solid rgba(225, 29, 72, 0.3); color: #BE123C !important; }

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

/* Chat Styling */
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
.chat-bubble-user {
    background: linear-gradient(180deg, #16A34A 0%, #15803D 100%);
    border-radius: 18px 6px 18px 18px;
    padding: 12px 18px;
    box-shadow: 0 6px 16px rgba(21, 128, 61, 0.2);
    max-width: 82%;
    color: #FFFFFF !important;
    font-size: 0.94rem;
    font-weight: 600;
}
.chat-bubble-user * { color: #FFFFFF !important; }
</style>
"""
)


# ==============================================================================
# 5. UI RENDERING HELPERS
# ==============================================================================
def build_aspect_progress_html(label: str, icon: str, val: int, delta: int, color: str) -> str:
    """Membangun HTML progress bar 3D glossy dengan indikator delta dan kontras tajam."""
    pct = max(0, min(100, int(val)))
    delta_str = f"{delta:+d}"
    text_color = {
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


# ==============================================================================
# 6. HEADER UTAMA SOLARPUNK (CLEAN HUD)
# ==============================================================================
render_html(
    """
<div class="eco-hero-banner">
  <div class="eco-hero-top">
    <div>
      <div class="eco-pill-badge">ECONOVA HUD · RULEBOOK RESMI v1.0</div>
      <h1 class="eco-hero-title">
        EcoNova <span style="color:#059669;">Sustainable City Planner</span> &amp; <span style="color:#0284C7;">AI Auditor</span>
      </h1>
      <div style="color:#4A5D52;font-size:0.92rem;font-weight:600;margin-top:4px;">
        Sistem Komando Tata Kota Berkelanjutan · Konsultasi Game Master &amp; Auditor Presisi
      </div>
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
# 7. PILIHAN & LABEL KARTU (CLEAN DISPLAY NAMES)
# ==============================================================================
project_id_options = list(PROJECT_BY_ID.keys())
tech_code_options = list(PERMANENT_TECH_BY_CODE.keys())
skill_code_options = list(SKILL_BY_CODE.keys())
problem_id_options = list(PROBLEM_BY_ID.keys())


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


TECH_ACTION_META: Dict[str, Dict[str, Any]] = {
    "T1": {
        "name": "Solar Engineering",
        "short_label": "+2 E",
        "solves_problems": ["PR03", "PR08", "PR11", "PR17", "PR20"],
        "passive_desc": "+2 Energy. Menetralkan krisis energi & memenuhi syarat proyek T1.",
    },
    "T2": {
        "name": "AI Urban System",
        "short_label": "+1 M, +1 QoL",
        "solves_problems": ["PR02", "PR08", "PR10", "PR16", "PR19"],
        "passive_desc": "+1 M, +1 QoL. Mengoptimalkan lalu lintas & krisis AI/kemacetan.",
    },
    "T3": {
        "name": "Circular Materials",
        "short_label": "+2 ENV",
        "solves_problems": ["PR01", "PR07", "PR11", "PR15", "PR16", "PR18", "PR20"],
        "passive_desc": "+2 ENV. Menetralkan krisis polusi/limbah & kebal EV06.",
    },
    "T4": {
        "name": "Electric Mobility",
        "short_label": "+2 M",
        "solves_problems": ["PR09", "PR03", "PR10", "PR18"],
        "passive_desc": "+2 Mobility. Mengatasi krisis transit massal & kebal penalti EV02.",
    },
    "T5": {
        "name": "Modular Eco-Housing",
        "short_label": "+1 ENV, +1 QoL",
        "solves_problems": ["PR04", "PR05", "PR07", "PR13", "PR20"],
        "passive_desc": "+1 ENV, +1 QoL. Mengatasi krisis air/banjir & kebal penalti EV10.",
    },
    "S1": {
        "name": "Emergency Response",
        "short_label": "Hapus 1 Problem",
        "solves_problems": "ALL",
        "passive_desc": "Hapus satu Problem Card penalti yang sedang aktif.",
    },
    "S2": {
        "name": "Carbon Capture Boost",
        "short_label": "+5 ENV",
        "solves_problems": ["PR01", "PR11"],
        "passive_desc": "Aktivasi instan +5 Environment ke tata kota.",
    },
    "S3": {
        "name": "Traffic Override",
        "short_label": "+5 M",
        "solves_problems": ["PR02"],
        "passive_desc": "Aktivasi instan +5 Mobility ke koridor transit.",
    },
    "S4": {
        "name": "Public Health Campaign",
        "short_label": "+5 QoL",
        "solves_problems": ["PR06"],
        "passive_desc": "Aktivasi instan +5 Quality of Life ke warga kota.",
    },
    "S5": {
        "name": "Cyber Shield",
        "short_label": "Kebal Penalti Event",
        "solves_problems": ["PR10"],
        "passive_desc": "Kebal terhadap semua penalti / efek negatif Event Card ronde ini.",
    },
}


# ==============================================================================
# 8. TIGA TAB UTAMA APLIKASI (TANPA SIMULATOR MAKET 3D)
# ==============================================================================
tab_tracker, tab_audit, tab_gm = st.tabs(
    [
        "Tab 1: Live Tracker",
        "Tab 2: Final Audit",
        "Tab 3: AI Game Master",
    ]
)


# ==============================================================================
# TAB 1: LIVE GAME DASHBOARD TRACKER (1 LAYAR BERSAMA 4 PEMAIN)
# ==============================================================================
with tab_tracker:
    # --------------------------------------------------------------------------
    # TOP TELEMETRY BAR: RONDE BERJALAN & GLOBAL EVENT AKTIF (SISTEM DISCARD)
    # --------------------------------------------------------------------------
    with st.container(border=True, key="panel_tracker_topbar"):
        r_col1, r_col2, r_col3 = st.columns([3.8, 5.2, 3.0], gap="medium")
        with r_col1:
            curr_round = int(st.session_state.current_round)
            render_html(
                f"""
                <div style="background:rgba(255,255,255,0.92);border:1.5px solid rgba(5,150,105,0.35);border-radius:16px;padding:10px 14px;box-shadow:0 4px 16px rgba(5,150,105,0.08);text-align:center;">
                  <div style="font-family:'Outfit',sans-serif;font-size:0.75rem;font-weight:700;color:#047857;letter-spacing:0.05em;text-transform:uppercase;">
                    Telemetri Ronde Permainan
                  </div>
                  <div class="stat-outfit" style="font-size:1.9rem;font-weight:900;color:#0F2A1D;line-height:1.15;margin-top:2px;">
                    RONDE <span style="color:#059669;">{curr_round:02d}</span> / 13
                  </div>
                  <div style="font-size:0.74rem;color:#4A5D52;font-weight:600;margin-top:2px;">
                    {'Ronde Terakhir (Evaluasi Akhir)' if curr_round == 13 else 'Fase Pembangunan Kota Fisik'}
                  </div>
                </div>
                """
            )

            # Tombol Navigasi Ronde dengan Sistem Discard Event & Cooldown Tech
            nav_c1, nav_c2 = st.columns(2, gap="small")
            with nav_c1:
                st.button(
                    "⬅️ Ronde Sebelumnya",
                    key="btn_prev_round",
                    disabled=(curr_round <= 1),
                    width="stretch",
                    on_click=callback_prev_round,
                )
            with nav_c2:
                st.button(
                    "Lanjut Ronde Berikutnya ➡️",
                    key="btn_next_round",
                    disabled=(curr_round >= 13),
                    type="primary",
                    width="stretch",
                    on_click=callback_next_round,
                    help="Lanjut ronde: simpan efek event aktif ke histori pemain, buang kartu ke Discard, dan reset tombol tech.",
                )

        with r_col2:
            used_events = st.session_state.get("used_events", [])
            available_events = [e["id"] for e in EVENT_CARDS if e["id"] not in used_events]
            event_picker_options: List[Optional[str]] = [None] + available_events

            current_sel = st.session_state.get("selected_event_id")
            if current_sel not in event_picker_options:
                current_sel = None
                st.session_state.selected_event_id = None

            current_idx = event_picker_options.index(current_sel)

            st.selectbox(
                "Event Card Terbuka di Papan Fisik:",
                options=event_picker_options,
                index=current_idx,
                format_func=format_event_selector,
                key="widget_event_picker",
                on_change=callback_event_picker_changed,
                help="Pilih Event Card yang sedang terbuka di papan fisik ronde ini. Kartu ronde lalu otomatis masuk Discard.",
            )

            active_event_id = st.session_state.selected_event_id
            if active_event_id and active_event_id in EVENT_BY_ID:
                active_event = EVENT_BY_ID[active_event_id]
                render_html(
                    f"""
                    <div style="background:rgba(255,255,255,0.92);border:1.5px solid rgba(2,132,199,0.35);border-radius:14px;padding:10px 14px;box-shadow:0 3px 14px rgba(2,132,199,0.06);margin-top:4px;">
                      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                        <span class="eco-pill eco-pill-m" style="font-size:0.74rem;background:rgba(2,132,199,0.12);color:#0284C7;border:1px solid rgba(2,132,199,0.3);">
                          {active_event['name']}
                        </span>
                        <span style="font-size:0.78rem;font-weight:700;color:#047857;">
                          Efek Live: {active_event.get('effect_summary', active_event.get('effect_str', ''))}
                        </span>
                      </div>
                      <div style="font-size:0.76rem;color:#334155;line-height:1.35;margin-top:6px;">
                        {active_event['description']}
                      </div>
                    </div>
                    """
                )
            else:
                render_html(
                    """
                    <div style="background:rgba(255,255,255,0.7);border:1.5px dashed #94A3B8;border-radius:14px;padding:10px 14px;margin-top:4px;color:#64748B;font-size:0.78rem;">
                      Belum ada Event Card yang dibuka di papan fisik ronde ini. Skor pemain tidak terpengaruh event sampai kartu dipilih.
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

        with p_cols[idx]:
            with st.container(border=True, key=f"panel_tracker_p{p_id}"):
                # Header Identitas
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

                # Live Scoring Calculation (Tanpa Event Otomatis, Hanya Event Aktif & Tech yang Diaktifkan)
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
                    accumulated_event_coins=pl["accumulated_event_coins"],
                    is_immune=pl.get("immune_this_round", False),
                    manual_delta=pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
                )
                live_audits_tab1.append(live_audit)
                arch = live_audit["archetype"]

                # Badge Rata-Rata Skor Live
                render_html(
                    f"""
                    <div style="background:linear-gradient(135deg,rgba(255,255,255,0.95) 0%,rgba(240,249,244,0.95) 100%);border:1.5px solid #D6E4DA;border-top:3.5px solid {arch['color']};border-radius:14px;padding:10px;text-align:center;margin:6px 0 10px 0;box-shadow:0 4px 14px rgba(15,42,29,0.06);">
                      <div style="font-family:'Outfit',sans-serif;font-size:0.72rem;color:#4A5D52;font-weight:700;text-transform:uppercase;">Live Average Score</div>
                      <div class="stat-outfit" style="font-size:2.0rem;font-weight:900;color:#047857;line-height:1.1;">{live_audit['avg_score']:.2f}</div>
                      <div style="font-size:0.78rem;font-weight:700;color:{arch['color']};margin-top:2px;">{arch['name']}</div>
                    </div>
                    """
                )

                # Telemetry Bar 4 Aspek (M, E, ENV, QoL)
                st.markdown(
                    build_aspect_progress_html("Mobility (M)", "M", live_audit["M"], live_audit["delta_M"], "#06B6D4"),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    build_aspect_progress_html("Energy (E)", "E", live_audit["E"], live_audit["delta_E"], "#F59E0B"),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    build_aspect_progress_html("Environment (ENV)", "ENV", live_audit["ENV"], live_audit["delta_ENV"], "#10B981"),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    build_aspect_progress_html("Quality of Life (QoL)", "QoL", live_audit["QoL"], live_audit["delta_QoL"], "#F43F5E"),
                    unsafe_allow_html=True,
                )

                # Indikator Imunitas S5 & Dampak Event Live
                if pl.get("immune_this_round", False):
                    render_html(
                        """
                        <div style="font-size:0.72rem;color:#047857;background:rgba(16,185,129,0.15);border:1px solid #10B981;border-radius:8px;padding:4px 8px;margin-top:6px;font-weight:700;">
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

                # Indikator Akumulasi Bonus Skill
                if any(pl["bonus_stats"].values()):
                    sb = pl["bonus_stats"]
                    render_html(
                        f"""
                        <div style="font-size:0.72rem;color:#7C3AED;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.3);border-radius:8px;padding:4px 8px;margin-top:4px;">
                          <b>Akumulasi Bonus Skill:</b> M:+{sb['M']} | E:+{sb['E']} | ENV:+{sb['ENV']} | QoL:+{sb['QoL']}
                        </div>
                        """
                    )

                # Panel Penyesuaian Nilai Poin Manual
                cur_mp = pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                if st.session_state.get("enable_manual_points", False):
                    render_html(
                        """
                        <div style="background:rgba(255,255,255,0.92);border:1.5px solid rgba(2,132,199,0.3);border-radius:10px;padding:6px 10px;margin-top:8px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="font-size:0.78rem;color:#0F2A1D;">🛠️ Tambah Nilai Poin Manual</b>
                            <span style="font-size:0.68rem;padding:2px 6px;border-radius:6px;background:rgba(2,132,199,0.12);color:#0284C7;font-weight:700;">Live Mod</span>
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

                st.write("")
                # --------------------------------------------------------------
                # 1. PROYEK DIBANGUN (120 PROYEK — MULTISELECT BERSIH)
                # --------------------------------------------------------------
                st.multiselect(
                    "Proyek Dibangun (120):",
                    options=project_id_options,
                    format_func=format_project_label,
                    key=f"widget_projects_{p_id}",
                    on_change=callback_sync_projects,
                    args=(p_id,),
                    help="Pilih kartu proyek yang telah dibangun di papan kota fisik.",
                )

                # Render 3D Glass Badges untuk Proyek Terpilih dengan Warna Kategori
                if pl["projects"]:
                    p_badges_html = '<div style="display:flex;flex-wrap:wrap;gap:5px;margin:6px 0 10px 0;">'
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
                    p_badges_html += '</div>'
                    render_html(p_badges_html)

                # --------------------------------------------------------------
                # 2. PERMANENT TECH (T1–T5) & TOMBOL AKSI 1X PER RONDE
                # --------------------------------------------------------------
                st.multiselect(
                    "Permanent Tech Dimiliki (T1–T5):",
                    options=tech_code_options,
                    format_func=format_tech_label,
                    key=f"widget_techs_{p_id}",
                    on_change=callback_sync_techs,
                    args=(p_id,),
                    help="Teknologi permanen yang dimiliki. Efek kartu hanya berlaku saat tombol aksi ditekan.",
                )

                if pl["techs"]:
                    render_html(
                        """
                        <div style="background:rgba(255,255,255,0.9);border:1.5px solid rgba(2,132,199,0.3);border-radius:10px;padding:6px 10px;margin-top:8px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="font-size:0.78rem;color:#0F2A1D;">Aksi Tech Card Dimiliki</b>
                            <span style="font-size:0.68rem;padding:2px 6px;border-radius:6px;background:rgba(2,132,199,0.12);color:#0284C7;font-weight:700;">1x / Ronde</span>
                          </div>
                        </div>
                        """
                    )
                    t_cols = st.columns(len(pl["techs"]) if len(pl["techs"]) <= 2 else 2, gap="small")
                    for t_idx, tc in enumerate(pl["techs"]):
                        t_clean = get_card_clean_name(tc)
                        is_used = tc in pl["active_techs_this_round"]

                        with t_cols[t_idx % len(t_cols)]:
                            if is_used:
                                st.button(
                                    f"⚡ {tc} [Sudah Dipakai]",
                                    key=f"btn_tech_{p_id}_{tc}",
                                    disabled=True,
                                    width="stretch",
                                    help=f"Aksi {tc} ({t_clean}) telah diaktifkan ronde ini. Reset di ronde berikutnya.",
                                )
                            else:
                                st.button(
                                    f"⚡ Pakai {t_clean}",
                                    key=f"btn_tech_{p_id}_{tc}",
                                    disabled=False,
                                    width="stretch",
                                    help=f"Aktifkan aksi {t_clean}.",
                                    on_click=callback_activate_tech,
                                    args=(p_id, tc),
                                    )

                # --------------------------------------------------------------
                # 3. CONSUMABLE SKILLS (S1–S5) & KONSUMSI 1X PAKAI
                # --------------------------------------------------------------
                st.multiselect(
                    "Skill Card di Tangan (S1–S5):",
                    options=skill_code_options,
                    format_func=format_skill_label,
                    key=f"widget_skills_{p_id}",
                    on_change=callback_sync_skills,
                    args=(p_id,),
                    help="Kartu skill yang dipegang pemain. Saat tombol aksi ditekan, kartu langsung terhapus (consumed).",
                )

                if pl["skills"]:
                    render_html(
                        """
                        <div style="background:rgba(255,255,255,0.9);border:1.5px solid rgba(124,58,237,0.3);border-radius:10px;padding:6px 10px;margin-top:8px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="font-size:0.78rem;color:#0F2A1D;">Pakai Skill (Sekali Pakai)</b>
                            <span style="font-size:0.68rem;padding:2px 6px;border-radius:6px;background:rgba(124,58,237,0.12);color:#7C3AED;font-weight:700;">Konsumsi</span>
                          </div>
                        </div>
                        """
                    )

                    # Khusus S1: Tampilkan dropdown Problem Card milik pemain untuk dihapus
                    if "S1" in pl["skills"]:
                        s1_name = get_card_clean_name("S1")
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
                                help="Hapus problem card terpilih dan konsumsi kartu S1.",
                            )
                        else:
                            st.caption("Pemain tidak memiliki Problem Card. Pakai S1 untuk Dana Darurat (+2 Semua Aspek):")
                            st.button(
                                "✨ Pakai S1 (Dana Darurat +2 All)",
                                key=f"btn_use_s1_fb_{p_id}",
                                width="stretch",
                                on_click=callback_use_s1_fallback,
                                args=(p_id,),
                            )

                    # Skill lainnya (S2, S3, S4, S5)
                    other_skills = [s for s in pl["skills"] if s != "S1"]
                    if other_skills:
                        s_cols = st.columns(len(other_skills) if len(other_skills) <= 2 else 2, gap="small")
                        for s_idx, sc in enumerate(other_skills):
                            s_clean = get_card_clean_name(sc)
                            with s_cols[s_idx % len(s_cols)]:
                                if sc == "S5":
                                    st.button(
                                        f"✨ Pakai {s_clean} (Kebal Event)",
                                        key=f"btn_use_s5_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s5,
                                        args=(p_id,),
                                        help="Aktifkan imunitas terhadap semua efek negatif Event Card ronde ini.",
                                    )
                                elif sc == "S2":
                                    st.button(
                                        f"✨ Pakai {s_clean} (+5 ENV)",
                                        key=f"btn_use_s2_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s2,
                                        args=(p_id,),
                                    )
                                elif sc == "S3":
                                    st.button(
                                        f"✨ Pakai {s_clean} (+5 M)",
                                        key=f"btn_use_s3_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s3,
                                        args=(p_id,),
                                    )
                                elif sc == "S4":
                                    st.button(
                                        f"✨ Pakai {s_clean} (+5 QoL)",
                                        key=f"btn_use_s4_{p_id}",
                                        width="stretch",
                                        on_click=callback_use_s4,
                                        args=(p_id,),
                                    )

                # --------------------------------------------------------------
                # 4. PROBLEM CARDS (PENALTI KRISIS GAGAL)
                # --------------------------------------------------------------
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
                    prob_badges_html = '<div style="display:flex;flex-wrap:wrap;gap:5px;margin:6px 0 10px 0;">'
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
                    prob_badges_html += '</div>'
                    render_html(prob_badges_html)

                # Kas Koin
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

                # Riwayat Aksi Pemakaian Terakhir
                if pl["tech_log"]:
                    last_act = pl["tech_log"][-1]
                    render_html(
                        f"""
                        <div style="font-size:0.71rem;color:#047857;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:4px 8px;margin-top:6px;">
                          <b>Riwayat Aksi:</b> {last_act}
                        </div>
                        """
                    )

                # Ringkasan Telemetri
                render_html(
                    f"""
                    <div style="background:rgba(255,255,255,0.88);border:1px solid #D6E4DA;border-radius:10px;padding:8px 10px;font-size:0.76rem;color:#4A5D52;margin-top:6px;line-height:1.4;">
                      <b>Telemetri:</b> <b>{len(pl['projects'])}</b> Proyek &nbsp;|&nbsp; <b>{len(pl['techs'])}</b> Tech<br/>
                      <b>{len(pl['skills'])}</b> Skill &nbsp;|&nbsp; <b>{len(pl['problems'])}</b> Krisis Gagal
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
with tab_audit:
    if not st.session_state.get("audit_triggered", False):
        # ----------------------------------------------------------------------
        # STATE 1: MENUNGGU INSTRUKSI AUDIT (STRICT LAZY LOADING)
        # ----------------------------------------------------------------------
        render_html(
            """
            <div style="background:rgba(255,255,255,0.85);backdrop-filter:blur(20px);border:1.5px solid rgba(255,255,255,0.95);border-radius:22px;padding:36px;text-align:center;box-shadow:0 14px 40px rgba(15,42,29,0.08);margin:16px 0 20px 0;">
              <div style="display:inline-block;padding:6px 18px;border-radius:999px;background:rgba(5,150,105,0.12);border:1px solid rgba(5,150,105,0.3);color:#047857;font-weight:800;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:12px;">
                Mode Siaga · Siap Eksekusi Final Audit
              </div>
              <h2 style="font-family:'Fredoka','Outfit',sans-serif;font-size:2.4rem;color:#0F2A1D;margin:0 0 10px 0;font-weight:800;">
                Final AI Audit &amp; Laporan Kota Masa Depan 2075
              </h2>
              <div style="max-width:760px;margin:0 auto 20px auto;color:#4A5D52;font-size:1.0rem;line-height:1.6;">
                Setelah 13 ronde berlangsung di papan permainan fisik, klik tombol di bawah untuk mengunci data,
                mengevaluasi ke-13 Global Event Rulebook secara otomatis, menghitung bonus tier sisa koin, menentukan peringkat dan tie-breaker resmi,
                serta menerbitkan Sertifikat Penghargaan Tata Kota 2075.
              </div>
            </div>
            """
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
        # ----------------------------------------------------------------------
        # STATE 2: AUDIT DIEKSEKUSI (FULL RESULTS, LEADERBOARD, & CERTIFICATES)
        # ----------------------------------------------------------------------
        top_ctrl_c1, top_ctrl_c2 = st.columns([7, 3])
        with top_ctrl_c1:
            render_html(
                """
                <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(5,150,105,0.12);border:1px solid rgba(5,150,105,0.35);border-radius:999px;padding:5px 14px;color:#047857;font-size:0.82rem;font-weight:800;letter-spacing:0.04em;">
                  <span>STATUS: FINAL AI AUDIT SELESAI DIEKSEKUSI</span>
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

        # Hitung skor lengkap dengan evaluasi ke-13 Global Event otomatis & bonus skill
        final_player_audits = []
        for idx in range(4):
            p_id = idx + 1
            pl = st.session_state.players[p_id]
            f_aud = compute_player_score(
                player_name=pl["name"],
                city_name=pl["city"],
                project_ids=pl["projects"],
                tech_codes=pl["techs"],
                failed_problem_ids=pl["problems"],
                coins=pl["coins"],
                used_skill_codes=pl["skills"],
                include_events=True,
                skill_bonus=pl["bonus_stats"],
                manual_delta=pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
            )
            final_player_audits.append(f_aud)

        # Evaluasi Otomatis 13 Global Event
        with st.container(border=True, key="panel_audit_events_auto"):
            ev_hdr1, ev_hdr2 = st.columns([7, 3])
            with ev_hdr1:
                st.markdown("#### Evaluasi Otomatis 13 Global Event (Round 1–13)")
                st.caption("Engine EcoNova menghitung dampak kumulatif seluruh Event Card dari Rulebook berdasarkan proyek dan teknologi yang dimiliki tiap pemain.")
            with ev_hdr2:
                render_html("<div style='text-align:right;padding-top:8px;'><span class='eco-pill eco-pill-env'>Auto-Evaluated Rulebook</span></div>")

            ev_cols = st.columns(4, gap="medium")
            for idx in range(4):
                aud = final_player_audits[idx]
                with ev_cols[idx]:
                    ev_d = aud.get("event_delta", {"M": 0, "E": 0, "ENV": 0, "QoL": 0})
                    ev_c = aud.get("event_coins", 0)
                    render_html(
                        f"""
                        <div style="background:rgba(255,255,255,0.85);border:1px solid #D6E4DA;border-radius:12px;padding:10px;font-size:0.78rem;">
                          <b style="color:#0F2A1D;">{aud['player_name']}</b> ({aud['city_name']})<br/>
                          <span style="color:#0369A1;font-weight:600;">Bonus Koin Event: +{ev_c}</span><br/>
                          <span style="color:#15803D;font-weight:600;">Dampak Event: M:{ev_d.get('M',0):+d} E:{ev_d.get('E',0):+d} ENV:{ev_d.get('ENV',0):+d} QoL:{ev_d.get('QoL',0):+d}</span>
                        </div>
                        """
                    )

            with st.expander("Detail Aturan & Log 13 Ronde Global Event", expanded=False):
                for round_no in range(1, 14):
                    ev = EVENT_BY_ROUND.get(round_no, EVENT_CARDS[0])
                    st.markdown(
                        f"**Ronde {round_no}: {ev['name']}** — *{ev['description']}* (Efek: `{ev.get('effect_summary', ev.get('effect_str', ''))}`)"
                    )

        # Leaderboard & Podium Juara
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
        podium_accents = ["#F59E0B", "#06B6D4", "#F59E0B", "#10B981"]

        for r_idx, p_res in enumerate(ranked_players):
            is_champ = r_idx == 0
            card_cls = "eco-card-champion" if is_champ else "eco-card"
            arch = p_res["archetype"]
            accent_pod = podium_accents[r_idx]

            tb_note = ""
            if p_res.get("tie_breaker_reason"):
                tb_note = (
                    f'<div style="background:rgba(245,158,11,0.18);border:1px solid #F59E0B;color:#B45309;'
                    f'border-radius:10px;padding:6px 10px;font-size:0.76rem;font-weight:700;margin-top:8px;">'
                    f'Tie-Breaker: {p_res["tie_breaker_reason"]}</div>'
                )

            with podium_cols[r_idx]:
                b_m = build_aspect_progress_html("Mobility", "M", p_res["M"], p_res["delta_M"], "#06B6D4")
                b_e = build_aspect_progress_html("Energy", "E", p_res["E"], p_res["delta_E"], "#F59E0B")
                b_env = build_aspect_progress_html("Environment", "ENV", p_res["ENV"], p_res["delta_ENV"], "#10B981")
                b_qol = build_aspect_progress_html("Quality of Life", "QoL", p_res["QoL"], p_res["delta_QoL"], "#F43F5E")

                render_html(
                    f"""
                    <div class="{card_cls}" style="margin-bottom:12px;border-top:4px solid {accent_pod};">
                      <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span class="eco-pill" style="background:rgba(245,158,11,0.18);color:#B45309;font-weight:800;border:1px solid rgba(245,158,11,0.5);">
                          {medal_titles[r_idx]}
                        </span>
                        <span style="font-family:'Outfit',sans-serif;font-size:0.75rem;font-weight:700;color:#6B7F73;">
                          Rank #{p_res['rank']}
                        </span>
                      </div>
                      <h4 style="margin:10px 0 2px 0;font-size:1.25rem;color:#0F2A1D;font-family:'Outfit',sans-serif;font-weight:800;">
                        {p_res['city_name']}
                      </h4>
                      <div style="font-size:0.86rem;color:#4A5D52;font-weight:600;margin-bottom:8px;">
                        {p_res['player_name']}
                      </div>
                      <div style="text-align:center;background:linear-gradient(135deg,rgba(16,185,129,0.14) 0%,rgba(6,182,212,0.14) 100%);border:1px solid rgba(16,185,129,0.45);border-radius:12px;padding:8px;margin-bottom:10px;">
                        <div style="font-family:'Outfit',sans-serif;font-size:0.7rem;color:#4A5D52;font-weight:700;text-transform:uppercase;">Average Score</div>
                        <div class="stat-outfit" style="font-size:1.9rem;font-weight:900;color:#047857;line-height:1.1;">{p_res['avg_score']:.2f}</div>
                        <div style="font-size:0.78rem;font-weight:700;color:{arch['color']};margin-top:2px;">{arch['name']}</div>
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

        # Matriks Perbandingan & Radar Plotly
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
                    st.plotly_chart(fig, width='stretch')

        # ----------------------------------------------------------------------
        # SERTIFIKAT AUDIT & LAPORAN NARATIF KOTA MASA DEPAN (TAHUN 2075)
        # Redesain Premium Futuristic Urban Planning Award Certificate
        # ----------------------------------------------------------------------
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
                            <div style="text-align:center;background:rgba(255,255,255,0.92);border:2px solid {arch['color']};border-radius:18px;padding:12px 22px;box-shadow:0 6px 20px rgba(0,0,0,0.05);">
                              <div style="font-family:'Outfit',sans-serif;font-size:0.72rem;color:#4A5D52;font-weight:800;text-transform:uppercase;letter-spacing:0.05em;">Skor Rata-Rata Akhir</div>
                              <div class="stat-outfit" style="font-size:2.5rem;font-weight:900;color:{arch['color']};line-height:1.05;margin:4px 0;">{p_res['avg_score']:.2f}</div>
                              <div style="font-size:0.75rem;font-weight:700;color:#059669;">Skala 0 – 100</div>
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
with tab_gm:
    col_gm_side, col_gm_chat = st.columns([3.3, 6.7], gap="large")

    # --------------------------------------------------------------------------
    # KOLOM KIRI (3.3): AI PERSONA, QUICK PROMPTS, & INSPEKTUR ATURAN
    # --------------------------------------------------------------------------
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
                quick_q = "Sebutkan efek pasif Permanent Technology T1 sampai T5 dan Consumable Skill S1 sampai S5!"
            if qc4.button("Solusi Krisis", width="stretch", key="qp_prob"):
                quick_q = "Bagaimana aturan menyelesaikan Problem Card dengan koin vs teknologi/skill dan penaltinya?"

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
                    - **3 Action Points (AP):** Pindah distrik = `1 AP`, Bangun Proyek / Ambil Tech = `1 AP`, Selesaikan Krisis via Tech = `2 AP`, Bayar Koin = `1 AP`.
                    - **City Center:** Tiba di City Center = `+3 Koin` (maks 1x per ronde).
                    - **Bonus Koin Akhir:** Tiap `20 Koin penuh` = `+5 poin ke 4 aspek`.
                    - **Tie-Breaker:** `Skor Rata-Rata` → `Jumlah Proyek` → `Tech Dimiliki` → `Sisa Koin`.
                    """
                )

    # --------------------------------------------------------------------------
    # KOLOM KANAN (6.7): MODERN AI CHAT CONSOLE
    # --------------------------------------------------------------------------
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
                for msg_idx, msg in enumerate(st.session_state.chat_history):
                    role = msg["role"]
                    content_html = format_chat_markdown_to_html(msg["content"])

                    if role == "user":
                        render_html(
                            f"""
                            <div class="chat-row-user">
                              <div class="chat-bubble-user">
                                <div class="chat-sender-tag" style="color:#0369A1;justify-content:flex-end;">
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
