"""
llm_service.py — Silent API Key Loading, Groq AI Game Master & Narrative Enhancer
Menangani integrasi Groq LLM (EcoBot & Narasi Kota 2075) dengan fallback lokal otomatis.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from cards_data import (
    RULEBOOK_SECTIONS,
    generate_city_narrative_report,
    smart_rulebook_search,
)

try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

BASE_DIR = Path(__file__).resolve().parent
SECRETS_PATH = BASE_DIR / ".streamlit" / "secrets.toml"


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
        "Kamu adalah EcoBot, robot asisten & Game Master board game 'EcoNova: Sustainable City Builder'.\n\n"
        "1. GAYA BAHASA & ANTI KEPANJANGAN (WAJIB):\n"
        "- Pakai bahasa Indonesia sehari-hari yang santai, akrab, dan luwes (pakai aku–kamu), kayak teman yang jago jelasin board game di meja. Jangan kaku atau terdengar kayak dosen.\n"
        "- LANGSUNG JAWAB ke inti! Dilarang pakai basa-basi pembuka seperti 'Berdasarkan rulebook...' atau 'Pertanyaan yang bagus!'.\n"
        "- Maksimal 2–4 kalimat pendek atau 3–4 poin singkat, KECUALI pemain secara eksplisit minta penjelasan lengkap/detail.\n\n"
        "2. IDENTITAS, KREATOR & PERTANYAAN KASUAL:\n"
        "- Identitasmu: EcoBot, robot pemandu resmi EcoNova yang bantu jelasin aturan main, efek kartu, dan hasil audit kota.\n"
        "- Pembuat Game & Web: Board game EcoNova dikembangkan oleh tim proyek CTI EcoNova di School of STEM, Universitas Prasetiya Mulya (dokumen rulebook disusun bersama Frederic Agung & tim). Aplikasi web EcoNova AI Auditor & EcoBot ini dibuat oleh Aldy Alfaisal Pasaribu (Aldy-create) bersama tim pengembang EcoNova.\n"
        "- Pertanyaan kasual soal game (misal 'susah nggak?', 'seru nggak?', 'mainnya lama nggak?'): Jawab santai pakai fakta rulebook—aturan dasarnya gampang dipahami dalam beberapa menit (pakai 3 AP buat gerak, bangun Proyek, dan jaga 4 pilar kota), tapi menantang pas menyeimbangkan skor dan ngadepin Problem/Event selama 13 ronde.\n\n"
        "3. GUARDRAIL KETAT & ANTI HALUSINASI:\n"
        "- DILARANG KERAS menjawab topik di luar board game EcoNova dan aplikasi web pendampingnya (misal presiden, ibukota negara, coding umum, politik, pelajaran sekolah, trivia umum).\n"
        "- Jika ditanya di luar topik EcoNova, tolak santai dalam 1–2 kalimat tetap in-character lalu arahkan balik ke game (contoh: 'Waduh, kalau soal itu di luar sirkuit dataku nih! Aku cuma paham segala hal tentang board game EcoNova—yuk tanya aturan main atau efek kartunya aja.').\n"
        "- Pastikan semua kode kartu (P001–P120, T1–T5, S1–S5, PR01–PR20, EV01–EV13), biaya koin, AP, dan perubahan stat (M, E, ENV, QoL) 100% sesuai Rulebook. Kalau suatu detail tidak tertulis di rulebook, bilang jujur aturan itu belum tercantum di rulebook.\n\n"
        f"RINGKASAN RULEBOOK RESMI:\n{rules_summary}\n\n"
        f"KONTEKS KARTU & ATURAN TERKAIT:\n{local_context}"
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
                temperature=0.45,
                groq_api_key=api_key,
                max_tokens=320,
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
