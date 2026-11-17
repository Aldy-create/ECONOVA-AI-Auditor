# GEMINI.md — Panduan Arsitektur & Aturan EcoNova AI Auditor

Dokumen ini menjadi panduan teknis dan desain resmi untuk proyek **EcoNova: Sustainable City Planner & AI Auditor** di root workspace.

---

## 1. Arsitektur Modul Aplikasi

Aplikasi dipisahkan menjadi modul-modul berfokus tunggal agar mudah dipelihara dan diuji:

| Modul | Tanggung Jawab |
| :--- | :--- |
| `app.py` | Entry point Streamlit utama (`st.set_page_config`, orkestrasi 3 tab utama). |
| `ai_auditor.py` | Entry point alias yang memastikan `sys.path` valid lalu mengeksekusi `app.py`. |
| `cards_data.py` | Database 197 kartu resmi (Project, Tech `T1–T5`, Skill `S1–S5`, Problem `PR01–PR20`, Event `EV01–EV13`), aturan kombinasi penyelesaian krisis (`PROBLEM_SOLUTION_RULES`), klasifikasi arketipe kota, serta engine perhitungan skor deterministik (`compute_player_score`). |
| `styles.py` | Palet warna faksi permanen (`FACTION_THEMES`), CSS global **EcoNova Official Poster (Tactile Eco-Solarpunk Board Game HUD)** (`GLOBAL_STYLES_CSS`), Ribbon Headers, Tactile Card Shadows, styling custom input/multiselect/expander, dan CSS dinamis giliran aktif (`inject_faction_turn_styles`). |
| `state_manager.py` | Inisialisasi `st.session_state`, definisi metadata aksi (`TECH_ACTION_META`), callback widget (`widget_*`), komitmen/rollback koin Event antar ronde, validasi kombinasi `T1–T5`, dan konsumsi `S1–S5`. |
| `llm_service.py` | Pemuatan senyap `GROQ_API_KEY` (`st.secrets`, `.streamlit/secrets.toml`, atau environment), layanan chat Profesor Terra (`query_llm_game_master`), serta pengayaan narasi visi kota 2075 (`generate_llm_enhanced_narrative`). |
| `ui_components.py` | Komponen UI untuk Hero Banner, Tab 1 Live Tracker, Tab 2 Final Audit & Sertifikat 2075, dan Tab 3 AI Game Master. |

---

## 2. Aturan `st.session_state`, `widget_*` Callbacks & Sinkronisasi Koin Event

1. **Zero-Crash Widget State Architecture:**
   - Sumber kebenaran utama data pemain disimpan di `st.session_state.players[1..4]`.
   - Widget Streamlit terikat ke kunci `widget_*` (misal `widget_name_{p_id}`, `widget_projects_{p_id}`, `widget_coins_{p_id}`, `widget_man_{stat}_{p_id}`) yang diinisialisasi di `init_session_state()` **tanpa** melewatkan argumen `default=` atau `value=` secara bersamaan pada widget.
   - Seluruh mutasi data dilakukan di dalam callback (`on_change` / `on_click`) sebelum render ulang, sehingga menghindari `StreamlitAPIException`.
2. **Sinkronisasi & Anti-Double-Counting Koin Event:**
   - **Live Preview:** Ketika Event Card dipilih pada `widget_event_picker` (`EV01`: `+2`, `EV09`: `+3`, `EV13`: `+2`), `compute_player_score` menghitung `live_event_coins` sehingga badge kas koin di Display Zone langsung menampilkan total efektif real-time (`🪙 X Koin (+Y Event)`).
   - **Commit saat `Next Ronde ➡️` (`callback_next_round`):**
     - Delta stat Event dikomit ke `pl["accumulated_event_delta"]`.
     - Koin Event langsung ditambahkan ke kas permanen `pl["coins"]` dan `st.session_state[f"widget_coins_{p_id}"]` (serta dicatat pada `pl["committed_event_coins"]`), **bukan** ke `accumulated_event_coins`, agar tidak terjadi penghitungan ganda saat selector di-reset ke `None`.
     - Snapshot ronde disimpan ke `st.session_state.round_event_history`.
   - **Rollback saat `⬅️ Prev` (`callback_prev_round`):**
     - Snapshot terakhir dari `round_event_history` di-pop untuk mengurangkan kembali delta stat & koin Event dari `pl["accumulated_event_delta"]`, `pl["coins"]`, `widget_coins_{p_id}`, dan `committed_event_coins`, sekaligus memulihkan kartu Event dari `used_events`.
   - **Audit Tab 2 (`audit_event_mode`):**
     - Mode default **`Gunakan Riwayat Event Ronde Aktual`** menghitung skor akhir memakai `accumulated_event_delta` dan kas koin aktual (`accumulated_event_coins=0`).
     - Mode **`Gunakan Simulasi Otomatis 13 Event`** mengevaluasi seluruh `EV01–EV13` dengan terlebih dahulu mengurangi `committed_event_coins` dari `coins` agar koin Event tidak terhitung dua kali.
