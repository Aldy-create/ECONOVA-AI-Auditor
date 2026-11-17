"""
state_manager.py — State Persistence, Callbacks & Game Mechanics Engine
Mengelola seluruh st.session_state, sinkronisasi widget, komitmen/rollback koin event,
validasi kombinasi teknologi T1–T5, konsumsi kartu skill S1–S5, dan navigasi tab aktif.
"""

import copy
import importlib
from typing import Any, Dict, List, Optional

import streamlit as st

import cards_data as _cards_data_mod

if not hasattr(_cards_data_mod, "get_resolvable_problems_for_tech"):
    importlib.reload(_cards_data_mod)

from cards_data import (
    EVENT_BY_ID,
    PERMANENT_TECH_BY_CODE,
    PROBLEM_BY_ID,
    PROJECT_BY_ID,
    SKILL_BY_CODE,
    evaluate_single_event_live,
    get_resolvable_problems_for_tech,
)

TAB_OPTIONS = [
    "Tab 1: Live Tracker",
    "Tab 2: Final Audit",
    "Tab 3: AI Game Master",
]

WELCOME_CHAT_MESSAGE = (
    "Hai Wali Kota! Aku **EcoBot**, robot pemandu game EcoNova kamu.\n\n"
    "Bingung soal aturan pas lagi main? Tanya aja langsung, misalnya:\n"
    "- Pakai **3 AP** di papan & bonus +3 Koin **City Center**\n"
    "- Efek **Tech (T1–T5)** & **Skill (S1–S5)** sekali pakai\n"
    "- Cara beresin **Problem Card (PR01–PR20)** & kombo Tech-nya\n"
    "- Hitungan **Bonus 20 Koin** & urutan **Tie-Breaker**\n\n"
    "Klik tombol cepat di samping atau ketik pertanyaanmu di bawah ya!"
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


def callback_lock_and_open_audit() -> None:
    """Mengunci simulasi dari Tab 1 dan langsung otomatis berpindah ke Tab 2: Final Audit."""
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
    }


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


def callback_undo_last_action() -> None:
    """Membatalkan aksi terakhir dari action_history dan memulihkan snapshot termasuk widget state."""
    history = st.session_state.get("action_history", [])
    if not history:
        return
    last_entry = history.pop()
    snap = last_entry.get("snapshot", {})
    if not snap:
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
    """Menerapkan kartu dari panel aksi cepat terpadu ke pemain aktif serta mencatat log & delta."""
    if not card_id or p_id not in st.session_state.players:
        return
    pl = st.session_state.players[p_id]
    curr_r = int(st.session_state.current_round)
    snap = _capture_undo_snapshot()

    if category == "Project" and card_id in PROJECT_BY_ID:
        if card_id in pl["projects"]:
            return
        card = PROJECT_BY_ID[card_id]
        pl["projects"].append(card_id)
        st.session_state[f"widget_projects_{p_id}"] = list(pl["projects"])
        deltas = {k: int(card.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}
        pl["tech_log"].append(f"R{curr_r}: Bangun Proyek [{card_id}] {card['name']}")
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Project", deltas, snap)

    elif category == "Tech" and card_id in PERMANENT_TECH_BY_CODE:
        if card_id in pl["techs"]:
            return
        card = PERMANENT_TECH_BY_CODE[card_id]
        pl["techs"].append(card_id)
        st.session_state[f"widget_techs_{p_id}"] = list(pl["techs"])
        pl["tech_log"].append(f"R{curr_r}: Tambah Tech [{card_id}] {card['name']}")
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Tech", {}, snap)

    elif category == "Skill" and card_id in SKILL_BY_CODE:
        if card_id in pl["skills"]:
            return
        card = SKILL_BY_CODE[card_id]
        pl["skills"].append(card_id)
        st.session_state[f"widget_skills_{p_id}"] = list(pl["skills"])
        pl["tech_log"].append(f"R{curr_r}: Tambah Skill [{card_id}] {card['name']}")
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Skill", {}, snap)

    elif category == "Problem" and card_id in PROBLEM_BY_ID:
        if card_id in pl["problems"]:
            return
        card = PROBLEM_BY_ID[card_id]
        pl["problems"].append(card_id)
        st.session_state[f"widget_problems_{p_id}"] = list(pl["problems"])
        deltas = {k: int(card.get(k, 0)) for k in ("M", "E", "ENV", "QoL")}
        pl["tech_log"].append(f"R{curr_r}: Catat Krisis [{card_id}] {card['name']}")
        _record_action_entry(curr_r, p_id, f"P{p_id} · {pl['city']}", card_id, card["name"], "Problem", deltas, snap)


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


def callback_reset_game() -> None:
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

    if t_code in pl["active_techs_this_round"]:
        return

    snap = _capture_undo_snapshot()
    pl["active_techs_this_round"].append(t_code)
    st.session_state.tech_used_this_round[p_id][t_code] = True

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