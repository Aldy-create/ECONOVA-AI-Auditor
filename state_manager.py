"""
state_manager.py — State Persistence, Callbacks & Game Mechanics Engine
Mengelola seluruh st.session_state, sinkronisasi widget, komitmen/rollback koin event,
validasi kombinasi teknologi T1–T5, konsumsi kartu skill S1–S5, dan navigasi tab aktif.
"""

import copy
import importlib
import json
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

import cards_data as _cards_data_mod

if not hasattr(_cards_data_mod, "get_resolvable_problems_for_tech") or not hasattr(_cards_data_mod, "recommend_cards_for_player"):
    importlib.reload(_cards_data_mod)

from cards_data import (
    DISTRICT_META,
    EVENT_BY_ID,
    PERMANENT_TECH_BY_CODE,
    PROBLEM_BY_ID,
    PROJECT_BY_ID,
    SKILL_BY_CODE,
    compute_player_score,
    evaluate_single_event_live,
    get_resolvable_problems_for_tech,
)

TAB_OPTIONS = [
    "Tab 1: Live Tracker",
    "Tab 2: Final Audit",
    "Tab 3: AI Game Master",
]

WELCOME_CHAT_MESSAGE = (
    "Hai! Aku **EcoBot**, asisten board game **EcoNova** kamu.\n\n"
    "Mau tanya aturan main, efek kartu, cara menang, atau soal game ini? "
    "Klik tombol cepat di samping atau langsung ketik aja ya!"
)

TECH_ACTION_META: Dict[str, Dict[str, Any]] = {
    "T1": {
        "name": "Solar Engineering",
        "short_label": "+2 E",
        "solves_problems": ["PR03", "PR08", "PR11", "PR17", "PR20"],
        "passive_desc": "+2 Energy. Dipakai maksimal 1x per ronde (AP dihitung fisik di meja) & kartu tetap dimiliki.",
    },
    "T2": {
        "name": "AI Urban System",
        "short_label": "+1 M, +1 QoL",
        "solves_problems": ["PR02", "PR08", "PR10", "PR16", "PR19"],
        "passive_desc": "+1 M, +1 QoL. Dipakai maksimal 1x per ronde (AP dihitung fisik di meja) & kartu tetap dimiliki.",
    },
    "T3": {
        "name": "Circular Materials",
        "short_label": "+2 ENV",
        "solves_problems": ["PR01", "PR07", "PR11", "PR15", "PR16", "PR18", "PR20"],
        "passive_desc": "+2 ENV. Dipakai maksimal 1x per ronde (AP dihitung fisik di meja) & kartu tetap dimiliki.",
    },
    "T4": {
        "name": "Electric Mobility",
        "short_label": "+2 M",
        "solves_problems": ["PR09"],
        "passive_desc": "+2 Mobility. Dipakai maksimal 1x per ronde (AP dihitung fisik di meja) & kartu tetap dimiliki.",
    },
    "T5": {
        "name": "Water Purification",
        "short_label": "+1 ENV, +1 QoL",
        "solves_problems": ["PR04", "PR05", "PR07", "PR13", "PR20"],
        "passive_desc": "+1 ENV, +1 QoL. Dipakai maksimal 1x per ronde (AP dihitung fisik di meja) & kartu tetap dimiliki.",
    },
    "S1": {
        "name": "Emergency Response",
        "short_label": "Hapus 1 Problem",
        "solves_problems": "ALL",
        "passive_desc": "Hapus 1 Problem Card aktif (sekali pakai lalu terhapus / consumed).",
    },
    "S2": {
        "name": "Carbon Capture Boost",
        "short_label": "+5 ENV",
        "solves_problems": ["PR01", "PR11"],
        "passive_desc": "+5 Environment atau amankan PR01/PR11 (sekali pakai lalu terhapus).",
    },
    "S3": {
        "name": "Traffic Override",
        "short_label": "+5 M",
        "solves_problems": ["PR02"],
        "passive_desc": "+5 Mobility atau amankan PR02 (sekali pakai lalu terhapus).",
    },
    "S4": {
        "name": "Public Health Campaign",
        "short_label": "+5 QoL",
        "solves_problems": ["PR06"],
        "passive_desc": "+5 Quality of Life atau amankan PR06 (sekali pakai lalu terhapus).",
    },
    "S5": {
        "name": "Cyber Shield",
        "short_label": "Kebal Penalti Event",
        "solves_problems": ["PR10"],
        "passive_desc": "Kebal penalti Event ronde ini atau amankan PR10 (sekali pakai lalu terhapus).",
    },
}


def init_session_state() -> None:
    """Inisialisasi session state murni baseline dengan struktur st.session_state.players."""
    if "active_tab" not in st.session_state or st.session_state.active_tab not in TAB_OPTIONS:
        st.session_state.active_tab = "Tab 1: Live Tracker"

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": WELCOME_CHAT_MESSAGE}]

    if "current_round" not in st.session_state:
        st.session_state.current_round = 1

    if "used_events" not in st.session_state:
        st.session_state.used_events = []

    if "round_event_history" not in st.session_state:
        st.session_state.round_event_history = []

    if "selected_event_id" not in st.session_state:
        st.session_state.selected_event_id = None

    if "audit_triggered" not in st.session_state:
        st.session_state.audit_triggered = False

    if "audit_event_mode" not in st.session_state:
        st.session_state.audit_event_mode = "Gunakan Riwayat Event Ronde Aktual"

    if "enable_manual_points" not in st.session_state:
        st.session_state.enable_manual_points = False

    if "active_player_id" not in st.session_state:
        st.session_state.active_player_id = 1

    if "action_history" not in st.session_state:
        st.session_state.action_history = []

    if "last_deltas" not in st.session_state:
        st.session_state.last_deltas = {p_id: {} for p_id in range(1, 5)}

    if "quick_card_category" not in st.session_state:
        st.session_state.quick_card_category = "Project"

    if "quick_district_filter" not in st.session_state:
        st.session_state.quick_district_filter = None

    if "score_history" not in st.session_state:
        st.session_state.score_history = [
            {"round": 1, "scores": {1: 50.0, 2: 50.0, 3: 50.0, 4: 50.0}}
        ]

    if "session_import_feedback" not in st.session_state:
        st.session_state.session_import_feedback = None

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
                "committed_event_coins": 0,
                "manual_points": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "active_techs_this_round": [],
                "tech_activations_this_round": [],
                "accumulated_tech_stats": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "bonus_stats": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "accumulated_event_delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "accumulated_event_coins": 0,
                "immune_this_round": False,
                "tech_log": [],
            }
        if "manual_points" not in st.session_state.players[p_id]:
            st.session_state.players[p_id]["manual_points"] = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
        if "committed_event_coins" not in st.session_state.players[p_id]:
            st.session_state.players[p_id]["committed_event_coins"] = 0
        if "accumulated_tech_stats" not in st.session_state.players[p_id]:
            st.session_state.players[p_id]["accumulated_tech_stats"] = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
        if "tech_activations_this_round" not in st.session_state.players[p_id]:
            st.session_state.players[p_id]["tech_activations_this_round"] = []

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