3. **Akumulasi Poin Tech Permanen (`accumulated_tech_stats`) vs Cooldown per Ronde (`active_techs_this_round`):**
   - **Saat Tombol Tech Ditekan (`callback_activate_tech`):**
     - Menandai kartu sudah dipakai pada ronde berjalan (`active_techs_this_round` & `tech_used_this_round[p_id][t_code] = True`) agar tombol ter-disable untuk sisa ronde tersebut.
     - Langsung mengakumulasikan stat kartu Tech (`T1`: `+2 E`, `T2`: `+1 M, +1 QoL`, `T3`: `+2 ENV`, `T4`: `+2 M`, `T5`: `+1 ENV, +1 QoL`) secara permanen ke `pl["accumulated_tech_stats"]` dan mencatatnya di `pl["tech_activations_this_round"]`.
   - **Saat `Next Ronde ➡️` (`callback_next_round`):**
     - Menyimpan snapshot aktivasi ronde ke `round_event_history`, lalu me-reset `active_techs_this_round`, `tech_activations_this_round`, dan `tech_used_this_round` agar tombol Tech aktif kembali di ronde baru.
     - **DILARANG mereset `pl["accumulated_tech_stats"]`** saat pindah ronde sehingga poin Tech dari ronde-ronde sebelumnya tetap bertahan dan terakumulasi di Live Tracker maupun Final Audit (Tab 2).
   - **Saat `⬅️ Prev` (`callback_prev_round`):**
     - Membatalkan aktivasi Tech yang sempat dilakukan pada ronde berjalan yang ditinggalkan dari `accumulated_tech_stats` (beserta problem yang diselesaikannya), lalu memulihkan status tombol Tech ronde tujuan dari `round_event_history`.
   - **Perhitungan Skor (`compute_player_score`):**
     - Menerima `accumulated_tech_stats` untuk menghitung `tech_delta` secara deterministik tanpa penghitungan ganda, sementara `tech_count`, `tie_tuple`, dan syarat proyek tetap membaca seluruh kartu Tech permanen yang dimiliki pemain (`tech_codes`).

---

## 3. Aturan Main Terbaru EcoNova

1. **Action Points (AP) di Papan Fisik:**
   - Dashboard **tidak** merender pelacak atau pengurang AP; pengelolaan AP dilakukan secara fisik di papan meja.
2. **Permanent Tech Card (`T1–T5`):**
   - Kartu `T1–T5` yang dimiliki pemain bersifat permanen dan **tetap berada di area pemain** sepanjang permainan (tidak pernah terhapus saat diaktifkan maupun saat menyelesaikan Problem Card).
   - Tiap ronde, pemain dapat mengaktifkan tombol aksi `T1–T5` miliknya maksimal **1x per ronde** (status direset otomatis saat menekan `Next Ronde ➡️`).
3. **Penyelesaian Problem Card (`PR01–PR20`) & Validasi Kombinasi (`+`):**
   - Resolusi via Tech memeriksa seluruh syarat kombinasi bersamaan sesuai Rulebook Bab IX melalui `PROBLEM_SOLUTION_RULES` & `get_resolvable_problems_for_tech()`:
     - `PR01`: `T3` atau `S2` | `PR02`: `T2` atau `S3` | `PR03`: `T1` | `PR04`: `T5` | `PR05`: `T5`
     - `PR06`: `S1` atau `S4` | `PR07`: `T3` atau `T5` | `PR08`: **`T1 + T2`** | `PR09`: `T4` | `PR10`: `T2` atau `S5`
     - `PR11`: **`T1 + T3`** atau `S2` | `PR12`: Bayar Koin | `PR13`: `T5` | `PR14`: Bayar Koin | `PR15`: `T3`
     - `PR16`: **`T2 + T3`** | `PR17`: `T1` | `PR18`: `T3` | `PR19`: `T2` atau `S1` | `PR20`: **`T1 + T3 + T5`**
   - Note: `T4` hanya menyelesaikan `PR09`.
