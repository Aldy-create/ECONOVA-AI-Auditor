"""
ai_auditor.py — Entry point alias untuk EcoNova: Sustainable City Planner & AI Auditor.
Menjalankan modul utama `app.py` yang terhubung dengan modul terpisah (`styles.py`,
`state_manager.py`, `llm_service.py`, `ui_components.py`, dan `cards_data.py`).
Dapat dijalankan dengan `streamlit run ai_auditor.py` maupun `streamlit run app.py`.
"""

import sys
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
if str(_BASE_DIR) not in sys.path:
    sys.path.insert(0, str(_BASE_DIR))

_APP_FILE = _BASE_DIR / "app.py"
exec(compile(_APP_FILE.read_text(encoding="utf-8"), str(_APP_FILE), "exec"))