# ------------------------------------------------------------------------------
# CALLBACKS NAVIGASI TAB & WIDGET SYNC
# ------------------------------------------------------------------------------
def callback_switch_tab(tab_name: str) -> None:
    """Berpindah antar tab secara langsung via session state."""
    if tab_name in TAB_OPTIONS:
        st.session_state.active_tab = tab_name


def clear_certificate_pdf_cache() -> None:
    """Menghapus cache sertifikat PDF 2075 di session_state agar selalu sinkron dengan skor terbaru."""
    stale_keys = [k for k in list(st.session_state.keys()) if str(k).startswith("cert_pdf_")]
    for k in stale_keys:
        st.session_state.pop(k, None)


def callback_lock_and_open_audit() -> None:
    """Mengunci simulasi dari Tab 1 dan langsung otomatis berpindah ke Tab 2: Final Audit."""
    clear_certificate_pdf_cache()
    st.session_state.audit_triggered = True
    st.session_state.active_tab = "Tab 2: Final Audit"


def callback_set_active_player(p_id: int) -> None:
    """Mengubah pemain yang sedang mendapat giliran aktif di meja."""
    if p_id in (1, 2, 3, 4):
        st.session_state.active_player_id = p_id


def callback_sync_name(p_id: int) -> None:
    val = st.session_state.get(f"widget_name_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["name"] = str(val).strip() or f"Pemain {p_id}"


def callback_sync_city(p_id: int) -> None:
    val = st.session_state.get(f"widget_city_{p_id}")
    if val is not None:
        st.session_state.players[p_id]["city"] = str(val).strip() or f"Kota {p_id}"


def _capture_undo_snapshot() -> Dict[str, Any]:
    """Mengambil salinan utuh state permainan sebelum aksi dijalankan untuk fitur Undo."""
    return {
        "current_round": int(st.session_state.get("current_round", 1)),
        "selected_event_id": st.session_state.get("selected_event_id"),
        "used_events": list(st.session_state.get("used_events", [])),
        "round_event_history": copy.deepcopy(st.session_state.get("round_event_history", [])),
        "tech_used_this_round": copy.deepcopy(st.session_state.get("tech_used_this_round", {})),
        "active_player_id": int(st.session_state.get("active_player_id", 1)),
        "players": copy.deepcopy(st.session_state.get("players", {})),
        "last_deltas": copy.deepcopy(st.session_state.get("last_deltas", {i: {} for i in range(1, 5)})),
        "score_history": copy.deepcopy(st.session_state.get("score_history", [])),
    }


def _compute_current_scores_map(active_event_id: Optional[str] = None) -> Dict[int, float]:
    """Menghitung Average Score keempat pemain saat ini untuk pencatatan score_history."""
    scores_map: Dict[int, float] = {}
    for p_id in range(1, 5):
        pl = st.session_state.players.get(p_id, {})
        res = compute_player_score(
            player_name=pl.get("name", f"Pemain {p_id}"),
            city_name=pl.get("city", f"Kota {p_id}"),
            project_ids=pl.get("projects", []),
            tech_codes=pl.get("techs", []),
            failed_problem_ids=pl.get("problems", []),
            coins=int(pl.get("coins", 5)),
            used_skill_codes=pl.get("skills", []),
            include_events=False,
            active_event_id=active_event_id,
            skill_bonus=pl.get("bonus_stats", {}),
            active_tech_codes=pl.get("active_techs_this_round", []),
            accumulated_event_delta=pl.get("accumulated_event_delta", {}),
            accumulated_event_coins=0,
            is_immune=bool(pl.get("immune_this_round", False)),
            manual_delta=pl.get("manual_points", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
            accumulated_tech_stats=pl.get("accumulated_tech_stats", {"M": 0, "E": 0, "ENV": 0, "QoL": 0}),
        )
        scores_map[p_id] = round(float(res["avg_score"]), 2)
    return scores_map


def _upsert_score_history(round_num: int, scores_map: Dict[int, float]) -> None:
    """Menyimpan atau memperbarui snapshot Average Score keempat pemain pada ronde tertentu."""
    if "score_history" not in st.session_state:
        st.session_state.score_history = []
    hist = st.session_state.score_history
    for entry in hist:
        if int(entry.get("round", 0)) == int(round_num):
            entry["scores"] = dict(scores_map)
            return
    hist.append({"round": int(round_num), "scores": dict(scores_map)})
    hist.sort(key=lambda e: int(e.get("round", 0)))


def callback_select_board_tile(tile_name: str) -> None:
    """Memilih petak pada Peta Mini 3x3: menyaring Project per distrik atau membuka Tech di City Center."""
    if tile_name == "City Center":
        st.session_state.quick_district_filter = None
        st.session_state.quick_card_category = "Tech"
        st.session_state.quick_card_picker = "T1"
    elif tile_name in DISTRICT_META:
        st.session_state.quick_district_filter = tile_name
        st.session_state.quick_card_category = "Project"
        dist_cards = [pid for pid, card in PROJECT_BY_ID.items() if card.get("district") == tile_name]
        if dist_cards and st.session_state.get("quick_card_picker") not in dist_cards:
            st.session_state.quick_card_picker = dist_cards[0]


def callback_reset_district_filter() -> None:
    """Mereset filter distrik pada Peta Mini 3x3 agar seluruh kartu Proyek tampil kembali."""
    st.session_state.quick_district_filter = None


def callback_pick_recommended_card(card_id: str, category: str) -> None:
    """Memuat kartu dari Rekomendasi Taktis langsung ke pratinjau Meja Aksi Kartu Cepat."""
    if category == "Project" and card_id in PROJECT_BY_ID:
        st.session_state.quick_district_filter = None
        st.session_state.quick_card_category = "Project"
        st.session_state.quick_card_picker = card_id
    elif category == "Tech" and card_id in PERMANENT_TECH_BY_CODE:
        st.session_state.quick_district_filter = None
        st.session_state.quick_card_category = "Tech"
        st.session_state.quick_card_picker = card_id


def _format_delta_summary(deltas: Dict[str, int]) -> str:
    """Mengubah dict perubahan stat menjadi ringkasan teks singkat seperti '+2 E, -1 ENV'."""
    parts = []
    for k in ("M", "E", "ENV", "QoL"):
        v = int(deltas.get(k, 0))
        if v != 0:
            parts.append(f"{v:+d} {k}")
    c_val = int(deltas.get("coins", 0))
    if c_val != 0:
        parts.append(f"{c_val:+d} Koin")
    return ", ".join(parts) if parts else "Status diperbarui"


def _record_action_entry(
    round_num: int,
    player_id: Optional[int],
    player_name: str,
    card_id: str,
    card_name: str,
    category: str,
    deltas: Dict[str, int],
    snapshot: Dict[str, Any],
) -> None:
    """Mencatat aksi ke action_history dan menyimpan last_deltas pemain terdampak."""
    if "action_history" not in st.session_state:
        st.session_state.action_history = []
    if "last_deltas" not in st.session_state:
        st.session_state.last_deltas = {i: {} for i in range(1, 5)}

    clean_deltas = {k: int(deltas.get(k, 0)) for k in ("M", "E", "ENV", "QoL", "coins") if int(deltas.get(k, 0)) != 0}
    if player_id in (1, 2, 3, 4) and clean_deltas:
        st.session_state.last_deltas[player_id] = {
            "round": int(round_num),
            "card": card_name,
            "deltas": clean_deltas,
        }

    st.session_state.action_history.append(
        {
            "round": int(round_num),
            "player_id": player_id,
            "player_name": player_name,
            "card_id": card_id,
            "card_name": card_name,
            "category": category,
            "deltas": clean_deltas,
            "delta_summary": _format_delta_summary(clean_deltas),
            "snapshot": snapshot,
        }
    )
    if len(st.session_state.action_history) > 40:
        st.session_state.action_history = st.session_state.action_history[-40:]


def _remove_last_occurrence(items: List[str], target_id: str) -> bool:
    """Menghapus hanya 1 kemunculan terakhir target_id dari list agar salinan ganda lainnya tetap aman."""
    for idx in range(len(items) - 1, -1, -1):
        if items[idx] == target_id:
            items.pop(idx)
            return True
    return False


def callback_undo_last_action() -> None:
    """Membatalkan aksi terakhir dari action_history (hapus hanya 1 salinan terakhir untuk kartu ganda)."""
    history = st.session_state.get("action_history", [])
    if not history:
        return
    last_entry = history.pop()
    snap = last_entry.get("snapshot", {})
    clear_certificate_pdf_cache()

    if not snap:
        pid = last_entry.get("player_id")
        cid = last_entry.get("card_id")
        cat = last_entry.get("category")
        cat_to_key = {"Project": "projects", "Tech": "techs", "Skill": "skills", "Problem": "problems"}
        lkey = cat_to_key.get(str(cat))
        if pid in st.session_state.players and lkey and cid:
            pl = st.session_state.players[pid]
            if _remove_last_occurrence(pl[lkey], str(cid)):
                st.session_state[f"widget_{lkey}_{pid}"] = list(pl[lkey])
        return

    st.session_state.current_round = int(snap.get("current_round", 1))
    st.session_state.selected_event_id = snap.get("selected_event_id")
    st.session_state.widget_event_picker = st.session_state.selected_event_id
    st.session_state.used_events = list(snap.get("used_events", []))
    st.session_state.round_event_history = copy.deepcopy(snap.get("round_event_history", []))
    st.session_state.tech_used_this_round = copy.deepcopy(snap.get("tech_used_this_round", {}))
    st.session_state.active_player_id = int(snap.get("active_player_id", 1))
    st.session_state.players = copy.deepcopy(snap.get("players", {}))
    st.session_state.last_deltas = copy.deepcopy(snap.get("last_deltas", {i: {} for i in range(1, 5)}))
    if "score_history" in snap and snap["score_history"]:
        st.session_state.score_history = copy.deepcopy(snap["score_history"])

    for p_id in range(1, 5):
        pl = st.session_state.players[p_id]
        st.session_state[f"widget_name_{p_id}"] = pl["name"]
        st.session_state[f"widget_city_{p_id}"] = pl["city"]
        st.session_state[f"widget_projects_{p_id}"] = list(pl["projects"])
        st.session_state[f"widget_techs_{p_id}"] = list(pl["techs"])
        st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
        st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])
        st.session_state[f"widget_coins_{p_id}"] = int(pl["coins"])
        for stat_key in ("M", "E", "ENV", "QoL"):
            st.session_state[f"widget_man_{stat_key}_{p_id}"] = int(pl.get("manual_points", {}).get(stat_key, 0))


