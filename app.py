"""
app.py — EcoNova: Sustainable City Planner & AI Auditor
Entry point modular aplikasi Streamlit.
"""

import importlib
import sys
import warnings
from pathlib import Path

_BASE_DIR = str(Path(__file__).resolve().parent)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

warnings.filterwarnings("ignore")
try:
    import streamlit.deprecation_util as _sdu
    _sdu.show_deprecation_warning = lambda *args, **kwargs: None
except Exception:
    pass

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

import streamlit as st

st.set_page_config(
    page_title="EcoNova — Sustainable City Planner & AI Auditor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_REQUIRED_MODULE_EXPORTS = (
    ("cards_data", ("PROBLEM_SOLUTION_RULES", "get_resolvable_problems_for_tech", "get_resolvable_problems_for_skill")),
    ("styles", ("FACTION_THEMES", "inject_global_styles", "inject_faction_turn_styles", "render_html")),
    ("state_manager", ("TAB_OPTIONS", "init_session_state", "callback_switch_tab", "callback_lock_and_open_audit")),
    ("llm_service", ("get_groq_api_key", "query_llm_game_master", "generate_llm_enhanced_narrative")),
    ("ui_components", ("render_hero_banner", "render_navigation_bar", "render_tab_tracker", "render_tab_audit", "render_tab_game_master")),
)
for _mod_name, _req_attrs in _REQUIRED_MODULE_EXPORTS:
    _mod_obj = importlib.import_module(_mod_name)
    if any(not hasattr(_mod_obj, _attr) for _attr in _req_attrs):
        importlib.reload(_mod_obj)

from state_manager import init_session_state
from styles import inject_global_styles
from ui_components import (
    render_hero_banner,
    render_navigation_bar,
    render_tab_audit,
    render_tab_game_master,
    render_tab_tracker,
)


def main() -> None:
    """Inisialisasi state, suntikkan CSS, dan render navigasi stateful 3 tab."""
    init_session_state()
    inject_global_styles()
    render_hero_banner()

    active_tab = render_navigation_bar()

    if active_tab == "Tab 1: Live Tracker":
        render_tab_tracker()
    elif active_tab == "Tab 2: Final Audit":
        render_tab_audit()
    else:
        render_tab_game_master()


main()