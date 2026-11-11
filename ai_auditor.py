"""
ai_auditor.py — Entry point alias untuk EcoNova: Sustainable City Builder Engine.
Menjalankan modul utama `app.py` yang terhubung langsung dengan `cards_data.py`.
Dapat dijalankan dengan `streamlit run ai_auditor.py` maupun `streamlit run app.py`.
"""

from pathlib import Path

_APP_FILE = Path(__file__).resolve().parent / "app.py"
exec(compile(_APP_FILE.read_text(encoding="utf-8"), str(_APP_FILE), "exec"))
