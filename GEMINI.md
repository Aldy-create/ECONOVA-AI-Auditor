# GEMINI.md — Panduan Arsitektur & Aturan EcoNova AI Auditor

Dokumen ini menjadi panduan teknis dan desain resmi untuk proyek **EcoNova: Sustainable City Planner & AI Auditor** di root workspace.

---

## 1. Arsitektur Modul Aplikasi

Aplikasi dipisahkan menjadi modul-modul berfokus tunggal agar mudah dipelihara dan diuji:

| Modul | Tanggung Jawab |
| :--- | :--- |
| `app.py` | Entry point Streamlit utama (`st.set_page_config`, orkestrasi 3 tab utama). |
| `ai_auditor.py` | Entry point alias yang memastikan `sys.path` valid lalu mengeksekusi `app.py`. |
| `cards_data.py` | Database 197 kartu resmi (Project, Tech `T1–T5`, Skill `S1–S5`, Problem `PR01–PR20`, Event `EV01–EV13`), aturan kombinasi penyelesaian krisis (`PROBLEM_SOLUTION_RULES`), klasifikasi arketipe kota, strategi rekomendasi (`recommend_cards_for_player`), gelar spesial (`assign_special_city_awards`), serta engine perhitungan skor deterministik (`compute_player_score`). |
| `styles.py` | Palet warna faksi permanen (`FACTION_THEMES`), CSS global **EcoNova Official Poster (Tactile Eco-Solarpunk Board Game HUD)** (`GLOBAL_STYLES_CSS`), Ribbon Headers, Tactile Card Shadows, Peta Mini 3×3 aspal (`.eco-mini-road-h`), styling custom input/multiselect/expander, dan CSS dinamis giliran aktif (`inject_faction_turn_styles`). |
| `state_manager.py` | Inisialisasi `st.session_state`, definisi metadata aksi (`TECH_ACTION_META`), callback widget (`widget_*`), Peta Mini 3×3 (`callback_select_board_tile`), riwayat skor (`score_history`), ekspor/impor JSON (`export_session_json`, `import_session_json`), simulasi demo 1-klik (`callback_load_demo_simulation`), komitmen/rollback koin Event antar ronde, validasi kombinasi `T1–T5`, dan konsumsi `S1–S5`. |
| `llm_service.py` | Pemuatan senyap `GROQ_API_KEY` (`st.secrets`, `.streamlit/secrets.toml`, atau environment), layanan chat robot pemandu **EcoBot** (`query_llm_game_master`), serta pengayaan narasi visi kota 2075 (`generate_llm_enhanced_narrative`). |
| `ui_components.py` | Komponen UI untuk Top HUD Bar & Hero Banner, Footer pengunci, Tab 1 Live Tracker (header ringkas tanpa strip bertumpuk, Meja Aksi Kartu Cepat dengan validasi Tech/koin/diskon Event + Rekomendasi Taktis + Peta Mini 3×3 + Simpan/Muat Sesi JSON + Log/Undo, tombol Demo Simulasi, Delta Badge, 4 Kartu Pemain dengan lencana distrik `> 0`), Tab 2 Final Audit (Gelar Spesial Podium, Radar 4 Pilar bervariasi *line dash*, Grafik Balapan Skor Antar-Ronde, Sertifikat 2075, & ekspor `.html` via `build_certificate_download_html`), dan Tab 3 **EcoBot Game Master**. |

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
5. **Event Pasar (`EV03` & `EV05`) & Validasi Meja Aksi Kartu Cepat:**
   - `EV03` memberi diskon `-2 Koin` Project Card Energy District; `EV05` memberi diskon `-2 Koin` Tech/Skill Card di City Center.
   - Meja Aksi Kartu Cepat menghitung `effective_cost` otomatis saat `EV03`/`EV05` aktif, memeriksa kecukupan syarat `tech_list` proyek terhadap `pl["techs"]` serta kecukupan kas koin efektif pemain target, sambil mempertahankan tombol `Terapkan` aktif sebagai override manual fasilitator.
6. **Lencana Distrik Dinamis (`> 0`), Dropdown Event, & Simulasi Demo 1-Klik:**
   - Kartu pemain hanya merender lencana distrik yang sudah dibangun (`count > 0`) atau teks ringkas `"Belum ada distrik terbangun"` bila kosong; `widget_event_picker` memakai placeholder `"-- Pilih Event Card --"`.
   - `callback_load_demo_simulation()` mengisi 4 kota skenario Ronde 11 dengan 4 arketipe berbeda (`Alya · Nusantara Green` *Green Eco City*, `Bima · Voltara Grid` *Smart Energy City*, `Citra · MetroPulse` *Connected Mobility City*, `Dimas · AstraNova` *Uneven / At-Risk City*) dan Event aktif `EV11` serta menyinkronkan seluruh kunci `widget_*_{p_id}`.