def callback_apply_quick_card(p_id: int, category: str, card_id: Optional[str]) -> None:
    """Menerapkan kartu dari panel aksi cepat terpadu ke pemain aktif (mendukung kartu ganda/stacking)."""
    if not card_id or p_id not in st.session_state.players:
        return
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    snap = _capture_undo_snapshot()
    clear_certificate_pdf_cache()

    if category == "Project" and card_id in PROJECT_BY_ID:
        card = PROJECT_BY_ID[card_id]
        pl["projects"].append(card_id)
        st.session_state[f"widget_projects_{p_id}"] = list(pl["projects"])
        deltas = {k: int(card.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}
        cnt = pl["projects"].count(card_id)
        pl["tech_log"].append(f"R{curr_r}: Bangun Proyek [{card_id}] {card['name']}" + (f" ({cnt}x)" if cnt > 1 else ""))
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Project", deltas, snap)

    elif category == "Tech" and card_id in PERMANENT_TECH_BY_CODE:
        card = PERMANENT_TECH_BY_CODE[card_id]
        pl["techs"].append(card_id)
        st.session_state[f"widget_techs_{p_id}"] = list(pl["techs"])
        cnt = pl["techs"].count(card_id)
        pl["tech_log"].append(f"R{curr_r}: Tambah Tech [{card_id}] {card['name']}" + (f" ({cnt}x)" if cnt > 1 else ""))
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Tech", {}, snap)

    elif category == "Skill" and card_id in SKILL_BY_CODE:
        card = SKILL_BY_CODE[card_id]
        pl["skills"].append(card_id)
        st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
        cnt = pl["skills"].count(card_id)
        pl["tech_log"].append(f"R{curr_r}: Tambah Skill [{card_id}] {card['name']}" + (f" ({cnt}x)" if cnt > 1 else ""))
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Skill", {}, snap)

    elif category == "Problem" and card_id in PROBLEM_BY_ID:
        card = PROBLEM_BY_ID[card_id]
        pl["problems"].append(card_id)
        st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])
        deltas = {k: int(card.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}
        cnt = pl["problems"].count(card_id)
        pl["tech_log"].append(f"R{curr_r}: Catat Krisis [{card_id}] {card['name']}" + (f" ({cnt}x)" if cnt > 1 else ""))
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Problem", deltas, snap)


def callback_add_player_card(p_id: int, cat_key: str, card_id: Optional[str] = None) -> None:
    """Menambahkan 1 salinan kartu pada panel Kelola Kartu & Kas (mendukung duplikat)."""
    key_to_cat = {
        "projects": "Project",
        "techs": "Tech",
        "skills": "Skill",
        "problems": "Problem",
    }
    category = key_to_cat.get(cat_key)
    if not category:
        return
    chosen_id = card_id or st.session_state.get(f"add_sel_{cat_key}_{p_id}")
    if chosen_id:
        callback_apply_quick_card(p_id, category, str(chosen_id))


def callback_remove_one_player_card(p_id: int, cat_key: str, card_id: str) -> None:
    """Menghapus hanya 1 salinan terakhir kartu tertentu dari pemain tanpa menghapus salinan lain."""
    if p_id not in st.session_state.players or cat_key not in ("projects", "techs", "skills", "problems"):
        return
    pl = st.session_state.players[p_id]
    if card_id not in pl[cat_key]:
        return

    snap = _capture_undo_snapshot()
    clear_certificate_pdf_cache()
    if not _remove_last_occurrence(pl[cat_key], card_id):
        return
    st.session_state[f"widget_{cat_key}_{p_id}"] = list(pl[cat_key])

    curr_r = int(st.session_state.current_round)
    cat_label_map = {
        "projects": ("Project", PROJECT_BY_ID),
        "techs": ("Tech", PERMANENT_TECH_BY_CODE),
        "skills": ("Skill", SKILL_BY_CODE),
        "problems": ("Problem", PROBLEM_BY_ID),
    }
    cat_name, lookup = cat_label_map[cat_key]
    card = lookup.get(card_id, {})
    c_name = card.get("name", card_id)
    deltas = (
        {k: -int(card.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}
        if cat_key in ("projects", "problems")
        else {}
    )
    pl["tech_log"].append(f"R{curr_r}: Hapus 1x [{card_id}] {c_name}")
    _record_action_entry(
        curr_r,
        p_id,
        f"P{p_id} · {pl['city']}",
        card_id,
        f"Hapus 1x {c_name}",
        cat_name,
        deltas,
        snap,
    )


def callback_sync_projects(p_id: int) -> None:
    val = st.session_state.get(f"widget_projects_{p_id}")
    if val is not None:
        old_list = list(st.session_state.players[p_id]["projects"])
        new_list = list(val)
        if old_list != new_list:
            snap = _capture_undo_snapshot()
            st.session_state.players[p_id]["projects"] = new_list
            added = [x for x in new_list if x not in old_list]
            if added:
                cid = added[-1]
                card = PROJECT_BY_ID.get(cid, {})
                deltas = {k: int(card.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}
                pl = st.session_state.players[p_id]
                _record_action_entry(
                    int(st.session_state.current_round),
                    p_id,
                    f"P{p_id} · {pl['city']}",
                    cid,
                    card.get("name", cid),
                    "Project",
                    deltas,
                    snap,
                )


def callback_sync_techs(p_id: int) -> None:
    val = st.session_state.get(f"widget_techs_{p_id}")
    if val is not None:
        old_list = list(st.session_state.players[p_id]["techs"])
        new_list = list(val)
        if old_list != new_list:
            snap = _capture_undo_snapshot()
            st.session_state.players[p_id]["techs"] = new_list
            added = [x for x in new_list if x not in old_list]
            if added:
                cid = added[-1]
                card = PERMANENT_TECH_BY_CODE.get(cid, {})
                pl = st.session_state.players[p_id]
                _record_action_entry(
                    int(st.session_state.current_round),
                    p_id,
                    f"P{p_id} · {pl['city']}",
                    cid,
                    card.get("name", cid),
                    "Tech",
                    {},
                    snap,
                )


def callback_sync_skills(p_id: int) -> None:
    val = st.session_state.get(f"widget_skills_{p_id}")
    if val is not None:
        old_list = list(st.session_state.players[p_id]["skills"])
        new_list = list(val)
        if old_list != new_list:
            snap = _capture_undo_snapshot()
            st.session_state.players[p_id]["skills"] = new_list
            added = [x for x in new_list if x not in old_list]
            if added:
                cid = added[-1]
                card = SKILL_BY_CODE.get(cid, {})
                pl = st.session_state.players[p_id]
                _record_action_entry(
                    int(st.session_state.current_round),
                    p_id,
                    f"P{p_id} · {pl['city']}",
                    cid,
                    card.get("name", cid),
                    "Skill",
                    {},
                    snap,
                )


def callback_sync_problems(p_id: int) -> None:
    val = st.session_state.get(f"widget_problems_{p_id}")
    if val is not None:
        old_list = list(st.session_state.players[p_id]["problems"])
        new_list = list(val)
        if old_list != new_list:
            snap = _capture_undo_snapshot()
            st.session_state.players[p_id]["problems"] = new_list
            added = [x for x in new_list if x not in old_list]
            if added:
                cid = added[-1]
                card = PROBLEM_BY_ID.get(cid, {})
                deltas = {k: int(card.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}
                pl = st.session_state.players[p_id]
                _record_action_entry(
                    int(st.session_state.current_round),
                    p_id,
                    f"P{p_id} · {pl['city']}",
                    cid,
                    card.get("name", cid),
                    "Problem",
                    deltas,
                    snap,
                )


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
    new_ev = st.session_state.get("widget_event_picker")
    if new_ev != st.session_state.get("selected_event_id"):
        snap = _capture_undo_snapshot()
        st.session_state.selected_event_id = new_ev
        if new_ev and new_ev in EVENT_BY_ID:
            ev = EVENT_BY_ID[new_ev]
            _record_action_entry(
                int(st.session_state.current_round),
                None,
                "Semua Pemain",
                new_ev,
                ev["name"],
                "Event",
                {k: int(ev.get(k, 0)) for k in ("M", "E", "ENV", "QoL")},
                snap,
            )


def callback_next_round() -> None:
    snap = _capture_undo_snapshot()
    curr_ev = st.session_state.selected_event_id
    has_valid_ev = bool(curr_ev and curr_ev in EVENT_BY_ID)
    prev_round = int(st.session_state.current_round)
    commit_entry: Dict[str, Any] = {
        "round": prev_round,
        "event_id": curr_ev if has_valid_ev else None,
        "players": {},
    }

    for p_id in range(1, 5):
        pl = st.session_state.players[p_id]
        ev_delta = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
        ev_coins = 0

        if has_valid_ev:
            is_imm = pl.get("immune_this_round", False)
            single_ev = evaluate_single_event_live(
                curr_ev, pl["projects"], pl["techs"], is_immune=is_imm
            )
            ev_delta = dict(single_ev["delta"])
            for k in ("M", "E", "ENV", "QoL"):
                pl["accumulated_event_delta"][k] += ev_delta[k]

            ev_coins = int(single_ev["coins"])
            if ev_coins != 0:
                pl["coins"] = max(0, int(pl["coins"]) + ev_coins)
                pl["committed_event_coins"] = max(0, int(pl.get("committed_event_coins", 0)) + ev_coins)
                st.session_state[f"widget_coins_{p_id}"] = pl["coins"]

            combined_ev_delta = dict(ev_delta)
            if ev_coins != 0:
                combined_ev_delta["coins"] = ev_coins
            if any(combined_ev_delta.values()):
                st.session_state.last_deltas[p_id] = {
                    "round": prev_round,
                    "card": EVENT_BY_ID[curr_ev]["name"],
                    "deltas": {k: v for k, v in combined_ev_delta.items() if v != 0},
                }

        commit_entry["players"][p_id] = {
            "delta": ev_delta,
            "coins": ev_coins,
            "active_techs": list(pl.get("active_techs_this_round", [])),
            "tech_activations": list(pl.get("tech_activations_this_round", [])),
        }

    if has_valid_ev and curr_ev not in st.session_state.used_events:
        st.session_state.used_events.append(curr_ev)

    st.session_state.round_event_history.append(commit_entry)

    # Catat skor penutup ronde berjalan (setelah komit Event) & skor awal ronde baru
    _upsert_score_history(prev_round, _compute_current_scores_map(active_event_id=None))

    if st.session_state.current_round < 13:
        st.session_state.current_round += 1

    st.session_state.selected_event_id = None
    if "widget_event_picker" in st.session_state:
        st.session_state.widget_event_picker = None

    st.session_state.tech_used_this_round = {
        p_id: {t: False for t in ["T1", "T2", "T3", "T4", "T5"]} for p_id in range(1, 5)
    }
    for p_id in range(1, 5):
        st.session_state.players[p_id]["active_techs_this_round"] = []
        st.session_state.players[p_id]["tech_activations_this_round"] = []
        st.session_state.players[p_id]["immune_this_round"] = False

    if int(st.session_state.current_round) != prev_round:
        _upsert_score_history(int(st.session_state.current_round), _compute_current_scores_map(active_event_id=None))

    ev_label = EVENT_BY_ID[curr_ev]["name"] if has_valid_ev else "Tanpa Event"
    _record_action_entry(
        prev_round,
        None,
        "Semua Pemain",
        curr_ev or f"R{prev_round}",
        f"Selesai Ronde {prev_round} ({ev_label})",
        "Ronde",
        {},
        snap,
    )


def callback_prev_round() -> None:
    if st.session_state.current_round > 1:
        st.session_state.current_round -= 1

        for p_id in range(1, 5):
            pl = st.session_state.players[p_id]
            if "accumulated_tech_stats" not in pl:
                pl["accumulated_tech_stats"] = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
            for act in pl.get("tech_activations_this_round", []):
                act_delta = act.get("delta", {})
                for k in ("M", "E", "ENV", "QoL"):
                    pl["accumulated_tech_stats"][k] -= int(act_delta.get(k, 0))
                spid = act.get("solved_problem")
                if spid and spid not in pl["problems"]:
                    pl["problems"].append(spid)
                    if f"widget_problems_{p_id}" in st.session_state:
                        st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])
            pl["tech_activations_this_round"] = []
            pl["active_techs_this_round"] = []

        if st.session_state.get("round_event_history"):
            last_commit = st.session_state.round_event_history.pop()
            restored_ev = last_commit.get("event_id")
            for p_id, p_commit in last_commit.get("players", {}).items():
                pl = st.session_state.players[p_id]
                for k in ("M", "E", "ENV", "QoL"):
                    pl["accumulated_event_delta"][k] -= int(p_commit["delta"].get(k, 0))
                c_delta = int(p_commit.get("coins", 0))
                if c_delta != 0:
                    pl["coins"] = max(0, int(pl["coins"]) - c_delta)
                    pl["committed_event_coins"] = max(0, int(pl.get("committed_event_coins", 0)) - c_delta)
                    st.session_state[f"widget_coins_{p_id}"] = pl["coins"]

                restored_active = list(p_commit.get("active_techs", []))
                pl["active_techs_this_round"] = restored_active
                pl["tech_activations_this_round"] = list(p_commit.get("tech_activations", []))
                st.session_state.tech_used_this_round[p_id] = {
                    t: (t in restored_active) for t in ["T1", "T2", "T3", "T4", "T5"]
                }

            if restored_ev and restored_ev in st.session_state.used_events:
                st.session_state.used_events.remove(restored_ev)
            st.session_state.selected_event_id = restored_ev
            st.session_state.widget_event_picker = restored_ev
        elif st.session_state.used_events:
            restored = st.session_state.used_events.pop()
            st.session_state.selected_event_id = restored
            st.session_state.widget_event_picker = restored

        curr_target_r = int(st.session_state.current_round)
        st.session_state.score_history = [
            e for e in st.session_state.get("score_history", []) if int(e.get("round", 1)) <= curr_target_r
        ]
        if not st.session_state.score_history:
            st.session_state.score_history = [
                {"round": 1, "scores": {1: 50.0, 2: 50.0, 3: 50.0, 4: 50.0}}
            ]


def callback_load_demo_simulation() -> None:
    """Mengisi skenario simulasi realistis Ronde 11 untuk keperluan demo & presentasi juri."""
    clear_certificate_pdf_cache()
    demo_players = {
        1: {
            "name": "Alya",
            "city": "Nusantara Green",
            "projects": ["P017", "P021", "P026", "P047", "P059"],
            "techs": ["T1", "T3", "T5"],
            "skills": ["S2"],
            "problems": [],
            "coins": 24,
        },
        2: {
            "name": "Bima",
            "city": "Voltara Grid",
            "projects": ["P092", "P094", "P098", "P105", "P055"],
            "techs": ["T1", "T2"],
            "skills": ["S1"],
            "problems": ["PR02"],
            "coins": 21,
        },
        3: {
            "name": "Citra",
            "city": "MetroPulse",
            "projects": ["P047", "P050", "P054", "P059", "P065"],
            "techs": ["T2", "T4"],
            "skills": ["S3"],
            "problems": [],
            "coins": 18,
        },
        4: {
            "name": "Dimas",
            "city": "AstraNova",
            "projects": ["P002", "P031", "P077"],
            "techs": ["T2"],
            "skills": ["S5"],
            "problems": ["PR01", "PR03"],
            "coins": 9,
        },
    }

    st.session_state.active_tab = "Tab 1: Live Tracker"
    st.session_state.current_round = 11
    st.session_state.used_events = [f"EV{r:02d}" for r in range(1, 11)]
    st.session_state.round_event_history = []
    st.session_state.action_history = []
    st.session_state.last_deltas = {p_id: {} for p_id in range(1, 5)}
    st.session_state.selected_event_id = "EV11"
    st.session_state.widget_event_picker = "EV11"
    st.session_state.audit_triggered = False
    st.session_state.active_player_id = 1
    st.session_state.tech_used_this_round = {
        p_id: {t: False for t in ["T1", "T2", "T3", "T4", "T5"]} for p_id in range(1, 5)
    }

    for p_id, cfg in demo_players.items():
        st.session_state.players[p_id] = {
            "name": cfg["name"],
            "city": cfg["city"],
            "projects": list(cfg["projects"]),
            "techs": list(cfg["techs"]),
            "skills": list(cfg["skills"]),
            "problems": list(cfg["problems"]),
            "coins": cfg["coins"],
            "committed_event_coins": 0,
            "manual_points": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "active_techs_this_round": [],
            "tech_activations_this_round": [],
            "accumulated_tech_stats": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "bonus_stats": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "accumulated_event_delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "accumulated_event_coins": 0,
            "immune_this_round": False,
            "tech_log": [f"Simulasi Demo R11: {cfg['city']} siap diaudit"],
        }
        st.session_state[f"widget_name_{p_id}"] = cfg["name"]
        st.session_state[f"widget_city_{p_id}"] = cfg["city"]
        st.session_state[f"widget_projects_{p_id}"] = list(cfg["projects"])
        st.session_state[f"widget_techs_{p_id}"] = list(cfg["techs"])
        st.session_state[f"widget_skills_{p_id}"] = list(cfg["skills"])
        st.session_state[f"widget_problems_{p_id}"] = list(cfg["problems"])
        st.session_state[f"widget_coins_{p_id}"] = cfg["coins"]
        for stat_key in ["M", "E", "ENV", "QoL"]:
            st.session_state[f"widget_man_{stat_key}_{p_id}"] = 0

    st.session_state.quick_district_filter = None
    target_scores = _compute_current_scores_map(active_event_id=None)
    demo_hist: List[Dict[str, Any]] = []
    # Kurva progres realistis R1..R11 dari baseline 50 menuju skor aktual Ronde 11
    curve_weights = [0.0, 0.08, 0.17, 0.28, 0.39, 0.51, 0.62, 0.74, 0.84, 0.93, 1.0]
    crisis_dips = {1: 0.0, 2: -1.5, 3: 0.0, 4: -2.2}
    for r_idx, w in enumerate(curve_weights, start=1):
        r_scores: Dict[int, float] = {}
        for p_id in range(1, 5):
            base = 50.0
            final_v = float(target_scores[p_id])
            dip = crisis_dips[p_id] if r_idx in (6, 8) else 0.0
            val = base + (final_v - base) * w + dip
            if r_idx == 11:
                val = final_v
            r_scores[p_id] = round(max(0.0, min(100.0, val)), 2)
        demo_hist.append({"round": r_idx, "scores": r_scores})
    st.session_state.score_history = demo_hist


def callback_reset_game() -> None:
    clear_certificate_pdf_cache()
    st.session_state.active_tab = "Tab 1: Live Tracker"
    st.session_state.current_round = 1
    st.session_state.used_events = []
    st.session_state.round_event_history = []
    st.session_state.action_history = []
    st.session_state.last_deltas = {p_id: {} for p_id in range(1, 5)}
    st.session_state.selected_event_id = None
    if "widget_event_picker" in st.session_state:
        st.session_state.widget_event_picker = None
    st.session_state.audit_triggered = False
    st.session_state.active_player_id = 1
    st.session_state.quick_district_filter = None
    st.session_state.score_history = [
        {"round": 1, "scores": {1: 50.0, 2: 50.0, 3: 50.0, 4: 50.0}}
    ]

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
            "committed_event_coins": 0,
            "manual_points": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "active_techs_this_round": [],
            "tech_activations_this_round": [],
            "accumulated_tech_stats": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
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
    pl = st.session_state.players[p_id]
    if "accumulated_tech_stats" not in pl:
        pl["accumulated_tech_stats"] = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    if "tech_activations_this_round" not in pl:
        pl["tech_activations_this_round"] = []

    owned_copies = max(1, pl["techs"].count(t_code))
    used_copies = pl["active_techs_this_round"].count(t_code)
    if used_copies >= owned_copies:
        return

    snap = _capture_undo_snapshot()
    clear_certificate_pdf_cache()
    pl["active_techs_this_round"].append(t_code)
    st.session_state.tech_used_this_round[p_id][t_code] = (used_copies + 1 >= owned_copies)

    tcard = PERMANENT_TECH_BY_CODE.get(t_code, {})
    t_delta = {
        "M": int(tcard.get("M", 0)),
        "E": int(tcard.get("E", 0)),
        "ENV": int(tcard.get("ENV", 0)),
        "QoL": int(tcard.get("QoL", 0)),
    }
    for k in ("M", "E", "ENV", "QoL"):
        pl["accumulated_tech_stats"][k] += t_delta[k]

    curr_r = int(st.session_state.current_round)
    meta = TECH_ACTION_META.get(t_code, {})

    resolvable = get_resolvable_problems_for_tech(t_code, pl["techs"], pl["problems"])
    solved_pid = resolvable[0] if resolvable else None

    effective_delta = dict(t_delta)
    if solved_pid:
        pl["problems"].remove(solved_pid)
        if f"widget_problems_{p_id}" in st.session_state:
            st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])
        pcard = PROBLEM_BY_ID.get(solved_pid, {})
        p_name = pcard.get("name", solved_pid)
        for k in ("M", "E", "ENV", "QoL"):
            effective_delta[k] -= int(pcard.get(k, 0))
        pl["tech_log"].append(f"R{curr_r}: Aksi {t_code} selesaikan krisis [{p_name}] & +{meta.get('short_label', '')}")
    else:
        pl["tech_log"].append(f"R{curr_r}: Aksi {t_code} diaktifkan ({meta.get('short_label', '')})")

    pl["tech_activations_this_round"].append(
        {
            "code": t_code,
            "delta": t_delta,
            "solved_problem": solved_pid,
        }
    )
    _record_action_entry(
        curr_r,
        p_id,
        f"P{p_id} · {pl['city']}",
        t_code,
        tcard.get("name", t_code),
        "Tech",
        effective_delta,
        snap,
    )


