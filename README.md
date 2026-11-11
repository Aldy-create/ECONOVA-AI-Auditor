# 🌿 EcoNova: Sustainable City Planner & AI Auditor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistem HUD simulator dan AI Game Master interaktif berbasis web untuk permainan papan **EcoNova: Sustainable City Builder**. Aplikasi ini dirancang dengan estetika **Bright Glass 3D Full-Color Solarpunk**, menyediakan pelacak ronde fisik (Live Tracker), auditor skor deterministik otomatis (Final Audit), serta asisten cerdas aturan permainan (Profesor Terra).

---

## ✨ Fitur Utama

### 🎮 Tab 1: Live Game Dashboard Tracker
- **Pelacak Telemetri Ronde (1–13)**: Navigasi ronde permainan dengan sistem discard otomatis untuk kartu event global.
- **Live Modifier Event Fisik**: Efek Event Card yang sedang terbuka di papan langsung memodifikasi skor 4 pemain secara real-time.
- **Aksi Teknologi Permanen (T1–T5)**: Mekanik aktivasi 1x per ronde dengan cooldown cerdas dan tombol proteksi.
- **Konsumsi Kartu Skill (S1–S5)**:
  - **S1 (Emergency Response)**: Menghapus 1 Problem Card milik pemain dan mengonsumsi kartu S1 seketika.
  - **S5 (Cyber Shield)**: Mengaktifkan imunitas penuh dari seluruh penalti Event Card pada ronde berjalan.
- **🛠️ Penyesuaian Poin Manual**: Mode juri/pengguna untuk menambah atau mengurangi poin pilar secara langsung dengan 1 klik toggle.

### 🏆 Tab 2: Final Audit & Award Certificate
- **Deterministic Pure Python Engine**: Menghitung skor akhir 4 pilar kota (Mobility, Energy, Environment, Quality of Life) pada skala 0–100.
- **Hierarki Tie-Breaker Resmi (Rulebook Bab VI.3)**: Skor Rata-Rata → Jumlah Proyek → Tech Dimiliki → Sisa Koin.
- **Klasifikasi Arketipe Kota 2075**: Menentukan profil arketipe kota (Balanced Sustainable Metropolis, Eco-Sanctuary, dll.).
- **Sertifikat Penghargaan Futuristik**: Visualisasi panggung pemenang Juara 1–4 dan analisis SWOT tata kota komprehensif.

### 📖 Tab 3: AI Game Master (Profesor Terra)
- Asisten aturan pintar bertenaga **Groq LLM (Llama 3)** dengan fallback offline *Smart Rulebook Engine*.
- Pertanyaan cepat 1-klik untuk aturan 3 AP, transit City Center, syarat teknologi, penalti krisis, dan rumus bonus koin akhir.

---

## 🚀 Cara Menjalankan Secara Lokal

1. **Clone repository ini**:
   ```bash
   git clone https://github.com/USERNAME/econova-ai-auditor.git
   cd econova-ai-auditor
   ```

2. **Buat & aktifkan virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```

3. **Install dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Opsional) Konfigurasi Groq API Key**:
   Buat file `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   ```

5. **Jalankan aplikasi**:
   ```bash
   streamlit run app.py
   ```
   Buka peramban pada tautan `http://localhost:8501`.

---

## ☁️ Deployment ke Streamlit Community Cloud

Aplikasi ini 100% siap di-deploy langsung ke **Streamlit Community Cloud**:

1. Push repository ini ke GitHub.
2. Buka [share.streamlit.io](https://share.streamlit.io/) dan hubungkan akun GitHub Anda.
3. Klik **New app** dan pilih repository ini:
   - **Repository:** `USERNAME/econova-ai-auditor`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Buka **Advanced settings** ➔ **Secrets**, lalu masukkan API key Anda:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   ```
5. Klik **Deploy!** 🚀

---

## 📄 Lisensi & Hak Cipta
Dikembangkan untuk EcoNova Board Game. Seluruh aturan mengacu pada `EcoNova_Rulebook_CardCollection.docx`.