7. **Sertifikat Akreditasi Kota 2075 Siap Cetak, Grafik Progres Skor, & Gelar Spesial:**
   - Tabel matriks Tab 2 menampilkan `"Peringkat #1 (Skor Tertinggi)"` untuk juara 1 dan `"Selisih -X.XX poin dari #1"` untuk peringkat di bawahnya saat tidak terjadi seri (`tie_breaker_reason` kosong).
   - Setiap tab sertifikat di Tab 2 menyediakan tombol `st.download_button` yang memanggil `build_certificate_download_html()` untuk mengunduh file `.html` mandiri berisi diploma 2075, tabel 4 pilar, dan 4 narasi audit.
   - `st.session_state.score_history` mencatat skor rata-rata keempat pemain antar-ronde (diperbarui saat `callback_next_round`, di-rollback di `callback_prev_round`, diisi kurva Ronde 1–11 di `callback_load_demo_simulation`, dan ditampilkan sebagai grafik garis Plotly di Tab 2).
   - `assign_special_city_awards(ranked_players)` menyematkan 1 gelar unik (`🛡️ Arsitek Tanpa Krisis`, `🔬 Pionir Teknologi`, `🪙 Bendahara Kota`, atau gelar pilar tertinggi) pada setiap kartu podium Tab 2.
8. **Peta Mini 3×3, Rekomendasi Taktis, & Simpan/Muat Sesi JSON (Tab 1):**
   - Peta Mini 3×3 (`callback_select_board_tile`, `callback_reset_district_filter`) memetakan 9 petak papan fisik dengan jalan aspal grid (`panel_mini_board_grid`); klik distrik menyaring daftar proyek di `quick_district_filter`, sedangkan klik `City Center` mengalihkan kategori ke `"Tech"`.
   - `recommend_cards_for_player()` menyarankan 3 kartu Project/Tech paling efisien untuk menutup pilar terlemah pemain aktif sesuai syarat Tech & koin efektif, lengkap dengan tombol 1-klik `"Pilih"` (`callback_pick_recommended_card`).
   - `export_session_json()` dan `import_session_json()` menyimpan serta memulihkan seluruh state permainan termasuk konversi kunci `"1".."4"` ke `1..4` dan sinkronisasi penuh seluruh kunci `widget_*`.
9. **Klasifikasi Archetype Kota (`classify_city_archetype`):**
   - `Uneven / At-Risk City`: `min_val < 40 or avg_score < 50 or spread >= 30`.
   - `Balanced Sustainable Metropolis`: `avg_score >= 75 and min_val >= 60 and spread < 30`.

---

## 4. Panduan Rendering HTML Aman, Tema EcoNova Official Poster & Skema Warna

1. **Safe HTML Rendering (`render_html`):**
   - Selalu gunakan helper `render_html(html_str)` dari `styles.py` untuk blok HTML multi-baris. Fungsi ini memangkas indentasi awal tiap baris (`line.strip()`) sebelum memanggil `st.markdown(..., unsafe_allow_html=True)` agar parser Markdown tidak menganggap HTML berindentasi >= 4 spasi sebagai code block `<pre><code>`.
   - Untuk nilai dinamis milik pengguna (nama wali kota, nama kota), selalu bungkus dengan `html.escape(...)`.