def callback_use_s1(p_id: int, prob_to_remove: str) -> None:
    snap = _capture_undo_snapshot()
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    pcard = PROBLEM_BY_ID.get(prob_to_remove, {})
    delta = {k: -int(pcard.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}

    if prob_to_remove in pl["problems"]:
        pl["problems"].remove(prob_to_remove)
        if f"widget_problems_{p_id}" in st.session_state:
            st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])

    if "S1" in pl["skills"]:
        pl["skills"].remove("S1")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])

    p_name = pcard.get("name", prob_to_remove)
    pl["tech_log"].append(f"R{curr_r}: S1 dipakai & terhapus (Amankan Krisis [{p_name}])")
    _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", "S1", f"S1 Hapus {prob_to_remove}", "Skill", delta, snap)


def callback_use_s1_fallback(p_id: int) -> None:
    snap = _capture_undo_snapshot()
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    if "S1" in pl["skills"]:
        pl["skills"].remove("S1")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    for k in ["M", "E", "ENV", "QoL"]:
        pl["bonus_stats"][k] += 2
    pl["tech_log"].append(f"R{curr_r}: S1 dipakai & terhapus (Dana Darurat +2 Semua Aspek)")
    _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", "S1", "S1 Dana Darurat", "Skill", {"M": 2, "E": 2, "ENV": 2, "QoL": 2}, snap)