4. **Consumable Skill (`S1–S5`):**
   - Sekali pakai: begitu tombol aksi dipakai (baik untuk efek langsung maupun mengamankan Problem Card yang sesuai), kartu Skill **langsung terhapus (`consumed`)** dari `pl["skills"]` dan `widget_skills_{p_id}`.
5. **Event Pasar (`EV03` & `EV05`):**
   - `EV03` menampilkan pengingat diskon `-2 Koin` Project Card Energy District; `EV05` menampilkan pengingat diskon `-2 Koin` Tech Card di City Center.
6. **Klasifikasi Archetype Kota (`classify_city_archetype`):**
   - `Uneven / At-Risk City`: `min_val < 40 or avg_score < 50 or spread >= 30`.
   - `Balanced Sustainable Metropolis`: `avg_score >= 75 and min_val >= 60 and spread < 30`.

---

## 4. Panduan Rendering HTML Aman, Tema EcoNova Official Poster & Skema Warna

1. **Safe HTML Rendering (`render_html`):**
   - Selalu gunakan helper `render_html(html_str)` dari `styles.py` untuk blok HTML multi-baris. Fungsi ini memangkas indentasi awal tiap baris (`line.strip()`) sebelum memanggil `st.markdown(..., unsafe_allow_html=True)` agar parser Markdown tidak menganggap HTML berindentasi >= 4 spasi sebagai code block `<pre><code>`.
   - Untuk nilai dinamis milik pengguna (nama wali kota, nama kota), selalu bungkus dengan `html.escape(...)`.
2. **EcoNova Official Poster Style (`styles.py` & `ui_components.py`):**
   - **Latar Sky-to-Parchment Cream:** `.stApp` memakai `linear-gradient(180deg, #B8E1F7 0%, #DDF0F6 24%, #F4F1E1 62%, #F9F6E8 100%)` dengan teks utama **Deep Forest Green (`#164E33`)** dan latar kartu fisik **Warm Cream (`#FFFDF7`)**.
   - **Forest Green Ribbons (`.eco-ribbon-header`):** Header utama dan judul bagian penting pada Hero Banner, Tab 1, Tab 2, dan Tab 3 memakai Bold Forest Green Ribbon Pill (`#1E6B47 -> #144A31`, teks `#FFFFFF`, font `'Fredoka'`, `border-radius: 999px`, `box-shadow: 0 4px 0 #0D3321`).
   - **Tactile Card Shadows & Tombol 3D:** Kartu pemain (`panel_tracker_p1`..`p4`) bergaya physical game card (`#FFFDF7`, border `2.5px` faksi, `box-shadow: 0 6px 0 rgba(22, 78, 51, 0.14), 0 12px 24px rgba(0,0,0,0.06)`), sementara tombol utama dan navigasi ronde memiliki efek tekan 3D (`border-bottom: 3.5px solid #0E3B26` dan `:active { transform: translateY(2px); }`). Input/select/expander menggunakan border `#B7D5C4` dan tag pill `#DCFCE7` dengan teks `#14532D`.
   - **Overall Rating Grade (`get_overall_rating_grade`):** Emblem rating lingkaran (`.eco-rating-badge`) di samping skor rata-rata dengan ambang `A+` (≥ 85), `A` (≥ 78), `A-` (≥ 70), `B+` (≥ 62), `B` (≥ 55), `C` (≥ 45), dan `D` (< 45).
3. **Skema Warna Faksi (`FACTION_THEMES`):**
   - **Pemain 1 — Faksi Emerald:** Accent `#059669`, Tint `rgba(16, 185, 129, 0.10)`
   - **Pemain 2 — Faksi Sky Blue:** Accent `#0284C7`, Tint `rgba(2, 132, 199, 0.10)`
   - **Pemain 3 — Faksi Amber:** Accent `#D97706`, Tint `rgba(245, 158, 11, 0.10)`
   - **Pemain 4 — Faksi Violet:** Accent `#7C3AED`, Tint `rgba(124, 58, 237, 0.10)`
4. **Skema Warna 4 Pilar Aspek Kota (Poster Palette):**
   - **Mobility (`M`):** `#0284C7` (`.eco-pill-m`)
   - **Energy (`E`):** `#EAB308` / `#B45309` (`.eco-pill-e`)
   - **Environment (`ENV`):** `#16A34A` (`.eco-pill-env`)
   - **Quality of Life (`QoL`):** `#E11D48` (`.eco-pill-qol`)