2. **EcoNova Official Poster Style (`styles.py` & `ui_components.py`):**
   - **Latar Langit & Papan Permainan (`econova board 3.pdf`):** `.stApp` memakai gradasi langit siang cerah berpadu cahaya hangat kota (`linear-gradient(180deg, #BAE6FD 0%, #E0F2FE 28%, #FEF9E7 70%, #F9F6E8 100%)`, dipadukan overlay halus di atas `assets/econova_bg.png`) dengan teks utama **Deep Forest Green (`#164E33`)** dan badan kartu **Warm Paper Cream (`#FFFDF7`)**. Area *Telemetri Ronde / Meja Aksi* dan *4 Kartu Pemain* di Tab 1 dipisahkan oleh **Asphalt Road Divider (`.eco-road-divider`)** (`#222629`, tinggi `10px`, `border-radius: 999px`, garis putus-putus putih `2px dashed rgba(255, 255, 255, 0.85)`).
   - **Forest Green Ribbons & Tab Aktif (`.eco-ribbon-header`):** Header ribbon utama dan tombol tab aktif memakai **Deep Forest Green (`#164E33`)** dengan aksen border **Sunny Gold (`#F59E0B`)** (`box-shadow: 0 4px 0 #0D3321`). Plakat logo `EcoNova` (`.eco-logo-plaque`) memakai wadah `#164E33` agar kontras tajam.
   - **Alas Papan Utama & Top Bar Kobalt-Teal (`styles.py` & `ui_components.py`):** `.block-container` dibingkai solid (`rgba(255, 253, 247, 0.97)`, `3px solid #164E33`, `box-shadow: 0 8px 0 #164E33`), dikunci oleh **Top HUD Bar** (`.eco-top-hud` bergradasi Cobalt-Teal Metropolitan `linear-gradient(90deg, #0369A1 0%, #0284C7 55%, #0D9488 100%)` selaras bingkai luar `econova board 3.pdf`, berisi plakat logo `#164E33`, indikator `RONDE X / 13`, giliran, Event, serta badge Krisis `#FFE4E6/#9F1239` saat `> 0` dan `rgba(255,255,255,0.2)/#FFFFFF` saat `0 Krisis`) dan **Footer** (`.eco-footer-bar` menampilkan label tab aktif konsisten termasuk `Tab 3: EcoBot Game Master`). Header Tab 1 dirampingkan tanpa bilah status bertumpuk di bawah navigasi tab.
   - **Tactile Card Shadows & Tombol 3D:** Kartu pemain (`panel_tracker_p1`..`p4`) dan panel kontrol bergaya papan fisik (`#FFFDF7`, border `2px solid #164E33` / `2.5px` faksi, bayangan padat `box-shadow: 0 4px 0 #164E33`), sementara tombol memiliki efek tekan fisik (`transform: translateY(3px)` dan `box-shadow: 0 1px 0 #164E33` saat `:active`). Input/select/expander menggunakan border `#8BB39E` dan tag pill berkode warna per kategori kartu.
   - **Tab 2 & Tab 3:** Radar 4 Pilar Kota di Tab 2 memakai variasi gaya garis `dash` (`["solid", "dash", "dot", "dashdot"]`) agar skor yang berimpitan tetap terbaca jelas; Tab 3 memakai branding **EcoBot Game Master** dengan avatar maskot generatif `assets/ecobot_avatar.png` dan 36 ikon `.png` custom di `assets/`.
   - **Background Panorama Solarpunk (`assets/econova_bg.png`):** Latar web `.stApp` memakai ilustrasi panorama kota berkelanjutan `assets/econova_bg.png` dengan lapisan *warm cream translucent overlay* (`linear-gradient(180deg, rgba(244, 241, 225, 0.72) 0%, rgba(249, 246, 232, 0.84) 100%)`), `background-size: cover`, dan `background-attachment: fixed`.
   - **Sinkronisasi Warna 8 Distrik Kartu Fisik (`Project Card.pdf` -> `cards_data.py` & `ui_components.py`):**
     - **Residential District:** `bg: #EDE9FE`, `border: #8B5CF6`, `text: #6D28D9`
     - **Green Park District:** `bg: #DCFCE7`, `border: #16A34A`, `text: #15803D`
     - **Industrial District:** `bg: #FEF3C7`, `border: #B45309`, `text: #92400E`
     - **Transportation District:** `bg: #E0F2FE`, `border: #0284C7`, `text: #0369A1`
     - **Public Services District:** `bg: #FCE7F3`, `border: #EC4899`, `text: #BE185D`
     - **Commercial District:** `bg: #CCFBF1`, `border: #0D9488`, `text: #0F766E`
     - **Energy District:** `bg: #FEF9C3`, `border: #EAB308`, `text: #A16207`
     - **Water District:** `bg: #DBEAFE`, `border: #2563EB`, `text: #1D4ED8`
   - **Overall Rating Grade (`get_overall_rating_grade`):** Emblem rating lingkaran (`.eco-rating-badge`) di samping skor rata-rata dengan ambang `A+` (≥ 85), `A` (≥ 78), `A-` (≥ 70), `B+` (≥ 62), `B` (≥ 55), `C` (≥ 45), dan `D` (< 45).
3. **Skema Warna Faksi Distrik Board (`FACTION_THEMES` — `econova board 3.pdf`):**
   - **Pemain 1 — Faksi Green Park (`P1 · Green Park`):** Accent `#16A34A`, Dark `#15803D`, Badge `#DCFCE7`, Tint `rgba(22, 163, 74, 0.10)`
   - **Pemain 2 — Faksi Water & Transit (`P2 · Hydro Transit`):** Accent `#0284C7`, Dark `#0369A1`, Badge `#E0F2FE`, Tint `rgba(2, 132, 199, 0.10)`
   - **Pemain 3 — Faksi Residential (`P3 · Terracotta`):** Accent `#DC2626`, Dark `#B91C1C`, Badge `#FEE2E2`, Tint `rgba(220, 38, 38, 0.09)`
   - **Pemain 4 — Faksi City Center (`P4 · Solar Gold`):** Accent `#D97706`, Dark `#B45309`, Badge `#FEF3C7`, Tint `rgba(217, 119, 6, 0.10)`
4. **Skema Warna 4 Pilar Aspek Kota (Poster Palette):**
   - **Mobility (`M`):** `#0284C7` (`.eco-pill-m`)
   - **Energy (`E`):** `#EAB308` / `#B45309` (`.eco-pill-e`)
   - **Environment (`ENV`):** `#16A34A` (`.eco-pill-env`)
   - **Quality of Life (`QoL`):** `#E11D48` (`.eco-pill-qol`)