def callback_use_s2(p_id: int) -> None:
    snap = _capture_undo_snapshot()
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    if "S2" in pl["skills"]:
        pl["skills"].remove("S2")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["bonus_stats"]["ENV"] += 5
    pl["tech_log"].append(f"R{curr_r}: S2 dipakai & terhapus (+5 ENV)")
    _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", "S2", "S2 Carbon Capture Boost", "Skill", {"ENV": 5}, snap)


def callback_use_s3(p_id: int) -> None:
    snap = _capture_undo_snapshot()
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    if "S3" in pl["skills"]:
        pl["skills"].remove("S3")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["bonus_stats"]["M"] += 5
    pl["tech_log"].append(f"R{curr_r}: S3 dipakai & terhapus (+5 M)")
    _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", "S3", "S3 Traffic Override", "Skill", {"M": 5}, snap)


def callback_use_s4(p_id: int) -> None:
    snap = _capture_undo_snapshot()
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    if "S4" in pl["skills"]:
        pl["skills"].remove("S4")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["bonus_stats"]["QoL"] += 5
    pl["tech_log"].append(f"R{curr_r}: S4 dipakai & terhapus (+5 QoL)")
    _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", "S4", "S4 Public Health Campaign", "Skill", {"QoL": 5}, snap)


def callback_use_s5(p_id: int) -> None:
    snap = _capture_undo_snapshot()
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    if "S5" in pl["skills"]:
        pl["skills"].remove("S5")
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
    pl["immune_this_round"] = True
    pl["tech_log"].append(f"R{curr_r}: S5 Cyber Shield aktif & terhapus (Kebal Event ronde ini)")
    _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", "S5", "S5 Cyber Shield", "Skill", {}, snap)


