"""
app.py — EcoNova: Sustainable City Planner & AI Auditor
Entry point modular aplikasi Streamlit yang mengorkestrasi:
- `styles.py`: Sistem desain EcoNova Official Poster (Tactile Eco-Solarpunk Board Game HUD) & CSS faksi/widget
- `state_manager.py`: State persistence, sinkronisasi koin event, validasi kombinasi T1–T5 & S1–S5
- `llm_service.py`: Silent API Key loading & integrasi Groq LLM (Profesor Terra)
- `ui_components.py`: Komponen Tab 1 Live Tracker, Tab 2 Final Audit, & Tab 3 AI Game Master
- `cards_data.py`: Database kartu resmi & engine skor deterministik
"""

import sys
import warnings
from pathlib import Path

# Pastikan root directory tersedia di sys.path saat dijalankan dari direktori mana pun
_BASE_DIR = str(Path(__file__).resolve().parent)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

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

import streamlit as st

# ==============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT (HARUS DIPANGGIL PERTAMA)
# ==============================================================================
st.set_page_config(
    page_title="EcoNova — Sustainable City Planner & AI Auditor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import importlib
import cards_data as _cards_data_mod

# Reload cards_data otomatis jika Streamlit Cloud masih menahan modul versi lama di sys.modules
if not hasattr(_cards_data_mod, "get_resolvable_problems_for_tech"):
    importlib.reload(_cards_data_mod)

from state_manager import init_session_state
from styles import inject_global_styles
from ui_components import (
    render_hero_banner,
    render_tab_audit,
    render_tab_game_master,
    render_tab_tracker,
)


def main() -> None:
    """Inisialisasi state, suntikkan CSS, dan render 3 tab utama aplikasi."""
    init_session_state()
    inject_global_styles()
    render_hero_banner()

    tab_tracker, tab_audit, tab_gm = st.tabs(
        [
            "Tab 1: Live Tracker",
            "Tab 2: Final Audit",
            "Tab 3: AI Game Master",
        ]
    )

    with tab_tracker:
        render_tab_tracker()

    with tab_audit:
        render_tab_audit()

    with tab_gm:
        render_tab_game_master()


main()