def callback_use_skill_solve_problem(p_id: int, s_code: str, prob_id: str) -> None:
    snap = _capture_undo_snapshot()
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    pcard = PROBLEM_BY_ID.get(prob_id, {})
    delta = {k: -int(pcard.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}

    if prob_id in pl["problems"]:
        pl["problems"].remove(prob_id)
        if f"widget_problems_{p_id}" in st.session_state:
            st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])

    if s_code in pl["skills"]:
        pl["skills"].remove(s_code)
        if f"widget_skills_{p_id}" in st.session_state:
            st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])

    p_name = pcard.get("name", prob_id)
    pl["tech_log"].append(f"R{curr_r}: {s_code} dipakai & terhapus (Amankan Krisis [{p_name}])")
    _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", s_code, f"{s_code} Amankan {prob_id}", "Skill", delta, snap)


def export_session_json() -> str:
    """Mengekspor state permainan EcoNova saat ini menjadi string JSON terformat rapi."""
    payload = {
        "current_round": int(st.session_state.get("current_round", 1)),
        "used_events": list(st.session_state.get("used_events", [])),
        "round_event_history": copy.deepcopy(st.session_state.get("round_event_history", [])),
        "score_history": copy.deepcopy(st.session_state.get("score_history", [])),
        "selected_event_id": st.session_state.get("selected_event_id"),
        "active_player_id": int(st.session_state.get("active_player_id", 1)),
        "players": copy.deepcopy(st.session_state.get("players", {})),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _normalize_player_dict(raw_pl: Dict[str, Any], p_id: int) -> Dict[str, Any]:
    """Menormalisasi struktur data 1 pemain agar seluruh field wajib tersedia & bertipe aman."""
    man_raw = raw_pl.get("manual_points", {}) or {}
    bon_raw = raw_pl.get("bonus_stats", {}) or {}
    ev_raw = raw_pl.get("accumulated_event_delta", {}) or {}
    tech_st_raw = raw_pl.get("accumulated_tech_stats", {}) or {}
    return {
        "name": str(raw_pl.get("name") or f"Pemain {p_id}"),
        "city": str(raw_pl.get("city") or f"Kota {p_id}"),
        "projects": [str(x) for x in raw_pl.get("projects", []) if str(x) in PROJECT_BY_ID],
        "techs": [str(x) for x in raw_pl.get("techs", []) if str(x) in PERMANENT_TECH_BY_CODE],
        "skills": [str(x) for x in raw_pl.get("skills", []) if str(x) in SKILL_BY_CODE],
        "problems": [str(x) for x in raw_pl.get("problems", []) if str(x) in PROBLEM_BY_ID],
        "coins": max(0, int(raw_pl.get("coins", 5))),
        "committed_event_coins": max(0, int(raw_pl.get("committed_event_coins", 0))),
        "manual_points": {k: int(man_raw.get(k, 0)) for k in ("M", "E", "ENV", "QoL")},
        "active_techs_this_round": [str(x) for x in raw_pl.get("active_techs_this_round", []) if str(x) in PERMANENT_TECH_BY_CODE],
        "tech_activations_this_round": list(raw_pl.get("tech_activations_this_round", [])),
        "accumulated_tech_stats": {k: int(tech_st_raw.get(k, 0)) for k in ("M", "E", "ENV", "QoL")},
        "bonus_stats": {k: int(bon_raw.get(k, 0)) for k in ("M", "E", "ENV", "QoL")},
        "accumulated_event_delta": {k: int(ev_raw.get(k, 0)) for k in ("M", "E", "ENV", "QoL")},
        "accumulated_event_coins": int(raw_pl.get("accumulated_event_coins", 0)),
        "immune_this_round": bool(raw_pl.get("immune_this_round", False)),
        "tech_log": [str(x) for x in raw_pl.get("tech_log", [])],
    }


def import_session_json(raw_json: str) -> Tuple[bool, str]:
    """
    Memvalidasi dan memulihkan state sesi EcoNova dari string JSON.
    Mengonversi kunci string '1'..'4' kembali ke integer 1..4 serta menyinkronkan seluruh
    kunci widget_* di st.session_state tanpa memicu StreamlitAPIException.
    """
    if not raw_json or not str(raw_json).strip():
        return False, "File JSON kosong."

    try:
        data = json.loads(raw_json)
    except Exception as exc:
        return False, f"Gagal mengurai JSON: {exc}"

    if not isinstance(data, dict) or not isinstance(data.get("players"), dict):
        return False, "Struktur JSON tidak valid: field 'players' tidak ditemukan."

    raw_players = data["players"]
    restored_players: Dict[int, Dict[str, Any]] = {}
    for p_id in range(1, 5):
        raw_pl = raw_players.get(str(p_id))
        if raw_pl is None:
            raw_pl = raw_players.get(p_id)
        if not isinstance(raw_pl, dict):
            return False, f"Data pemain #{p_id} ('{p_id}') tidak ditemukan atau tidak valid."
        restored_players[p_id] = _normalize_player_dict(raw_pl, p_id)

    curr_round = max(1, min(13, int(data.get("current_round", 1))))
    used_events = [str(e) for e in data.get("used_events", []) if str(e) in EVENT_BY_ID]

    raw_rev_hist = data.get("round_event_history", [])
    restored_rev_hist: List[Dict[str, Any]] = []
    if isinstance(raw_rev_hist, list):
        for item in raw_rev_hist:
            if not isinstance(item, dict):
                continue
            item_copy = copy.deepcopy(item)
            item_players = item_copy.get("players", {})
            if isinstance(item_players, dict):
                item_copy["players"] = {
                    int(k): v for k, v in item_players.items() if str(k).isdigit()
                }
            restored_rev_hist.append(item_copy)

    raw_score_hist = data.get("score_history", [])
    restored_score_hist: List[Dict[str, Any]] = []
    if isinstance(raw_score_hist, list):
        for item in raw_score_hist:
            if not isinstance(item, dict) or not isinstance(item.get("scores"), dict):
                continue
            sc_map = {
                int(k): float(v)
                for k, v in item["scores"].items()
                if str(k) in ("1", "2", "3", "4")
            }
            if len(sc_map) == 4:
                restored_score_hist.append({"round": int(item.get("round", 1)), "scores": sc_map})

    sel_ev = data.get("selected_event_id")
    if sel_ev not in EVENT_BY_ID or sel_ev in used_events:
        sel_ev = None

    act_pid = int(data.get("active_player_id", 1))
    if act_pid not in (1, 2, 3, 4):
        act_pid = 1

    st.session_state.current_round = curr_round
    st.session_state.used_events = used_events
    st.session_state.round_event_history = restored_rev_hist
    st.session_state.selected_event_id = sel_ev
    st.session_state.widget_event_picker = sel_ev
    st.session_state.active_player_id = act_pid
    st.session_state.players = restored_players
    st.session_state.audit_triggered = False
    clear_certificate_pdf_cache()
    st.session_state.action_history = []
    st.session_state.last_deltas = {p_id: {} for p_id in range(1, 5)}
    st.session_state.quick_district_filter = None
    st.session_state.tech_used_this_round = {
        p_id: {
            t: (t in restored_players[p_id].get("active_techs_this_round", []))
            for t in ["T1", "T2", "T3", "T4", "T5"]
        }
        for p_id in range(1, 5)
    }

    for p_id, pl in restored_players.items():
        st.session_state[f"widget_name_{p_id}"] = pl["name"]
        st.session_state[f"widget_city_{p_id}"] = pl["city"]
        st.session_state[f"widget_projects_{p_id}"] = list(pl["projects"])
        st.session_state[f"widget_techs_{p_id}"] = list(pl["techs"])
        st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
        st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])
        st.session_state[f"widget_coins_{p_id}"] = int(pl["coins"])
        for stat_key in ("M", "E", "ENV", "QoL"):
            st.session_state[f"widget_man_{stat_key}_{p_id}"] = int(pl["manual_points"].get(stat_key, 0))

    if restored_score_hist:
        st.session_state.score_history = restored_score_hist
    else:
        st.session_state.score_history = [
            {"round": curr_round, "scores": _compute_current_scores_map(active_event_id=None)}
        ]

    return True, f"Sesi Ronde {curr_round} berhasil dipulihkan ({len(used_events)} Event di Discard)."


def callback_import_uploaded_session() -> None:
    """Callback tombol Muat Sesi JSON agar mutasi widget_* berjalan sebelum render ulang."""
    uploaded_obj = st.session_state.get("uploader_session_json")
    if uploaded_obj is None:
        st.session_state.session_import_feedback = (False, "Pilih file .json sesi terlebih dahulu.")
        return
    try:
        raw_text = uploaded_obj.getvalue().decode("utf-8")
    except Exception as exc:
        st.session_state.session_import_feedback = (False, f"Gagal membaca file: {exc}")
        return
    ok, msg = import_session_json(raw_text)
    st.session_state.session_import_feedback = (ok, msg)