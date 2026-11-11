"""
cards_data.py — Basis Data Resmi & Deterministic Score Engine untuk EcoNova: Sustainable City Builder.
Diekstrak secara presisi 100% dari dokumen resmi `EcoNova_Rulebook_CardCollection.docx`:
- 120 Project Cards (P001 s/d P120 di 8 District)
- 40 Tech Cards (5 Permanent Tech T1–T5 × 4 salinan + 5 Consumable Skill S1–S5 × 4 salinan)
- 20 Problem Cards (PR01 s/d PR20)
- 13 Global Event Cards (EV01 s/d EV13)
- Mesin Perhitungan Skor Deterministik, Tie-Breaker Resmi, Klasifikasi Archetype, & Generator Narasi Solarpunk.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

DISTRICT_META: Dict[str, Dict[str, str]] = {'Residential': {'emoji': '🏘️',
                 'color': '#BE123C',
                 'badge_bg': '#FFE4E6',
                 'focus': 'Quality of Life (QoL) & Energy/ENV',
                 'description': 'Perumahan berkelanjutan, apartemen hijau, dan hunian pintar warga.'},
 'Green Park': {'emoji': '🌳',
                'color': '#15803D',
                'badge_bg': '#DCFCE7',
                'focus': 'Environment (ENV) & Quality of Life',
                'description': 'Ruang terbuka hijau, hutan kota, taman botani, dan koridor biodiversitas.'},
 'Industrial': {'emoji': '🏭',
                'color': '#B45309',
                'badge_bg': '#FEF3C7',
                'focus': 'Energy (E) & Environment (ENV)',
                'description': 'Kawasan industri sirkular, pabrik pintar, daur ulang, dan logistik hijau.'},
 'Transportation': {'emoji': '🚝',
                    'color': '#0369A1',
                    'badge_bg': '#E0F2FE',
                    'focus': 'Mobility (M)',
                    'description': 'Jaringan transportasi massal elektrik, metro, kereta cepat, dan jalur '
                                   'sepeda.'},
 'Public Services': {'emoji': '🏥',
                     'color': '#9D174D',
                     'badge_bg': '#FCE7F3',
                     'focus': 'Quality of Life (QoL)',
                     'description': 'Sekolah publik, rumah sakit cerdas, pusat riset, dan layanan darurat '
                                    'terpadu.'},
 'Commercial': {'emoji': '🏬',
                'color': '#6D28D9',
                'badge_bg': '#EDE9FE',
                'focus': 'Quality of Life (QoL) & Energy',
                'description': 'Pusat bisnis rendah karbon, ritel pintar, ekowisata, dan ekonomi masa '
                               'depan.'},
 'Energy': {'emoji': '⚡',
            'color': '#C2410C',
            'badge_bg': '#FFEDD5',
            'focus': 'Energy (E) & Environment (ENV)',
            'description': 'Pembangkit surya, turbin angin, mikrohidro, hidrogen, dan smart megagrid.'},
 'Water': {'emoji': '💧',
           'color': '#0284C7',
           'badge_bg': '#E0F2FE',
           'focus': 'Environment (ENV) & Quality of Life',
           'description': 'Pengolahan air bersih, restorasi sungai, pengendalian banjir, dan desalinasi.'}}

PROJECT_CARDS: List[Dict[str, Any]] = [{'id': 'P001',
  'global_no': 1,
  'district_no': 1,
  'name': 'Affordable Housing',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 3,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 3},
  'effect_str': '0 / 0 / +1 / +3',
  'effect_summary': '+1 ENV, +3 QoL',
  'description': 'Kartu Proyek #1 di Residential District (ID P001). Biaya: 3 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +1 ENV, +3 QoL.',
  'picker_label': '[P001] 🏘️ Residential - Affordable Housing (+1 ENV, +3 QoL | 🪙3)'},
 {'id': 'P002',
  'global_no': 2,
  'district_no': 2,
  'name': 'Public Housing Complex',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 4,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 4},
  'effect_str': '0 / 0 / 0 / +4',
  'effect_summary': '+4 QoL',
  'description': 'Kartu Proyek #2 di Residential District (ID P002). Biaya: 4 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +4 QoL.',
  'picker_label': '[P002] 🏘️ Residential - Public Housing Complex (+4 QoL | 🪙4)'},
 {'id': 'P003',
  'global_no': 3,
  'district_no': 3,
  'name': 'Green Residential',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 0,
  'ENV': 4,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 4, 'QoL': 2},
  'effect_str': '0 / 0 / +4 / +2',
  'effect_summary': '+4 ENV, +2 QoL',
  'description': 'Kartu Proyek #3 di Residential District (ID P003). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +4 ENV, +2 QoL.',
  'picker_label': '[P003] 🏘️ Residential - Green Residential (+4 ENV, +2 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P004',
  'global_no': 4,
  'district_no': 4,
  'name': 'Smart Home Community',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 3,
  'ENV': 1,
  'QoL': 3,
  'effects': {'M': 0, 'E': 3, 'ENV': 1, 'QoL': 3},
  'effect_str': '0 / +3 / +1 / +3',
  'effect_summary': '+3 E, +1 ENV, +3 QoL',
  'description': 'Kartu Proyek #4 di Residential District (ID P004). Biaya: 5 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +3 E, +1 ENV, +3 QoL.',
  'picker_label': '[P004] 🏘️ Residential - Smart Home Community (+3 E, +1 ENV, +3 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P005',
  'global_no': 5,
  'district_no': 5,
  'name': 'Solar Rooftop Housing',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 6,
  'tech_req': 'T1',
  'tech_list': ['T1'],
  'M': 0,
  'E': 5,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 0, 'E': 5, 'ENV': 3, 'QoL': 1},
  'effect_str': '0 / +5 / +3 / +1',
  'effect_summary': '+5 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #5 di Residential District (ID P005). Biaya: 6 Koin + 1 AP. Syarat Tech: T1. '
                 'Efek Stat: +5 E, +3 ENV, +1 QoL.',
  'picker_label': '[P005] 🏘️ Residential - Solar Rooftop Housing (+5 E, +3 ENV, +1 QoL | 🪙6 [Syarat: T1])'},
 {'id': 'P006',
  'global_no': 6,
  'district_no': 6,
  'name': 'Vertical Housing',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 1,
  'ENV': 2,
  'QoL': 3,
  'effects': {'M': 0, 'E': 1, 'ENV': 2, 'QoL': 3},
  'effect_str': '0 / +1 / +2 / +3',
  'effect_summary': '+1 E, +2 ENV, +3 QoL',
  'description': 'Kartu Proyek #6 di Residential District (ID P006). Biaya: 5 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +1 E, +2 ENV, +3 QoL.',
  'picker_label': '[P006] 🏘️ Residential - Vertical Housing (+1 E, +2 ENV, +3 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P007',
  'global_no': 7,
  'district_no': 7,
  'name': 'Eco-Friendly Apartments',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 6,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 2,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 2, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / +2 / +5 / +2',
  'effect_summary': '+2 E, +5 ENV, +2 QoL',
  'description': 'Kartu Proyek #7 di Residential District (ID P007). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 + '
                 'T3. Efek Stat: +2 E, +5 ENV, +2 QoL.',
  'picker_label': '[P007] 🏘️ Residential - Eco-Friendly Apartments (+2 E, +5 ENV, +2 QoL | 🪙6 [Syarat: T1 + '
                  'T3])'},
 {'id': 'P008',
  'global_no': 8,
  'district_no': 8,
  'name': 'Community Health Housing',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 5,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': '0 / 0 / 0 / +5',
  'effect_summary': '+5 QoL',
  'description': 'Kartu Proyek #8 di Residential District (ID P008). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +5 QoL.',
  'picker_label': '[P008] 🏘️ Residential - Community Health Housing (+5 QoL | 🪙5)'},
 {'id': 'P009',
  'global_no': 9,
  'district_no': 9,
  'name': 'Smart Security Housing',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 4,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 4},
  'effect_str': '0 / 0 / +1 / +4',
  'effect_summary': '+1 ENV, +4 QoL',
  'description': 'Kartu Proyek #9 di Residential District (ID P009). Biaya: 5 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +1 ENV, +4 QoL.',
  'picker_label': '[P009] 🏘️ Residential - Smart Security Housing (+1 ENV, +4 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P010',
  'global_no': 10,
  'district_no': 10,
  'name': 'Rainwater Housing System',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 5,
  'tech_req': 'T5',
  'tech_list': ['T5'],
  'M': 0,
  'E': 1,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 1, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / +1 / +3 / +2',
  'effect_summary': '+1 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #10 di Residential District (ID P010). Biaya: 5 Koin + 1 AP. Syarat Tech: T5. '
                 'Efek Stat: +1 E, +3 ENV, +2 QoL.',
  'picker_label': '[P010] 🏘️ Residential - Rainwater Housing System (+1 E, +3 ENV, +2 QoL | 🪙5 [Syarat: '
                  'T5])'},
 {'id': 'P011',
  'global_no': 11,
  'district_no': 11,
  'name': 'Energy Efficient Homes',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 6,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 0,
  'E': 5,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 5, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / +5 / +3 / +2',
  'effect_summary': '+5 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #11 di Residential District (ID P011). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 '
                 '+ T2. Efek Stat: +5 E, +3 ENV, +2 QoL.',
  'picker_label': '[P011] 🏘️ Residential - Energy Efficient Homes (+5 E, +3 ENV, +2 QoL | 🪙6 [Syarat: T1 + '
                  'T2])'},
 {'id': 'P012',
  'global_no': 12,
  'district_no': 12,
  'name': 'Urban Community Center',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 4,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 4},
  'effect_str': '0 / 0 / +1 / +4',
  'effect_summary': '+1 ENV, +4 QoL',
  'description': 'Kartu Proyek #12 di Residential District (ID P012). Biaya: 4 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +1 ENV, +4 QoL.',
  'picker_label': '[P012] 🏘️ Residential - Urban Community Center (+1 ENV, +4 QoL | 🪙4)'},
 {'id': 'P013',
  'global_no': 13,
  'district_no': 13,
  'name': 'Green Roof Apartments',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 6,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 1,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 1, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / +1 / +5 / +2',
  'effect_summary': '+1 E, +5 ENV, +2 QoL',
  'description': 'Kartu Proyek #13 di Residential District (ID P013). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 '
                 '+ T3. Efek Stat: +1 E, +5 ENV, +2 QoL.',
  'picker_label': '[P013] 🏘️ Residential - Green Roof Apartments (+1 E, +5 ENV, +2 QoL | 🪙6 [Syarat: T1 + '
                  'T3])'},
 {'id': 'P014',
  'global_no': 14,
  'district_no': 14,
  'name': 'Smart Residential Network',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 7,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 0,
  'E': 3,
  'ENV': 2,
  'QoL': 5,
  'effects': {'M': 0, 'E': 3, 'ENV': 2, 'QoL': 5},
  'effect_str': '0 / +3 / +2 / +5',
  'effect_summary': '+3 E, +2 ENV, +5 QoL',
  'description': 'Kartu Proyek #14 di Residential District (ID P014). Biaya: 7 Koin + 1 AP. Syarat Tech: T2 '
                 '+ T5. Efek Stat: +3 E, +2 ENV, +5 QoL.',
  'picker_label': '[P014] 🏘️ Residential - Smart Residential Network (+3 E, +2 ENV, +5 QoL | 🪙7 [Syarat: T2 '
                  '+ T5])'},
 {'id': 'P015',
  'global_no': 15,
  'district_no': 15,
  'name': 'Zero Carbon Residential',
  'category': 'Project',
  'district': 'Residential',
  'emoji': '🏘️',
  'cost': 8,
  'tech_req': 'T1 + T2 + T3',
  'tech_list': ['T1', 'T2', 'T3'],
  'M': 0,
  'E': 6,
  'ENV': 6,
  'QoL': 3,
  'effects': {'M': 0, 'E': 6, 'ENV': 6, 'QoL': 3},
  'effect_str': '0 / +6 / +6 / +3',
  'effect_summary': '+6 E, +6 ENV, +3 QoL',
  'description': 'Kartu Proyek #15 di Residential District (ID P015). Biaya: 8 Koin + 1 AP. Syarat Tech: T1 '
                 '+ T2 + T3. Efek Stat: +6 E, +6 ENV, +3 QoL.',
  'picker_label': '[P015] 🏘️ Residential - Zero Carbon Residential (+6 E, +6 ENV, +3 QoL | 🪙8 [Syarat: T1 + '
                  'T2 + T3])'},
 {'id': 'P016',
  'global_no': 16,
  'district_no': 1,
  'name': 'Community Park',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / 0 / +3 / +2',
  'effect_summary': '+3 ENV, +2 QoL',
  'description': 'Kartu Proyek #1 di Green Park District (ID P016). Biaya: 3 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +3 ENV, +2 QoL.',
  'picker_label': '[P016] 🌳 Green Park - Community Park (+3 ENV, +2 QoL | 🪙3)'},
 {'id': 'P017',
  'global_no': 17,
  'district_no': 2,
  'name': 'Urban Forest',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 5,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / 0 / +5 / +2',
  'effect_summary': '+5 ENV, +2 QoL',
  'description': 'Kartu Proyek #2 di Green Park District (ID P017). Biaya: 5 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +5 ENV, +2 QoL.',
  'picker_label': '[P017] 🌳 Green Park - Urban Forest (+5 ENV, +2 QoL | 🪙5)'},
 {'id': 'P018',
  'global_no': 18,
  'district_no': 3,
  'name': 'Botanical Garden',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 3,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 3},
  'effect_str': '0 / 0 / +5 / +3',
  'effect_summary': '+5 ENV, +3 QoL',
  'description': 'Kartu Proyek #3 di Green Park District (ID P018). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +5 ENV, +3 QoL.',
  'picker_label': '[P018] 🌳 Green Park - Botanical Garden (+5 ENV, +3 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P019',
  'global_no': 19,
  'district_no': 4,
  'name': 'Smart Irrigation Park',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 6,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 0,
  'E': 1,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 1, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / +1 / +5 / +2',
  'effect_summary': '+1 E, +5 ENV, +2 QoL',
  'description': 'Kartu Proyek #4 di Green Park District (ID P019). Biaya: 6 Koin + 1 AP. Syarat Tech: T2 + '
                 'T5. Efek Stat: +1 E, +5 ENV, +2 QoL.',
  'picker_label': '[P019] 🌳 Green Park - Smart Irrigation Park (+1 E, +5 ENV, +2 QoL | 🪙6 [Syarat: T2 + '
                  'T5])'},
 {'id': 'P020',
  'global_no': 20,
  'district_no': 5,
  'name': 'Vertical Garden',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / 0 / +3 / +2',
  'effect_summary': '+3 ENV, +2 QoL',
  'description': 'Kartu Proyek #5 di Green Park District (ID P020). Biaya: 4 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +3 ENV, +2 QoL.',
  'picker_label': '[P020] 🌳 Green Park - Vertical Garden (+3 ENV, +2 QoL | 🪙4)'},
 {'id': 'P021',
  'global_no': 21,
  'district_no': 6,
  'name': 'Biodiversity Sanctuary',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 6,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 0,
  'ENV': 7,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 7, 'QoL': 2},
  'effect_str': '0 / 0 / +7 / +2',
  'effect_summary': '+7 ENV, +2 QoL',
  'description': 'Kartu Proyek #6 di Green Park District (ID P021). Biaya: 6 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +7 ENV, +2 QoL.',
  'picker_label': '[P021] 🌳 Green Park - Biodiversity Sanctuary (+7 ENV, +2 QoL | 🪙6 [Syarat: T3])'},
 {'id': 'P022',
  'global_no': 22,
  'district_no': 7,
  'name': 'Eco Recreation Park',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 5,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 3,
  'QoL': 4,
  'effects': {'M': 0, 'E': 0, 'ENV': 3, 'QoL': 4},
  'effect_str': '0 / 0 / +3 / +4',
  'effect_summary': '+3 ENV, +4 QoL',
  'description': 'Kartu Proyek #7 di Green Park District (ID P022). Biaya: 5 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +3 ENV, +4 QoL.',
  'picker_label': '[P022] 🌳 Green Park - Eco Recreation Park (+3 ENV, +4 QoL | 🪙5)'},
 {'id': 'P023',
  'global_no': 23,
  'district_no': 8,
  'name': 'Green Rooftop Park',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 6,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 2,
  'ENV': 5,
  'QoL': 3,
  'effects': {'M': 0, 'E': 2, 'ENV': 5, 'QoL': 3},
  'effect_str': '0 / +2 / +5 / +3',
  'effect_summary': '+2 E, +5 ENV, +3 QoL',
  'description': 'Kartu Proyek #8 di Green Park District (ID P023). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 + '
                 'T3. Efek Stat: +2 E, +5 ENV, +3 QoL.',
  'picker_label': '[P023] 🌳 Green Park - Green Rooftop Park (+2 E, +5 ENV, +3 QoL | 🪙6 [Syarat: T1 + T3])'},
 {'id': 'P024',
  'global_no': 24,
  'district_no': 9,
  'name': 'Urban Farming Park',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 1,
  'ENV': 4,
  'QoL': 3,
  'effects': {'M': 0, 'E': 1, 'ENV': 4, 'QoL': 3},
  'effect_str': '0 / +1 / +4 / +3',
  'effect_summary': '+1 E, +4 ENV, +3 QoL',
  'description': 'Kartu Proyek #9 di Green Park District (ID P024). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +1 E, +4 ENV, +3 QoL.',
  'picker_label': '[P024] 🌳 Green Park - Urban Farming Park (+1 E, +4 ENV, +3 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P025',
  'global_no': 25,
  'district_no': 10,
  'name': 'Wildlife Protection Zone',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 6,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 0,
  'ENV': 7,
  'QoL': 1,
  'effects': {'M': 0, 'E': 0, 'ENV': 7, 'QoL': 1},
  'effect_str': '0 / 0 / +7 / +1',
  'effect_summary': '+7 ENV, +1 QoL',
  'description': 'Kartu Proyek #10 di Green Park District (ID P025). Biaya: 6 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +7 ENV, +1 QoL.',
  'picker_label': '[P025] 🌳 Green Park - Wildlife Protection Zone (+7 ENV, +1 QoL | 🪙6 [Syarat: T3])'},
 {'id': 'P026',
  'global_no': 26,
  'district_no': 11,
  'name': 'Carbon Absorption Forest',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 7,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 1,
  'ENV': 8,
  'QoL': 1,
  'effects': {'M': 0, 'E': 1, 'ENV': 8, 'QoL': 1},
  'effect_str': '0 / +1 / +8 / +1',
  'effect_summary': '+1 E, +8 ENV, +1 QoL',
  'description': 'Kartu Proyek #11 di Green Park District (ID P026). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + '
                 'T3. Efek Stat: +1 E, +8 ENV, +1 QoL.',
  'picker_label': '[P026] 🌳 Green Park - Carbon Absorption Forest (+1 E, +8 ENV, +1 QoL | 🪙7 [Syarat: T1 + '
                  'T3])'},
 {'id': 'P027',
  'global_no': 27,
  'district_no': 12,
  'name': 'Smart Eco Park',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 7,
  'tech_req': 'T2 + T3',
  'tech_list': ['T2', 'T3'],
  'M': 0,
  'E': 2,
  'ENV': 6,
  'QoL': 4,
  'effects': {'M': 0, 'E': 2, 'ENV': 6, 'QoL': 4},
  'effect_str': '0 / +2 / +6 / +4',
  'effect_summary': '+2 E, +6 ENV, +4 QoL',
  'description': 'Kartu Proyek #12 di Green Park District (ID P027). Biaya: 7 Koin + 1 AP. Syarat Tech: T2 + '
                 'T3. Efek Stat: +2 E, +6 ENV, +4 QoL.',
  'picker_label': '[P027] 🌳 Green Park - Smart Eco Park (+2 E, +6 ENV, +4 QoL | 🪙7 [Syarat: T2 + T3])'},
 {'id': 'P028',
  'global_no': 28,
  'district_no': 13,
  'name': 'Botanical Research Center',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 6,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 1,
  'ENV': 5,
  'QoL': 3,
  'effects': {'M': 0, 'E': 1, 'ENV': 5, 'QoL': 3},
  'effect_str': '0 / +1 / +5 / +3',
  'effect_summary': '+1 E, +5 ENV, +3 QoL',
  'description': 'Kartu Proyek #13 di Green Park District (ID P028). Biaya: 6 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +1 E, +5 ENV, +3 QoL.',
  'picker_label': '[P028] 🌳 Green Park - Botanical Research Center (+1 E, +5 ENV, +3 QoL | 🪙6 [Syarat: T2])'},
 {'id': 'P029',
  'global_no': 29,
  'district_no': 14,
  'name': 'Climate Resilience Park',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 7,
  'tech_req': 'T3 + T5',
  'tech_list': ['T3', 'T5'],
  'M': 0,
  'E': 2,
  'ENV': 7,
  'QoL': 3,
  'effects': {'M': 0, 'E': 2, 'ENV': 7, 'QoL': 3},
  'effect_str': '0 / +2 / +7 / +3',
  'effect_summary': '+2 E, +7 ENV, +3 QoL',
  'description': 'Kartu Proyek #14 di Green Park District (ID P029). Biaya: 7 Koin + 1 AP. Syarat Tech: T3 + '
                 'T5. Efek Stat: +2 E, +7 ENV, +3 QoL.',
  'picker_label': '[P029] 🌳 Green Park - Climate Resilience Park (+2 E, +7 ENV, +3 QoL | 🪙7 [Syarat: T3 + '
                  'T5])'},
 {'id': 'P030',
  'global_no': 30,
  'district_no': 15,
  'name': 'Mega Green Corridor',
  'category': 'Project',
  'district': 'Green Park',
  'emoji': '🌳',
  'cost': 8,
  'tech_req': 'T2 + T3 + T5',
  'tech_list': ['T2', 'T3', 'T5'],
  'M': 2,
  'E': 1,
  'ENV': 8,
  'QoL': 5,
  'effects': {'M': 2, 'E': 1, 'ENV': 8, 'QoL': 5},
  'effect_str': '+2 / +1 / +8 / +5',
  'effect_summary': '+2 M, +1 E, +8 ENV, +5 QoL',
  'description': 'Kartu Proyek #15 di Green Park District (ID P030). Biaya: 8 Koin + 1 AP. Syarat Tech: T2 + '
                 'T3 + T5. Efek Stat: +2 M, +1 E, +8 ENV, +5 QoL.',
  'picker_label': '[P030] 🌳 Green Park - Mega Green Corridor (+2 M, +1 E, +8 ENV, +5 QoL | 🪙8 [Syarat: T2 + '
                  'T3 + T5])'},
 {'id': 'P031',
  'global_no': 31,
  'district_no': 1,
  'name': 'Small Manufacturing Hub',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 2,
  'ENV': -1,
  'QoL': 1,
  'effects': {'M': 0, 'E': 2, 'ENV': -1, 'QoL': 1},
  'effect_str': '0 / +2 / -1 / +1',
  'effect_summary': '+2 E, -1 ENV, +1 QoL',
  'description': 'Kartu Proyek #1 di Industrial District (ID P031). Biaya: 3 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +2 E, -1 ENV, +1 QoL.',
  'picker_label': '[P031] 🏭 Industrial - Small Manufacturing Hub (+2 E, -1 ENV, +1 QoL | 🪙3)'},
 {'id': 'P032',
  'global_no': 32,
  'district_no': 2,
  'name': 'Eco Industrial Estate',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 3,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 0, 'E': 3, 'ENV': 3, 'QoL': 1},
  'effect_str': '0 / +3 / +3 / +1',
  'effect_summary': '+3 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #2 di Industrial District (ID P032). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +3 E, +3 ENV, +1 QoL.',
  'picker_label': '[P032] 🏭 Industrial - Eco Industrial Estate (+3 E, +3 ENV, +1 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P033',
  'global_no': 33,
  'district_no': 3,
  'name': 'Smart Factory',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 6,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 5,
  'ENV': 1,
  'QoL': 2,
  'effects': {'M': 0, 'E': 5, 'ENV': 1, 'QoL': 2},
  'effect_str': '0 / +5 / +1 / +2',
  'effect_summary': '+5 E, +1 ENV, +2 QoL',
  'description': 'Kartu Proyek #3 di Industrial District (ID P033). Biaya: 6 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +5 E, +1 ENV, +2 QoL.',
  'picker_label': '[P033] 🏭 Industrial - Smart Factory (+5 E, +1 ENV, +2 QoL | 🪙6 [Syarat: T2])'},
 {'id': 'P034',
  'global_no': 34,
  'district_no': 4,
  'name': 'Solar Manufacturing Plant',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 6,
  'tech_req': 'T1',
  'tech_list': ['T1'],
  'M': 0,
  'E': 5,
  'ENV': 2,
  'QoL': 1,
  'effects': {'M': 0, 'E': 5, 'ENV': 2, 'QoL': 1},
  'effect_str': '0 / +5 / +2 / +1',
  'effect_summary': '+5 E, +2 ENV, +1 QoL',
  'description': 'Kartu Proyek #4 di Industrial District (ID P034). Biaya: 6 Koin + 1 AP. Syarat Tech: T1. '
                 'Efek Stat: +5 E, +2 ENV, +1 QoL.',
  'picker_label': '[P034] 🏭 Industrial - Solar Manufacturing Plant (+5 E, +2 ENV, +1 QoL | 🪙6 [Syarat: T1])'},
 {'id': 'P035',
  'global_no': 35,
  'district_no': 5,
  'name': 'Waste Recycling Factory',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 1,
  'ENV': 5,
  'QoL': 1,
  'effects': {'M': 0, 'E': 1, 'ENV': 5, 'QoL': 1},
  'effect_str': '0 / +1 / +5 / +1',
  'effect_summary': '+1 E, +5 ENV, +1 QoL',
  'description': 'Kartu Proyek #5 di Industrial District (ID P035). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +1 E, +5 ENV, +1 QoL.',
  'picker_label': '[P035] 🏭 Industrial - Waste Recycling Factory (+1 E, +5 ENV, +1 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P036',
  'global_no': 36,
  'district_no': 6,
  'name': 'Electric Equipment Factory',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 6,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 0,
  'E': 4,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 0, 'E': 4, 'ENV': 3, 'QoL': 1},
  'effect_str': '0 / +4 / +3 / +1',
  'effect_summary': '+4 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #6 di Industrial District (ID P036). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 + '
                 'T2. Efek Stat: +4 E, +3 ENV, +1 QoL.',
  'picker_label': '[P036] 🏭 Industrial - Electric Equipment Factory (+4 E, +3 ENV, +1 QoL | 🪙6 [Syarat: T1 + '
                  'T2])'},
 {'id': 'P037',
  'global_no': 37,
  'district_no': 7,
  'name': 'Industrial Waste Treatment',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 5,
  'tech_req': 'T5',
  'tech_list': ['T5'],
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / 0 / +5 / +2',
  'effect_summary': '+5 ENV, +2 QoL',
  'description': 'Kartu Proyek #7 di Industrial District (ID P037). Biaya: 5 Koin + 1 AP. Syarat Tech: T5. '
                 'Efek Stat: +5 ENV, +2 QoL.',
  'picker_label': '[P037] 🏭 Industrial - Industrial Waste Treatment (+5 ENV, +2 QoL | 🪙5 [Syarat: T5])'},
 {'id': 'P038',
  'global_no': 38,
  'district_no': 8,
  'name': 'Automated Production Center',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 6,
  'tech_req': 'T2 + T3',
  'tech_list': ['T2', 'T3'],
  'M': 0,
  'E': 5,
  'ENV': 1,
  'QoL': 2,
  'effects': {'M': 0, 'E': 5, 'ENV': 1, 'QoL': 2},
  'effect_str': '0 / +5 / +1 / +2',
  'effect_summary': '+5 E, +1 ENV, +2 QoL',
  'description': 'Kartu Proyek #8 di Industrial District (ID P038). Biaya: 6 Koin + 1 AP. Syarat Tech: T2 + '
                 'T3. Efek Stat: +5 E, +1 ENV, +2 QoL.',
  'picker_label': '[P038] 🏭 Industrial - Automated Production Center (+5 E, +1 ENV, +2 QoL | 🪙6 [Syarat: T2 '
                  '+ T3])'},
 {'id': 'P039',
  'global_no': 39,
  'district_no': 9,
  'name': 'Green Logistics Factory',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 6,
  'tech_req': 'T2 + T4',
  'tech_list': ['T2', 'T4'],
  'M': 3,
  'E': 2,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 3, 'E': 2, 'ENV': 3, 'QoL': 1},
  'effect_str': '+3 / +2 / +3 / +1',
  'effect_summary': '+3 M, +2 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #9 di Industrial District (ID P039). Biaya: 6 Koin + 1 AP. Syarat Tech: T2 + '
                 'T4. Efek Stat: +3 M, +2 E, +3 ENV, +1 QoL.',
  'picker_label': '[P039] 🏭 Industrial - Green Logistics Factory (+3 M, +2 E, +3 ENV, +1 QoL | 🪙6 [Syarat: '
                  'T2 + T4])'},
 {'id': 'P040',
  'global_no': 40,
  'district_no': 10,
  'name': 'Carbon Neutral Industry',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 8,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 5,
  'ENV': 7,
  'QoL': 2,
  'effects': {'M': 0, 'E': 5, 'ENV': 7, 'QoL': 2},
  'effect_str': '0 / +5 / +7 / +2',
  'effect_summary': '+5 E, +7 ENV, +2 QoL',
  'description': 'Kartu Proyek #10 di Industrial District (ID P040). Biaya: 8 Koin + 1 AP. Syarat Tech: T1 + '
                 'T3. Efek Stat: +5 E, +7 ENV, +2 QoL.',
  'picker_label': '[P040] 🏭 Industrial - Carbon Neutral Industry (+5 E, +7 ENV, +2 QoL | 🪙8 [Syarat: T1 + '
                  'T3])'},
 {'id': 'P041',
  'global_no': 41,
  'district_no': 11,
  'name': 'Circular Economy Factory',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 7,
  'tech_req': 'T3 + T5',
  'tech_list': ['T3', 'T5'],
  'M': 0,
  'E': 3,
  'ENV': 7,
  'QoL': 2,
  'effects': {'M': 0, 'E': 3, 'ENV': 7, 'QoL': 2},
  'effect_str': '0 / +3 / +7 / +2',
  'effect_summary': '+3 E, +7 ENV, +2 QoL',
  'description': 'Kartu Proyek #11 di Industrial District (ID P041). Biaya: 7 Koin + 1 AP. Syarat Tech: T3 + '
                 'T5. Efek Stat: +3 E, +7 ENV, +2 QoL.',
  'picker_label': '[P041] 🏭 Industrial - Circular Economy Factory (+3 E, +7 ENV, +2 QoL | 🪙7 [Syarat: T3 + '
                  'T5])'},
 {'id': 'P042',
  'global_no': 42,
  'district_no': 12,
  'name': 'Smart Industrial Network',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 7,
  'tech_req': 'T2 + T4',
  'tech_list': ['T2', 'T4'],
  'M': 2,
  'E': 5,
  'ENV': 2,
  'QoL': 2,
  'effects': {'M': 2, 'E': 5, 'ENV': 2, 'QoL': 2},
  'effect_str': '+2 / +5 / +2 / +2',
  'effect_summary': '+2 M, +5 E, +2 ENV, +2 QoL',
  'description': 'Kartu Proyek #12 di Industrial District (ID P042). Biaya: 7 Koin + 1 AP. Syarat Tech: T2 + '
                 'T4. Efek Stat: +2 M, +5 E, +2 ENV, +2 QoL.',
  'picker_label': '[P042] 🏭 Industrial - Smart Industrial Network (+2 M, +5 E, +2 ENV, +2 QoL | 🪙7 [Syarat: '
                  'T2 + T4])'},
 {'id': 'P043',
  'global_no': 43,
  'district_no': 13,
  'name': 'Clean Technology Research',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 7,
  'tech_req': 'T1 + T2 + T3',
  'tech_list': ['T1', 'T2', 'T3'],
  'M': 0,
  'E': 6,
  'ENV': 5,
  'QoL': 3,
  'effects': {'M': 0, 'E': 6, 'ENV': 5, 'QoL': 3},
  'effect_str': '0 / +6 / +5 / +3',
  'effect_summary': '+6 E, +5 ENV, +3 QoL',
  'description': 'Kartu Proyek #13 di Industrial District (ID P043). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + '
                 'T2 + T3. Efek Stat: +6 E, +5 ENV, +3 QoL.',
  'picker_label': '[P043] 🏭 Industrial - Clean Technology Research (+6 E, +5 ENV, +3 QoL | 🪙7 [Syarat: T1 + '
                  'T2 + T3])'},
 {'id': 'P044',
  'global_no': 44,
  'district_no': 14,
  'name': 'Zero Waste Industrial Zone',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 8,
  'tech_req': 'T3 + T5',
  'tech_list': ['T3', 'T5'],
  'M': 0,
  'E': 3,
  'ENV': 8,
  'QoL': 3,
  'effects': {'M': 0, 'E': 3, 'ENV': 8, 'QoL': 3},
  'effect_str': '0 / +3 / +8 / +3',
  'effect_summary': '+3 E, +8 ENV, +3 QoL',
  'description': 'Kartu Proyek #14 di Industrial District (ID P044). Biaya: 8 Koin + 1 AP. Syarat Tech: T3 + '
                 'T5. Efek Stat: +3 E, +8 ENV, +3 QoL.',
  'picker_label': '[P044] 🏭 Industrial - Zero Waste Industrial Zone (+3 E, +8 ENV, +3 QoL | 🪙8 [Syarat: T3 + '
                  'T5])'},
 {'id': 'P045',
  'global_no': 45,
  'district_no': 15,
  'name': 'Sustainable Mega Industry',
  'category': 'Project',
  'district': 'Industrial',
  'emoji': '🏭',
  'cost': 9,
  'tech_req': 'T1 + T2 + T3',
  'tech_list': ['T1', 'T2', 'T3'],
  'M': 2,
  'E': 7,
  'ENV': 7,
  'QoL': 3,
  'effects': {'M': 2, 'E': 7, 'ENV': 7, 'QoL': 3},
  'effect_str': '+2 / +7 / +7 / +3',
  'effect_summary': '+2 M, +7 E, +7 ENV, +3 QoL',
  'description': 'Kartu Proyek #15 di Industrial District (ID P045). Biaya: 9 Koin + 1 AP. Syarat Tech: T1 + '
                 'T2 + T3. Efek Stat: +2 M, +7 E, +7 ENV, +3 QoL.',
  'picker_label': '[P045] 🏭 Industrial - Sustainable Mega Industry (+2 M, +7 E, +7 ENV, +3 QoL | 🪙9 [Syarat: '
                  'T1 + T2 + T3])'},
 {'id': 'P046',
  'global_no': 46,
  'district_no': 1,
  'name': 'Public Bus Terminal',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 3,
  'E': 0,
  'ENV': 1,
  'QoL': 1,
  'effects': {'M': 3, 'E': 0, 'ENV': 1, 'QoL': 1},
  'effect_str': '+3 / 0 / +1 / +1',
  'effect_summary': '+3 M, +1 ENV, +1 QoL',
  'description': 'Kartu Proyek #1 di Transportation District (ID P046). Biaya: 3 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +3 M, +1 ENV, +1 QoL.',
  'picker_label': '[P046] 🚝 Transportation - Public Bus Terminal (+3 M, +1 ENV, +1 QoL | 🪙3)'},
 {'id': 'P047',
  'global_no': 47,
  'district_no': 2,
  'name': 'Bicycle Lane Network',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 4,
  'E': 0,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 4, 'E': 0, 'ENV': 3, 'QoL': 2},
  'effect_str': '+4 / 0 / +3 / +2',
  'effect_summary': '+4 M, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #2 di Transportation District (ID P047). Biaya: 4 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +4 M, +3 ENV, +2 QoL.',
  'picker_label': '[P047] 🚝 Transportation - Bicycle Lane Network (+4 M, +3 ENV, +2 QoL | 🪙4)'},
 {'id': 'P048',
  'global_no': 48,
  'district_no': 3,
  'name': 'Electric Bus Station',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 5,
  'tech_req': 'T4',
  'tech_list': ['T4'],
  'M': 5,
  'E': 1,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 5, 'E': 1, 'ENV': 3, 'QoL': 2},
  'effect_str': '+5 / +1 / +3 / +2',
  'effect_summary': '+5 M, +1 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #3 di Transportation District (ID P048). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'T4. Efek Stat: +5 M, +1 E, +3 ENV, +2 QoL.',
  'picker_label': '[P048] 🚝 Transportation - Electric Bus Station (+5 M, +1 E, +3 ENV, +2 QoL | 🪙5 [Syarat: '
                  'T4])'},
 {'id': 'P049',
  'global_no': 49,
  'district_no': 4,
  'name': 'Smart Traffic Light',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 5,
  'E': 0,
  'ENV': 1,
  'QoL': 2,
  'effects': {'M': 5, 'E': 0, 'ENV': 1, 'QoL': 2},
  'effect_str': '+5 / 0 / +1 / +2',
  'effect_summary': '+5 M, +1 ENV, +2 QoL',
  'description': 'Kartu Proyek #4 di Transportation District (ID P049). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'T2. Efek Stat: +5 M, +1 ENV, +2 QoL.',
  'picker_label': '[P049] 🚝 Transportation - Smart Traffic Light (+5 M, +1 ENV, +2 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P050',
  'global_no': 50,
  'district_no': 5,
  'name': 'Metro Station',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 6,
  'tech_req': 'T2 + T4',
  'tech_list': ['T2', 'T4'],
  'M': 6,
  'E': 1,
  'ENV': 2,
  'QoL': 3,
  'effects': {'M': 6, 'E': 1, 'ENV': 2, 'QoL': 3},
  'effect_str': '+6 / +1 / +2 / +3',
  'effect_summary': '+6 M, +1 E, +2 ENV, +3 QoL',
  'description': 'Kartu Proyek #5 di Transportation District (ID P050). Biaya: 6 Koin + 1 AP. Syarat Tech: '
                 'T2 + T4. Efek Stat: +6 M, +1 E, +2 ENV, +3 QoL.',
  'picker_label': '[P050] 🚝 Transportation - Metro Station (+6 M, +1 E, +2 ENV, +3 QoL | 🪙6 [Syarat: T2 + '
                  'T4])'},
 {'id': 'P051',
  'global_no': 51,
  'district_no': 6,
  'name': 'Pedestrian Friendly Road',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 3,
  'E': 0,
  'ENV': 2,
  'QoL': 3,
  'effects': {'M': 3, 'E': 0, 'ENV': 2, 'QoL': 3},
  'effect_str': '+3 / 0 / +2 / +3',
  'effect_summary': '+3 M, +2 ENV, +3 QoL',
  'description': 'Kartu Proyek #6 di Transportation District (ID P051). Biaya: 4 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +3 M, +2 ENV, +3 QoL.',
  'picker_label': '[P051] 🚝 Transportation - Pedestrian Friendly Road (+3 M, +2 ENV, +3 QoL | 🪙4)'},
 {'id': 'P052',
  'global_no': 52,
  'district_no': 7,
  'name': 'Electric Vehicle Charging Hub',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 5,
  'tech_req': 'T1 + T4',
  'tech_list': ['T1', 'T4'],
  'M': 3,
  'E': 3,
  'ENV': 4,
  'QoL': 1,
  'effects': {'M': 3, 'E': 3, 'ENV': 4, 'QoL': 1},
  'effect_str': '+3 / +3 / +4 / +1',
  'effect_summary': '+3 M, +3 E, +4 ENV, +1 QoL',
  'description': 'Kartu Proyek #7 di Transportation District (ID P052). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'T1 + T4. Efek Stat: +3 M, +3 E, +4 ENV, +1 QoL.',
  'picker_label': '[P052] 🚝 Transportation - Electric Vehicle Charging Hub (+3 M, +3 E, +4 ENV, +1 QoL | 🪙5 '
                  '[Syarat: T1 + T4])'},
 {'id': 'P053',
  'global_no': 53,
  'district_no': 8,
  'name': 'Smart Parking System',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 3,
  'E': 1,
  'ENV': 2,
  'QoL': 2,
  'effects': {'M': 3, 'E': 1, 'ENV': 2, 'QoL': 2},
  'effect_str': '+3 / +1 / +2 / +2',
  'effect_summary': '+3 M, +1 E, +2 ENV, +2 QoL',
  'description': 'Kartu Proyek #8 di Transportation District (ID P053). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'T2. Efek Stat: +3 M, +1 E, +2 ENV, +2 QoL.',
  'picker_label': '[P053] 🚝 Transportation - Smart Parking System (+3 M, +1 E, +2 ENV, +2 QoL | 🪙5 [Syarat: '
                  'T2])'},
 {'id': 'P054',
  'global_no': 54,
  'district_no': 9,
  'name': 'High Speed Rail',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 8,
  'tech_req': 'T2 + T4',
  'tech_list': ['T2', 'T4'],
  'M': 8,
  'E': 2,
  'ENV': 3,
  'QoL': 3,
  'effects': {'M': 8, 'E': 2, 'ENV': 3, 'QoL': 3},
  'effect_str': '+8 / +2 / +3 / +3',
  'effect_summary': '+8 M, +2 E, +3 ENV, +3 QoL',
  'description': 'Kartu Proyek #9 di Transportation District (ID P054). Biaya: 8 Koin + 1 AP. Syarat Tech: '
                 'T2 + T4. Efek Stat: +8 M, +2 E, +3 ENV, +3 QoL.',
  'picker_label': '[P054] 🚝 Transportation - High Speed Rail (+8 M, +2 E, +3 ENV, +3 QoL | 🪙8 [Syarat: T2 + '
                  'T4])'},
 {'id': 'P055',
  'global_no': 55,
  'district_no': 10,
  'name': 'Green Transportation Hub',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 7,
  'tech_req': 'T3 + T4',
  'tech_list': ['T3', 'T4'],
  'M': 6,
  'E': 2,
  'ENV': 5,
  'QoL': 3,
  'effects': {'M': 6, 'E': 2, 'ENV': 5, 'QoL': 3},
  'effect_str': '+6 / +2 / +5 / +3',
  'effect_summary': '+6 M, +2 E, +5 ENV, +3 QoL',
  'description': 'Kartu Proyek #10 di Transportation District (ID P055). Biaya: 7 Koin + 1 AP. Syarat Tech: '
                 'T3 + T4. Efek Stat: +6 M, +2 E, +5 ENV, +3 QoL.',
  'picker_label': '[P055] 🚝 Transportation - Green Transportation Hub (+6 M, +2 E, +5 ENV, +3 QoL | 🪙7 '
                  '[Syarat: T3 + T4])'},
 {'id': 'P056',
  'global_no': 56,
  'district_no': 11,
  'name': 'Autonomous Public Transport',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 8,
  'tech_req': 'T2 + T4',
  'tech_list': ['T2', 'T4'],
  'M': 7,
  'E': 2,
  'ENV': 3,
  'QoL': 4,
  'effects': {'M': 7, 'E': 2, 'ENV': 3, 'QoL': 4},
  'effect_str': '+7 / +2 / +3 / +4',
  'effect_summary': '+7 M, +2 E, +3 ENV, +4 QoL',
  'description': 'Kartu Proyek #11 di Transportation District (ID P056). Biaya: 8 Koin + 1 AP. Syarat Tech: '
                 'T2 + T4. Efek Stat: +7 M, +2 E, +3 ENV, +4 QoL.',
  'picker_label': '[P056] 🚝 Transportation - Autonomous Public Transport (+7 M, +2 E, +3 ENV, +4 QoL | 🪙8 '
                  '[Syarat: T2 + T4])'},
 {'id': 'P057',
  'global_no': 57,
  'district_no': 12,
  'name': 'Integrated Transit Network',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 8,
  'tech_req': 'T2 + T4',
  'tech_list': ['T2', 'T4'],
  'M': 8,
  'E': 2,
  'ENV': 3,
  'QoL': 4,
  'effects': {'M': 8, 'E': 2, 'ENV': 3, 'QoL': 4},
  'effect_str': '+8 / +2 / +3 / +4',
  'effect_summary': '+8 M, +2 E, +3 ENV, +4 QoL',
  'description': 'Kartu Proyek #12 di Transportation District (ID P057). Biaya: 8 Koin + 1 AP. Syarat Tech: '
                 'T2 + T4. Efek Stat: +8 M, +2 E, +3 ENV, +4 QoL.',
  'picker_label': '[P057] 🚝 Transportation - Integrated Transit Network (+8 M, +2 E, +3 ENV, +4 QoL | 🪙8 '
                  '[Syarat: T2 + T4])'},
 {'id': 'P058',
  'global_no': 58,
  'district_no': 13,
  'name': 'Urban Cable Transport',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 6,
  'tech_req': 'T4',
  'tech_list': ['T4'],
  'M': 5,
  'E': 1,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 5, 'E': 1, 'ENV': 3, 'QoL': 2},
  'effect_str': '+5 / +1 / +3 / +2',
  'effect_summary': '+5 M, +1 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #13 di Transportation District (ID P058). Biaya: 6 Koin + 1 AP. Syarat Tech: '
                 'T4. Efek Stat: +5 M, +1 E, +3 ENV, +2 QoL.',
  'picker_label': '[P058] 🚝 Transportation - Urban Cable Transport (+5 M, +1 E, +3 ENV, +2 QoL | 🪙6 [Syarat: '
                  'T4])'},
 {'id': 'P059',
  'global_no': 59,
  'district_no': 14,
  'name': 'Zero Emission Mobility',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 9,
  'tech_req': 'T1 + T2 + T4',
  'tech_list': ['T1', 'T2', 'T4'],
  'M': 8,
  'E': 5,
  'ENV': 6,
  'QoL': 4,
  'effects': {'M': 8, 'E': 5, 'ENV': 6, 'QoL': 4},
  'effect_str': '+8 / +5 / +6 / +4',
  'effect_summary': '+8 M, +5 E, +6 ENV, +4 QoL',
  'description': 'Kartu Proyek #14 di Transportation District (ID P059). Biaya: 9 Koin + 1 AP. Syarat Tech: '
                 'T1 + T2 + T4. Efek Stat: +8 M, +5 E, +6 ENV, +4 QoL.',
  'picker_label': '[P059] 🚝 Transportation - Zero Emission Mobility (+8 M, +5 E, +6 ENV, +4 QoL | 🪙9 '
                  '[Syarat: T1 + T2 + T4])'},
 {'id': 'P060',
  'global_no': 60,
  'district_no': 15,
  'name': 'Smart Mobility Megacity',
  'category': 'Project',
  'district': 'Transportation',
  'emoji': '🚝',
  'cost': 10,
  'tech_req': 'T2 + T3 + T4',
  'tech_list': ['T2', 'T3', 'T4'],
  'M': 10,
  'E': 3,
  'ENV': 5,
  'QoL': 5,
  'effects': {'M': 10, 'E': 3, 'ENV': 5, 'QoL': 5},
  'effect_str': '+10 / +3 / +5 / +5',
  'effect_summary': '+10 M, +3 E, +5 ENV, +5 QoL',
  'description': 'Kartu Proyek #15 di Transportation District (ID P060). Biaya: 10 Koin + 1 AP. Syarat Tech: '
                 'T2 + T3 + T4. Efek Stat: +10 M, +3 E, +5 ENV, +5 QoL.',
  'picker_label': '[P060] 🚝 Transportation - Smart Mobility Megacity (+10 M, +3 E, +5 ENV, +5 QoL | 🪙10 '
                  '[Syarat: T2 + T3 + T4])'},
 {'id': 'P061',
  'global_no': 61,
  'district_no': 1,
  'name': 'Public School',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 4,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 4},
  'effect_str': '0 / 0 / 0 / +4',
  'effect_summary': '+4 QoL',
  'description': 'Kartu Proyek #1 di Public Services District (ID P061). Biaya: 3 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +4 QoL.',
  'picker_label': '[P061] 🏥 Public Services - Public School (+4 QoL | 🪙3)'},
 {'id': 'P062',
  'global_no': 62,
  'district_no': 2,
  'name': 'Community Hospital',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 5,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': '0 / 0 / 0 / +5',
  'effect_summary': '+5 QoL',
  'description': 'Kartu Proyek #2 di Public Services District (ID P062). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +5 QoL.',
  'picker_label': '[P062] 🏥 Public Services - Community Hospital (+5 QoL | 🪙5)'},
 {'id': 'P063',
  'global_no': 63,
  'district_no': 3,
  'name': 'Public Library',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 3,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 3},
  'effect_str': '0 / 0 / +1 / +3',
  'effect_summary': '+1 ENV, +3 QoL',
  'description': 'Kartu Proyek #3 di Public Services District (ID P063). Biaya: 3 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +1 ENV, +3 QoL.',
  'picker_label': '[P063] 🏥 Public Services - Public Library (+1 ENV, +3 QoL | 🪙3)'},
 {'id': 'P064',
  'global_no': 64,
  'district_no': 4,
  'name': 'Emergency Response Center',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 4,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 4},
  'effect_str': '0 / 0 / 0 / +4',
  'effect_summary': '+4 QoL',
  'description': 'Kartu Proyek #4 di Public Services District (ID P064). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'T2. Efek Stat: +4 QoL.',
  'picker_label': '[P064] 🏥 Public Services - Emergency Response Center (+4 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P065',
  'global_no': 65,
  'district_no': 5,
  'name': 'Smart Healthcare Center',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 6,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 1,
  'ENV': 1,
  'QoL': 6,
  'effects': {'M': 0, 'E': 1, 'ENV': 1, 'QoL': 6},
  'effect_str': '0 / +1 / +1 / +6',
  'effect_summary': '+1 E, +1 ENV, +6 QoL',
  'description': 'Kartu Proyek #5 di Public Services District (ID P065). Biaya: 6 Koin + 1 AP. Syarat Tech: '
                 'T2. Efek Stat: +1 E, +1 ENV, +6 QoL.',
  'picker_label': '[P065] 🏥 Public Services - Smart Healthcare Center (+1 E, +1 ENV, +6 QoL | 🪙6 [Syarat: '
                  'T2])'},
 {'id': 'P066',
  'global_no': 66,
  'district_no': 6,
  'name': 'Digital Education Center',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 1,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 1, 'ENV': 0, 'QoL': 5},
  'effect_str': '0 / +1 / 0 / +5',
  'effect_summary': '+1 E, +5 QoL',
  'description': 'Kartu Proyek #6 di Public Services District (ID P066). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'T2. Efek Stat: +1 E, +5 QoL.',
  'picker_label': '[P066] 🏥 Public Services - Digital Education Center (+1 E, +5 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P067',
  'global_no': 67,
  'district_no': 7,
  'name': 'Public Safety Network',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': '0 / 0 / 0 / +5',
  'effect_summary': '+5 QoL',
  'description': 'Kartu Proyek #7 di Public Services District (ID P067). Biaya: 5 Koin + 1 AP. Syarat Tech: '
                 'T2. Efek Stat: +5 QoL.',
  'picker_label': '[P067] 🏥 Public Services - Public Safety Network (+5 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P068',
  'global_no': 68,
  'district_no': 8,
  'name': 'Green Hospital',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 6,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 3,
  'ENV': 3,
  'QoL': 5,
  'effects': {'M': 0, 'E': 3, 'ENV': 3, 'QoL': 5},
  'effect_str': '0 / +3 / +3 / +5',
  'effect_summary': '+3 E, +3 ENV, +5 QoL',
  'description': 'Kartu Proyek #8 di Public Services District (ID P068). Biaya: 6 Koin + 1 AP. Syarat Tech: '
                 'T1 + T3. Efek Stat: +3 E, +3 ENV, +5 QoL.',
  'picker_label': '[P068] 🏥 Public Services - Green Hospital (+3 E, +3 ENV, +5 QoL | 🪙6 [Syarat: T1 + T3])'},
 {'id': 'P069',
  'global_no': 69,
  'district_no': 9,
  'name': 'Community Sports Center',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 4,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 4},
  'effect_str': '0 / 0 / +1 / +4',
  'effect_summary': '+1 ENV, +4 QoL',
  'description': 'Kartu Proyek #9 di Public Services District (ID P069). Biaya: 4 Koin + 1 AP. Syarat Tech: '
                 'Tanpa Syarat. Efek Stat: +1 ENV, +4 QoL.',
  'picker_label': '[P069] 🏥 Public Services - Community Sports Center (+1 ENV, +4 QoL | 🪙4)'},
 {'id': 'P070',
  'global_no': 70,
  'district_no': 10,
  'name': 'Disaster Management Center',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 6,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 0,
  'E': 1,
  'ENV': 2,
  'QoL': 5,
  'effects': {'M': 0, 'E': 1, 'ENV': 2, 'QoL': 5},
  'effect_str': '0 / +1 / +2 / +5',
  'effect_summary': '+1 E, +2 ENV, +5 QoL',
  'description': 'Kartu Proyek #10 di Public Services District (ID P070). Biaya: 6 Koin + 1 AP. Syarat Tech: '
                 'T2 + T5. Efek Stat: +1 E, +2 ENV, +5 QoL.',
  'picker_label': '[P070] 🏥 Public Services - Disaster Management Center (+1 E, +2 ENV, +5 QoL | 🪙6 [Syarat: '
                  'T2 + T5])'},
 {'id': 'P071',
  'global_no': 71,
  'district_no': 11,
  'name': 'Smart Government Office',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 6,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 2,
  'ENV': 1,
  'QoL': 5,
  'effects': {'M': 0, 'E': 2, 'ENV': 1, 'QoL': 5},
  'effect_str': '0 / +2 / +1 / +5',
  'effect_summary': '+2 E, +1 ENV, +5 QoL',
  'description': 'Kartu Proyek #11 di Public Services District (ID P071). Biaya: 6 Koin + 1 AP. Syarat Tech: '
                 'T2. Efek Stat: +2 E, +1 ENV, +5 QoL.',
  'picker_label': '[P071] 🏥 Public Services - Smart Government Office (+2 E, +1 ENV, +5 QoL | 🪙6 [Syarat: '
                  'T2])'},
 {'id': 'P072',
  'global_no': 72,
  'district_no': 12,
  'name': 'Public Research Institute',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 6,
  'tech_req': 'T2 + T3',
  'tech_list': ['T2', 'T3'],
  'M': 0,
  'E': 2,
  'ENV': 3,
  'QoL': 5,
  'effects': {'M': 0, 'E': 2, 'ENV': 3, 'QoL': 5},
  'effect_str': '0 / +2 / +3 / +5',
  'effect_summary': '+2 E, +3 ENV, +5 QoL',
  'description': 'Kartu Proyek #12 di Public Services District (ID P072). Biaya: 6 Koin + 1 AP. Syarat Tech: '
                 'T2 + T3. Efek Stat: +2 E, +3 ENV, +5 QoL.',
  'picker_label': '[P072] 🏥 Public Services - Public Research Institute (+2 E, +3 ENV, +5 QoL | 🪙6 [Syarat: '
                  'T2 + T3])'},
 {'id': 'P073',
  'global_no': 73,
  'district_no': 13,
  'name': 'Integrated Health Network',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 7,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 0,
  'E': 1,
  'ENV': 2,
  'QoL': 7,
  'effects': {'M': 0, 'E': 1, 'ENV': 2, 'QoL': 7},
  'effect_str': '0 / +1 / +2 / +7',
  'effect_summary': '+1 E, +2 ENV, +7 QoL',
  'description': 'Kartu Proyek #13 di Public Services District (ID P073). Biaya: 7 Koin + 1 AP. Syarat Tech: '
                 'T2 + T5. Efek Stat: +1 E, +2 ENV, +7 QoL.',
  'picker_label': '[P073] 🏥 Public Services - Integrated Health Network (+1 E, +2 ENV, +7 QoL | 🪙7 [Syarat: '
                  'T2 + T5])'},
 {'id': 'P074',
  'global_no': 74,
  'district_no': 14,
  'name': 'Universal Public Service Hub',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 8,
  'tech_req': 'T2 + T3',
  'tech_list': ['T2', 'T3'],
  'M': 1,
  'E': 2,
  'ENV': 3,
  'QoL': 8,
  'effects': {'M': 1, 'E': 2, 'ENV': 3, 'QoL': 8},
  'effect_str': '+1 / +2 / +3 / +8',
  'effect_summary': '+1 M, +2 E, +3 ENV, +8 QoL',
  'description': 'Kartu Proyek #14 di Public Services District (ID P074). Biaya: 8 Koin + 1 AP. Syarat Tech: '
                 'T2 + T3. Efek Stat: +1 M, +2 E, +3 ENV, +8 QoL.',
  'picker_label': '[P074] 🏥 Public Services - Universal Public Service Hub (+1 M, +2 E, +3 ENV, +8 QoL | 🪙8 '
                  '[Syarat: T2 + T3])'},
 {'id': 'P075',
  'global_no': 75,
  'district_no': 15,
  'name': 'Smart Civic Megacenter',
  'category': 'Project',
  'district': 'Public Services',
  'emoji': '🏥',
  'cost': 9,
  'tech_req': 'T1 + T2 + T5',
  'tech_list': ['T1', 'T2', 'T5'],
  'M': 1,
  'E': 3,
  'ENV': 4,
  'QoL': 9,
  'effects': {'M': 1, 'E': 3, 'ENV': 4, 'QoL': 9},
  'effect_str': '+1 / +3 / +4 / +9',
  'effect_summary': '+1 M, +3 E, +4 ENV, +9 QoL',
  'description': 'Kartu Proyek #15 di Public Services District (ID P075). Biaya: 9 Koin + 1 AP. Syarat Tech: '
                 'T1 + T2 + T5. Efek Stat: +1 M, +3 E, +4 ENV, +9 QoL.',
  'picker_label': '[P075] 🏥 Public Services - Smart Civic Megacenter (+1 M, +3 E, +4 ENV, +9 QoL | 🪙9 '
                  '[Syarat: T1 + T2 + T5])'},
 {'id': 'P076',
  'global_no': 76,
  'district_no': 1,
  'name': 'Local Market',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 2},
  'effect_str': '0 / 0 / 0 / +2',
  'effect_summary': '+2 QoL',
  'description': 'Kartu Proyek #1 di Commercial District (ID P076). Biaya: 3 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +2 QoL.',
  'picker_label': '[P076] 🏬 Commercial - Local Market (+2 QoL | 🪙3)'},
 {'id': 'P077',
  'global_no': 77,
  'district_no': 2,
  'name': 'Shopping Center',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': -1,
  'ENV': 0,
  'QoL': 3,
  'effects': {'M': 0, 'E': -1, 'ENV': 0, 'QoL': 3},
  'effect_str': '0 / -1 / 0 / +3',
  'effect_summary': '-1 E, +3 QoL',
  'description': 'Kartu Proyek #2 di Commercial District (ID P077). Biaya: 4 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: -1 E, +3 QoL.',
  'picker_label': '[P077] 🏬 Commercial - Shopping Center (-1 E, +3 QoL | 🪙4)'},
 {'id': 'P078',
  'global_no': 78,
  'district_no': 3,
  'name': 'Green Business Center',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 2,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 2, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / +2 / +3 / +2',
  'effect_summary': '+2 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #3 di Commercial District (ID P078). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +2 E, +3 ENV, +2 QoL.',
  'picker_label': '[P078] 🏬 Commercial - Green Business Center (+2 E, +3 ENV, +2 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P079',
  'global_no': 79,
  'district_no': 4,
  'name': 'Smart Retail Hub',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 1,
  'ENV': 1,
  'QoL': 3,
  'effects': {'M': 0, 'E': 1, 'ENV': 1, 'QoL': 3},
  'effect_str': '0 / +1 / +1 / +3',
  'effect_summary': '+1 E, +1 ENV, +3 QoL',
  'description': 'Kartu Proyek #4 di Commercial District (ID P079). Biaya: 5 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +1 E, +1 ENV, +3 QoL.',
  'picker_label': '[P079] 🏬 Commercial - Smart Retail Hub (+1 E, +1 ENV, +3 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P080',
  'global_no': 80,
  'district_no': 5,
  'name': 'Digital Commerce Center',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 5,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 2,
  'ENV': 1,
  'QoL': 3,
  'effects': {'M': 0, 'E': 2, 'ENV': 1, 'QoL': 3},
  'effect_str': '0 / +2 / +1 / +3',
  'effect_summary': '+2 E, +1 ENV, +3 QoL',
  'description': 'Kartu Proyek #5 di Commercial District (ID P080). Biaya: 5 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +2 E, +1 ENV, +3 QoL.',
  'picker_label': '[P080] 🏬 Commercial - Digital Commerce Center (+2 E, +1 ENV, +3 QoL | 🪙5 [Syarat: T2])'},
 {'id': 'P081',
  'global_no': 81,
  'district_no': 6,
  'name': 'Sustainable Office Tower',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 6,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 0,
  'E': 4,
  'ENV': 3,
  'QoL': 3,
  'effects': {'M': 0, 'E': 4, 'ENV': 3, 'QoL': 3},
  'effect_str': '0 / +4 / +3 / +3',
  'effect_summary': '+4 E, +3 ENV, +3 QoL',
  'description': 'Kartu Proyek #6 di Commercial District (ID P081). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 + '
                 'T2. Efek Stat: +4 E, +3 ENV, +3 QoL.',
  'picker_label': '[P081] 🏬 Commercial - Sustainable Office Tower (+4 E, +3 ENV, +3 QoL | 🪙6 [Syarat: T1 + '
                  'T2])'},
 {'id': 'P082',
  'global_no': 82,
  'district_no': 7,
  'name': 'Eco Tourism Center',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 1,
  'E': 0,
  'ENV': 4,
  'QoL': 3,
  'effects': {'M': 1, 'E': 0, 'ENV': 4, 'QoL': 3},
  'effect_str': '+1 / 0 / +4 / +3',
  'effect_summary': '+1 M, +4 ENV, +3 QoL',
  'description': 'Kartu Proyek #7 di Commercial District (ID P082). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. '
                 'Efek Stat: +1 M, +4 ENV, +3 QoL.',
  'picker_label': '[P082] 🏬 Commercial - Eco Tourism Center (+1 M, +4 ENV, +3 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P083',
  'global_no': 83,
  'district_no': 8,
  'name': 'Green Shopping Mall',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 6,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 3,
  'ENV': 4,
  'QoL': 3,
  'effects': {'M': 0, 'E': 3, 'ENV': 4, 'QoL': 3},
  'effect_str': '0 / +3 / +4 / +3',
  'effect_summary': '+3 E, +4 ENV, +3 QoL',
  'description': 'Kartu Proyek #8 di Commercial District (ID P083). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 + '
                 'T3. Efek Stat: +3 E, +4 ENV, +3 QoL.',
  'picker_label': '[P083] 🏬 Commercial - Green Shopping Mall (+3 E, +4 ENV, +3 QoL | 🪙6 [Syarat: T1 + T3])'},
 {'id': 'P084',
  'global_no': 84,
  'district_no': 9,
  'name': 'Innovation Business Park',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 6,
  'tech_req': 'T2 + T3',
  'tech_list': ['T2', 'T3'],
  'M': 0,
  'E': 2,
  'ENV': 2,
  'QoL': 4,
  'effects': {'M': 0, 'E': 2, 'ENV': 2, 'QoL': 4},
  'effect_str': '0 / +2 / +2 / +4',
  'effect_summary': '+2 E, +2 ENV, +4 QoL',
  'description': 'Kartu Proyek #9 di Commercial District (ID P084). Biaya: 6 Koin + 1 AP. Syarat Tech: T2 + '
                 'T3. Efek Stat: +2 E, +2 ENV, +4 QoL.',
  'picker_label': '[P084] 🏬 Commercial - Innovation Business Park (+2 E, +2 ENV, +4 QoL | 🪙6 [Syarat: T2 + '
                  'T3])'},
 {'id': 'P085',
  'global_no': 85,
  'district_no': 10,
  'name': 'Smart Financial District',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 7,
  'tech_req': 'T2',
  'tech_list': ['T2'],
  'M': 0,
  'E': 2,
  'ENV': 1,
  'QoL': 4,
  'effects': {'M': 0, 'E': 2, 'ENV': 1, 'QoL': 4},
  'effect_str': '0 / +2 / +1 / +4',
  'effect_summary': '+2 E, +1 ENV, +4 QoL',
  'description': 'Kartu Proyek #10 di Commercial District (ID P085). Biaya: 7 Koin + 1 AP. Syarat Tech: T2. '
                 'Efek Stat: +2 E, +1 ENV, +4 QoL.',
  'picker_label': '[P085] 🏬 Commercial - Smart Financial District (+2 E, +1 ENV, +4 QoL | 🪙7 [Syarat: T2])'},
 {'id': 'P086',
  'global_no': 86,
  'district_no': 11,
  'name': 'Low Carbon Business Hub',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 7,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 4,
  'ENV': 5,
  'QoL': 3,
  'effects': {'M': 0, 'E': 4, 'ENV': 5, 'QoL': 3},
  'effect_str': '0 / +4 / +5 / +3',
  'effect_summary': '+4 E, +5 ENV, +3 QoL',
  'description': 'Kartu Proyek #11 di Commercial District (ID P086). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + '
                 'T3. Efek Stat: +4 E, +5 ENV, +3 QoL.',
  'picker_label': '[P086] 🏬 Commercial - Low Carbon Business Hub (+4 E, +5 ENV, +3 QoL | 🪙7 [Syarat: T1 + '
                  'T3])'},
 {'id': 'P087',
  'global_no': 87,
  'district_no': 12,
  'name': 'Integrated Commercial Zone',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 7,
  'tech_req': 'T2 + T4',
  'tech_list': ['T2', 'T4'],
  'M': 2,
  'E': 2,
  'ENV': 2,
  'QoL': 4,
  'effects': {'M': 2, 'E': 2, 'ENV': 2, 'QoL': 4},
  'effect_str': '+2 / +2 / +2 / +4',
  'effect_summary': '+2 M, +2 E, +2 ENV, +4 QoL',
  'description': 'Kartu Proyek #12 di Commercial District (ID P087). Biaya: 7 Koin + 1 AP. Syarat Tech: T2 + '
                 'T4. Efek Stat: +2 M, +2 E, +2 ENV, +4 QoL.',
  'picker_label': '[P087] 🏬 Commercial - Integrated Commercial Zone (+2 M, +2 E, +2 ENV, +4 QoL | 🪙7 '
                  '[Syarat: T2 + T4])'},
 {'id': 'P088',
  'global_no': 88,
  'district_no': 13,
  'name': 'Sustainable Convention Center',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 7,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 1,
  'E': 3,
  'ENV': 3,
  'QoL': 5,
  'effects': {'M': 1, 'E': 3, 'ENV': 3, 'QoL': 5},
  'effect_str': '+1 / +3 / +3 / +5',
  'effect_summary': '+1 M, +3 E, +3 ENV, +5 QoL',
  'description': 'Kartu Proyek #13 di Commercial District (ID P088). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + '
                 'T2. Efek Stat: +1 M, +3 E, +3 ENV, +5 QoL.',
  'picker_label': '[P088] 🏬 Commercial - Sustainable Convention Center (+1 M, +3 E, +3 ENV, +5 QoL | 🪙7 '
                  '[Syarat: T1 + T2])'},
 {'id': 'P089',
  'global_no': 89,
  'district_no': 14,
  'name': 'Green Innovation District',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 8,
  'tech_req': 'T1 + T2 + T3',
  'tech_list': ['T1', 'T2', 'T3'],
  'M': 0,
  'E': 5,
  'ENV': 6,
  'QoL': 4,
  'effects': {'M': 0, 'E': 5, 'ENV': 6, 'QoL': 4},
  'effect_str': '0 / +5 / +6 / +4',
  'effect_summary': '+5 E, +6 ENV, +4 QoL',
  'description': 'Kartu Proyek #14 di Commercial District (ID P089). Biaya: 8 Koin + 1 AP. Syarat Tech: T1 + '
                 'T2 + T3. Efek Stat: +5 E, +6 ENV, +4 QoL.',
  'picker_label': '[P089] 🏬 Commercial - Green Innovation District (+5 E, +6 ENV, +4 QoL | 🪙8 [Syarat: T1 + '
                  'T2 + T3])'},
 {'id': 'P090',
  'global_no': 90,
  'district_no': 15,
  'name': 'Future Smart Economy Center',
  'category': 'Project',
  'district': 'Commercial',
  'emoji': '🏬',
  'cost': 9,
  'tech_req': 'T1 + T2 + T3',
  'tech_list': ['T1', 'T2', 'T3'],
  'M': 2,
  'E': 6,
  'ENV': 5,
  'QoL': 6,
  'effects': {'M': 2, 'E': 6, 'ENV': 5, 'QoL': 6},
  'effect_str': '+2 / +6 / +5 / +6',
  'effect_summary': '+2 M, +6 E, +5 ENV, +6 QoL',
  'description': 'Kartu Proyek #15 di Commercial District (ID P090). Biaya: 9 Koin + 1 AP. Syarat Tech: T1 + '
                 'T2 + T3. Efek Stat: +2 M, +6 E, +5 ENV, +6 QoL.',
  'picker_label': '[P090] 🏬 Commercial - Future Smart Economy Center (+2 M, +6 E, +5 ENV, +6 QoL | 🪙9 '
                  '[Syarat: T1 + T2 + T3])'},
 {'id': 'P091',
  'global_no': 91,
  'district_no': 1,
  'name': 'Solar Panel Station',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 3,
  'ENV': 2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 3, 'ENV': 2, 'QoL': 0},
  'effect_str': '0 / +3 / +2 / 0',
  'effect_summary': '+3 E, +2 ENV',
  'description': 'Kartu Proyek #1 di Energy District (ID P091). Biaya: 3 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +3 E, +2 ENV.',
  'picker_label': '[P091] ⚡ Energy - Solar Panel Station (+3 E, +2 ENV | 🪙3)'},
 {'id': 'P092',
  'global_no': 92,
  'district_no': 2,
  'name': 'Wind Turbine Farm',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 4,
  'ENV': 3,
  'QoL': 0,
  'effects': {'M': 0, 'E': 4, 'ENV': 3, 'QoL': 0},
  'effect_str': '0 / +4 / +3 / 0',
  'effect_summary': '+4 E, +3 ENV',
  'description': 'Kartu Proyek #2 di Energy District (ID P092). Biaya: 4 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +4 E, +3 ENV.',
  'picker_label': '[P092] ⚡ Energy - Wind Turbine Farm (+4 E, +3 ENV | 🪙4)'},
 {'id': 'P093',
  'global_no': 93,
  'district_no': 3,
  'name': 'Micro Hydropower Plant',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 5,
  'tech_req': 'T5',
  'tech_list': ['T5'],
  'M': 0,
  'E': 4,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 0, 'E': 4, 'ENV': 3, 'QoL': 1},
  'effect_str': '0 / +4 / +3 / +1',
  'effect_summary': '+4 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #3 di Energy District (ID P093). Biaya: 5 Koin + 1 AP. Syarat Tech: T5. Efek '
                 'Stat: +4 E, +3 ENV, +1 QoL.',
  'picker_label': '[P093] ⚡ Energy - Micro Hydropower Plant (+4 E, +3 ENV, +1 QoL | 🪙5 [Syarat: T5])'},
 {'id': 'P094',
  'global_no': 94,
  'district_no': 4,
  'name': 'Smart Power Grid',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 6,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 0,
  'E': 6,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 0, 'E': 6, 'ENV': 3, 'QoL': 1},
  'effect_str': '0 / +6 / +3 / +1',
  'effect_summary': '+6 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #4 di Energy District (ID P094). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 + T2. '
                 'Efek Stat: +6 E, +3 ENV, +1 QoL.',
  'picker_label': '[P094] ⚡ Energy - Smart Power Grid (+6 E, +3 ENV, +1 QoL | 🪙6 [Syarat: T1 + T2])'},
 {'id': 'P095',
  'global_no': 95,
  'district_no': 5,
  'name': 'Battery Storage Facility',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 5,
  'tech_req': 'T1',
  'tech_list': ['T1'],
  'M': 0,
  'E': 5,
  'ENV': 1,
  'QoL': 1,
  'effects': {'M': 0, 'E': 5, 'ENV': 1, 'QoL': 1},
  'effect_str': '0 / +5 / +1 / +1',
  'effect_summary': '+5 E, +1 ENV, +1 QoL',
  'description': 'Kartu Proyek #5 di Energy District (ID P095). Biaya: 5 Koin + 1 AP. Syarat Tech: T1. Efek '
                 'Stat: +5 E, +1 ENV, +1 QoL.',
  'picker_label': '[P095] ⚡ Energy - Battery Storage Facility (+5 E, +1 ENV, +1 QoL | 🪙5 [Syarat: T1])'},
 {'id': 'P096',
  'global_no': 96,
  'district_no': 6,
  'name': 'Biogas Power Plant',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 4,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 0, 'E': 4, 'ENV': 3, 'QoL': 1},
  'effect_str': '0 / +4 / +3 / +1',
  'effect_summary': '+4 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #6 di Energy District (ID P096). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. Efek '
                 'Stat: +4 E, +3 ENV, +1 QoL.',
  'picker_label': '[P096] ⚡ Energy - Biogas Power Plant (+4 E, +3 ENV, +1 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P097',
  'global_no': 97,
  'district_no': 7,
  'name': 'Geothermal Energy Station',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 6,
  'tech_req': 'T1',
  'tech_list': ['T1'],
  'M': 0,
  'E': 6,
  'ENV': 3,
  'QoL': 1,
  'effects': {'M': 0, 'E': 6, 'ENV': 3, 'QoL': 1},
  'effect_str': '0 / +6 / +3 / +1',
  'effect_summary': '+6 E, +3 ENV, +1 QoL',
  'description': 'Kartu Proyek #7 di Energy District (ID P097). Biaya: 6 Koin + 1 AP. Syarat Tech: T1. Efek '
                 'Stat: +6 E, +3 ENV, +1 QoL.',
  'picker_label': '[P097] ⚡ Energy - Geothermal Energy Station (+6 E, +3 ENV, +1 QoL | 🪙6 [Syarat: T1])'},
 {'id': 'P098',
  'global_no': 98,
  'district_no': 8,
  'name': 'Solar Farm',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 6,
  'tech_req': 'T1',
  'tech_list': ['T1'],
  'M': 0,
  'E': 7,
  'ENV': 3,
  'QoL': 0,
  'effects': {'M': 0, 'E': 7, 'ENV': 3, 'QoL': 0},
  'effect_str': '0 / +7 / +3 / 0',
  'effect_summary': '+7 E, +3 ENV',
  'description': 'Kartu Proyek #8 di Energy District (ID P098). Biaya: 6 Koin + 1 AP. Syarat Tech: T1. Efek '
                 'Stat: +7 E, +3 ENV.',
  'picker_label': '[P098] ⚡ Energy - Solar Farm (+7 E, +3 ENV | 🪙6 [Syarat: T1])'},
 {'id': 'P099',
  'global_no': 99,
  'district_no': 9,
  'name': 'Energy Efficient Network',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 6,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 0,
  'E': 5,
  'ENV': 4,
  'QoL': 2,
  'effects': {'M': 0, 'E': 5, 'ENV': 4, 'QoL': 2},
  'effect_str': '0 / +5 / +4 / +2',
  'effect_summary': '+5 E, +4 ENV, +2 QoL',
  'description': 'Kartu Proyek #9 di Energy District (ID P099). Biaya: 6 Koin + 1 AP. Syarat Tech: T1 + T2. '
                 'Efek Stat: +5 E, +4 ENV, +2 QoL.',
  'picker_label': '[P099] ⚡ Energy - Energy Efficient Network (+5 E, +4 ENV, +2 QoL | 🪙6 [Syarat: T1 + T2])'},
 {'id': 'P100',
  'global_no': 100,
  'district_no': 10,
  'name': 'Hydrogen Energy Center',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 7,
  'tech_req': 'T1 + T3',
  'tech_list': ['T1', 'T3'],
  'M': 0,
  'E': 6,
  'ENV': 4,
  'QoL': 1,
  'effects': {'M': 0, 'E': 6, 'ENV': 4, 'QoL': 1},
  'effect_str': '0 / +6 / +4 / +1',
  'effect_summary': '+6 E, +4 ENV, +1 QoL',
  'description': 'Kartu Proyek #10 di Energy District (ID P100). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + T3. '
                 'Efek Stat: +6 E, +4 ENV, +1 QoL.',
  'picker_label': '[P100] ⚡ Energy - Hydrogen Energy Center (+6 E, +4 ENV, +1 QoL | 🪙7 [Syarat: T1 + T3])'},
 {'id': 'P101',
  'global_no': 101,
  'district_no': 11,
  'name': 'Smart Energy Storage',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 7,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 0,
  'E': 7,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 7, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / +7 / +3 / +2',
  'effect_summary': '+7 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #11 di Energy District (ID P101). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + T2. '
                 'Efek Stat: +7 E, +3 ENV, +2 QoL.',
  'picker_label': '[P101] ⚡ Energy - Smart Energy Storage (+7 E, +3 ENV, +2 QoL | 🪙7 [Syarat: T1 + T2])'},
 {'id': 'P102',
  'global_no': 102,
  'district_no': 12,
  'name': 'Renewable Energy Research',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 7,
  'tech_req': 'T1 + T2 + T3',
  'tech_list': ['T1', 'T2', 'T3'],
  'M': 0,
  'E': 6,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 6, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / +6 / +5 / +2',
  'effect_summary': '+6 E, +5 ENV, +2 QoL',
  'description': 'Kartu Proyek #12 di Energy District (ID P102). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + T2 '
                 '+ T3. Efek Stat: +6 E, +5 ENV, +2 QoL.',
  'picker_label': '[P102] ⚡ Energy - Renewable Energy Research (+6 E, +5 ENV, +2 QoL | 🪙7 [Syarat: T1 + T2 + '
                  'T3])'},
 {'id': 'P103',
  'global_no': 103,
  'district_no': 13,
  'name': 'Distributed Energy Network',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 8,
  'tech_req': 'T1 + T2',
  'tech_list': ['T1', 'T2'],
  'M': 0,
  'E': 7,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 7, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / +7 / +5 / +2',
  'effect_summary': '+7 E, +5 ENV, +2 QoL',
  'description': 'Kartu Proyek #13 di Energy District (ID P103). Biaya: 8 Koin + 1 AP. Syarat Tech: T1 + T2. '
                 'Efek Stat: +7 E, +5 ENV, +2 QoL.',
  'picker_label': '[P103] ⚡ Energy - Distributed Energy Network (+7 E, +5 ENV, +2 QoL | 🪙8 [Syarat: T1 + '
                  'T2])'},
 {'id': 'P104',
  'global_no': 104,
  'district_no': 14,
  'name': 'Zero Carbon Power Plant',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 9,
  'tech_req': 'T1 + T3 + T5',
  'tech_list': ['T1', 'T3', 'T5'],
  'M': 0,
  'E': 8,
  'ENV': 7,
  'QoL': 2,
  'effects': {'M': 0, 'E': 8, 'ENV': 7, 'QoL': 2},
  'effect_str': '0 / +8 / +7 / +2',
  'effect_summary': '+8 E, +7 ENV, +2 QoL',
  'description': 'Kartu Proyek #14 di Energy District (ID P104). Biaya: 9 Koin + 1 AP. Syarat Tech: T1 + T3 '
                 '+ T5. Efek Stat: +8 E, +7 ENV, +2 QoL.',
  'picker_label': '[P104] ⚡ Energy - Zero Carbon Power Plant (+8 E, +7 ENV, +2 QoL | 🪙9 [Syarat: T1 + T3 + '
                  'T5])'},
 {'id': 'P105',
  'global_no': 105,
  'district_no': 15,
  'name': 'Renewable Energy Megagrid',
  'category': 'Project',
  'district': 'Energy',
  'emoji': '⚡',
  'cost': 10,
  'tech_req': 'T1 + T2 + T3',
  'tech_list': ['T1', 'T2', 'T3'],
  'M': 1,
  'E': 10,
  'ENV': 7,
  'QoL': 3,
  'effects': {'M': 1, 'E': 10, 'ENV': 7, 'QoL': 3},
  'effect_str': '+1 / +10 / +7 / +3',
  'effect_summary': '+1 M, +10 E, +7 ENV, +3 QoL',
  'description': 'Kartu Proyek #15 di Energy District (ID P105). Biaya: 10 Koin + 1 AP. Syarat Tech: T1 + T2 '
                 '+ T3. Efek Stat: +1 M, +10 E, +7 ENV, +3 QoL.',
  'picker_label': '[P105] ⚡ Energy - Renewable Energy Megagrid (+1 M, +10 E, +7 ENV, +3 QoL | 🪙10 [Syarat: '
                  'T1 + T2 + T3])'},
 {'id': 'P106',
  'global_no': 106,
  'district_no': 1,
  'name': 'Public Water Station',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 3,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 2},
  'effect_str': '0 / 0 / +2 / +2',
  'effect_summary': '+2 ENV, +2 QoL',
  'description': 'Kartu Proyek #1 di Water District (ID P106). Biaya: 3 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +2 ENV, +2 QoL.',
  'picker_label': '[P106] 💧 Water - Public Water Station (+2 ENV, +2 QoL | 🪙3)'},
 {'id': 'P107',
  'global_no': 107,
  'district_no': 2,
  'name': 'Water Treatment Plant',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 1,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 1, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / +1 / +3 / +2',
  'effect_summary': '+1 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #2 di Water District (ID P107). Biaya: 4 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +1 E, +3 ENV, +2 QoL.',
  'picker_label': '[P107] 💧 Water - Water Treatment Plant (+1 E, +3 ENV, +2 QoL | 🪙4)'},
 {'id': 'P108',
  'global_no': 108,
  'district_no': 3,
  'name': 'Rainwater Harvesting',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 4,
  'tech_req': '-',
  'tech_list': [],
  'M': 0,
  'E': 1,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 1, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / +1 / +3 / +2',
  'effect_summary': '+1 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #3 di Water District (ID P108). Biaya: 4 Koin + 1 AP. Syarat Tech: Tanpa '
                 'Syarat. Efek Stat: +1 E, +3 ENV, +2 QoL.',
  'picker_label': '[P108] 💧 Water - Rainwater Harvesting (+1 E, +3 ENV, +2 QoL | 🪙4)'},
 {'id': 'P109',
  'global_no': 109,
  'district_no': 4,
  'name': 'Smart Water Meter',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 5,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 0,
  'E': 2,
  'ENV': 3,
  'QoL': 2,
  'effects': {'M': 0, 'E': 2, 'ENV': 3, 'QoL': 2},
  'effect_str': '0 / +2 / +3 / +2',
  'effect_summary': '+2 E, +3 ENV, +2 QoL',
  'description': 'Kartu Proyek #4 di Water District (ID P109). Biaya: 5 Koin + 1 AP. Syarat Tech: T2 + T5. '
                 'Efek Stat: +2 E, +3 ENV, +2 QoL.',
  'picker_label': '[P109] 💧 Water - Smart Water Meter (+2 E, +3 ENV, +2 QoL | 🪙5 [Syarat: T2 + T5])'},
 {'id': 'P110',
  'global_no': 110,
  'district_no': 5,
  'name': 'Wastewater Treatment',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 5,
  'tech_req': 'T5',
  'tech_list': ['T5'],
  'M': 0,
  'E': 1,
  'ENV': 5,
  'QoL': 2,
  'effects': {'M': 0, 'E': 1, 'ENV': 5, 'QoL': 2},
  'effect_str': '0 / +1 / +5 / +2',
  'effect_summary': '+1 E, +5 ENV, +2 QoL',
  'description': 'Kartu Proyek #5 di Water District (ID P110). Biaya: 5 Koin + 1 AP. Syarat Tech: T5. Efek '
                 'Stat: +1 E, +5 ENV, +2 QoL.',
  'picker_label': '[P110] 💧 Water - Wastewater Treatment (+1 E, +5 ENV, +2 QoL | 🪙5 [Syarat: T5])'},
 {'id': 'P111',
  'global_no': 111,
  'district_no': 6,
  'name': 'River Restoration',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 5,
  'tech_req': 'T3',
  'tech_list': ['T3'],
  'M': 0,
  'E': 0,
  'ENV': 6,
  'QoL': 2,
  'effects': {'M': 0, 'E': 0, 'ENV': 6, 'QoL': 2},
  'effect_str': '0 / 0 / +6 / +2',
  'effect_summary': '+6 ENV, +2 QoL',
  'description': 'Kartu Proyek #6 di Water District (ID P111). Biaya: 5 Koin + 1 AP. Syarat Tech: T3. Efek '
                 'Stat: +6 ENV, +2 QoL.',
  'picker_label': '[P111] 💧 Water - River Restoration (+6 ENV, +2 QoL | 🪙5 [Syarat: T3])'},
 {'id': 'P112',
  'global_no': 112,
  'district_no': 7,
  'name': 'Flood Control System',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 5,
  'tech_req': 'T5',
  'tech_list': ['T5'],
  'M': 0,
  'E': 1,
  'ENV': 4,
  'QoL': 3,
  'effects': {'M': 0, 'E': 1, 'ENV': 4, 'QoL': 3},
  'effect_str': '0 / +1 / +4 / +3',
  'effect_summary': '+1 E, +4 ENV, +3 QoL',
  'description': 'Kartu Proyek #7 di Water District (ID P112). Biaya: 5 Koin + 1 AP. Syarat Tech: T5. Efek '
                 'Stat: +1 E, +4 ENV, +3 QoL.',
  'picker_label': '[P112] 💧 Water - Flood Control System (+1 E, +4 ENV, +3 QoL | 🪙5 [Syarat: T5])'},
 {'id': 'P113',
  'global_no': 113,
  'district_no': 8,
  'name': 'Water Recycling Center',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 6,
  'tech_req': 'T3 + T5',
  'tech_list': ['T3', 'T5'],
  'M': 0,
  'E': 2,
  'ENV': 6,
  'QoL': 2,
  'effects': {'M': 0, 'E': 2, 'ENV': 6, 'QoL': 2},
  'effect_str': '0 / +2 / +6 / +2',
  'effect_summary': '+2 E, +6 ENV, +2 QoL',
  'description': 'Kartu Proyek #8 di Water District (ID P113). Biaya: 6 Koin + 1 AP. Syarat Tech: T3 + T5. '
                 'Efek Stat: +2 E, +6 ENV, +2 QoL.',
  'picker_label': '[P113] 💧 Water - Water Recycling Center (+2 E, +6 ENV, +2 QoL | 🪙6 [Syarat: T3 + T5])'},
 {'id': 'P114',
  'global_no': 114,
  'district_no': 9,
  'name': 'Smart Irrigation Network',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 6,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 0,
  'E': 2,
  'ENV': 4,
  'QoL': 3,
  'effects': {'M': 0, 'E': 2, 'ENV': 4, 'QoL': 3},
  'effect_str': '0 / +2 / +4 / +3',
  'effect_summary': '+2 E, +4 ENV, +3 QoL',
  'description': 'Kartu Proyek #9 di Water District (ID P114). Biaya: 6 Koin + 1 AP. Syarat Tech: T2 + T5. '
                 'Efek Stat: +2 E, +4 ENV, +3 QoL.',
  'picker_label': '[P114] 💧 Water - Smart Irrigation Network (+2 E, +4 ENV, +3 QoL | 🪙6 [Syarat: T2 + T5])'},
 {'id': 'P115',
  'global_no': 115,
  'district_no': 10,
  'name': 'Desalination Plant',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 7,
  'tech_req': 'T1 + T5',
  'tech_list': ['T1', 'T5'],
  'M': 0,
  'E': 4,
  'ENV': 4,
  'QoL': 3,
  'effects': {'M': 0, 'E': 4, 'ENV': 4, 'QoL': 3},
  'effect_str': '0 / +4 / +4 / +3',
  'effect_summary': '+4 E, +4 ENV, +3 QoL',
  'description': 'Kartu Proyek #10 di Water District (ID P115). Biaya: 7 Koin + 1 AP. Syarat Tech: T1 + T5. '
                 'Efek Stat: +4 E, +4 ENV, +3 QoL.',
  'picker_label': '[P115] 💧 Water - Desalination Plant (+4 E, +4 ENV, +3 QoL | 🪙7 [Syarat: T1 + T5])'},
 {'id': 'P116',
  'global_no': 116,
  'district_no': 11,
  'name': 'Urban Drainage Network',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 6,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 1,
  'E': 1,
  'ENV': 4,
  'QoL': 3,
  'effects': {'M': 1, 'E': 1, 'ENV': 4, 'QoL': 3},
  'effect_str': '+1 / +1 / +4 / +3',
  'effect_summary': '+1 M, +1 E, +4 ENV, +3 QoL',
  'description': 'Kartu Proyek #11 di Water District (ID P116). Biaya: 6 Koin + 1 AP. Syarat Tech: T2 + T5. '
                 'Efek Stat: +1 M, +1 E, +4 ENV, +3 QoL.',
  'picker_label': '[P116] 💧 Water - Urban Drainage Network (+1 M, +1 E, +4 ENV, +3 QoL | 🪙6 [Syarat: T2 + '
                  'T5])'},
 {'id': 'P117',
  'global_no': 117,
  'district_no': 12,
  'name': 'Aquatic Ecosystem Protection',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 6,
  'tech_req': 'T3 + T5',
  'tech_list': ['T3', 'T5'],
  'M': 0,
  'E': 0,
  'ENV': 7,
  'QoL': 3,
  'effects': {'M': 0, 'E': 0, 'ENV': 7, 'QoL': 3},
  'effect_str': '0 / 0 / +7 / +3',
  'effect_summary': '+7 ENV, +3 QoL',
  'description': 'Kartu Proyek #12 di Water District (ID P117). Biaya: 6 Koin + 1 AP. Syarat Tech: T3 + T5. '
                 'Efek Stat: +7 ENV, +3 QoL.',
  'picker_label': '[P117] 💧 Water - Aquatic Ecosystem Protection (+7 ENV, +3 QoL | 🪙6 [Syarat: T3 + T5])'},
 {'id': 'P118',
  'global_no': 118,
  'district_no': 13,
  'name': 'Smart Water Distribution',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 7,
  'tech_req': 'T2 + T5',
  'tech_list': ['T2', 'T5'],
  'M': 1,
  'E': 2,
  'ENV': 5,
  'QoL': 4,
  'effects': {'M': 1, 'E': 2, 'ENV': 5, 'QoL': 4},
  'effect_str': '+1 / +2 / +5 / +4',
  'effect_summary': '+1 M, +2 E, +5 ENV, +4 QoL',
  'description': 'Kartu Proyek #13 di Water District (ID P118). Biaya: 7 Koin + 1 AP. Syarat Tech: T2 + T5. '
                 'Efek Stat: +1 M, +2 E, +5 ENV, +4 QoL.',
  'picker_label': '[P118] 💧 Water - Smart Water Distribution (+1 M, +2 E, +5 ENV, +4 QoL | 🪙7 [Syarat: T2 + '
                  'T5])'},
 {'id': 'P119',
  'global_no': 119,
  'district_no': 14,
  'name': 'Zero Wastewater City',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 8,
  'tech_req': 'T3 + T5',
  'tech_list': ['T3', 'T5'],
  'M': 0,
  'E': 3,
  'ENV': 8,
  'QoL': 4,
  'effects': {'M': 0, 'E': 3, 'ENV': 8, 'QoL': 4},
  'effect_str': '0 / +3 / +8 / +4',
  'effect_summary': '+3 E, +8 ENV, +4 QoL',
  'description': 'Kartu Proyek #14 di Water District (ID P119). Biaya: 8 Koin + 1 AP. Syarat Tech: T3 + T5. '
                 'Efek Stat: +3 E, +8 ENV, +4 QoL.',
  'picker_label': '[P119] 💧 Water - Zero Wastewater City (+3 E, +8 ENV, +4 QoL | 🪙8 [Syarat: T3 + T5])'},
 {'id': 'P120',
  'global_no': 120,
  'district_no': 15,
  'name': 'Integrated Water Security System',
  'category': 'Project',
  'district': 'Water',
  'emoji': '💧',
  'cost': 9,
  'tech_req': 'T1 + T2 + T5',
  'tech_list': ['T1', 'T2', 'T5'],
  'M': 1,
  'E': 4,
  'ENV': 8,
  'QoL': 5,
  'effects': {'M': 1, 'E': 4, 'ENV': 8, 'QoL': 5},
  'effect_str': '+1 / +4 / +8 / +5',
  'effect_summary': '+1 M, +4 E, +8 ENV, +5 QoL',
  'description': 'Kartu Proyek #15 di Water District (ID P120). Biaya: 9 Koin + 1 AP. Syarat Tech: T1 + T2 + '
                 'T5. Efek Stat: +1 M, +4 E, +8 ENV, +5 QoL.',
  'picker_label': '[P120] 💧 Water - Integrated Water Security System (+1 M, +4 E, +8 ENV, +5 QoL | 🪙9 '
                  '[Syarat: T1 + T2 + T5])'}]

PERMANENT_TECH_CARDS: List[Dict[str, Any]] = [{'id': 'T1',
  'code': 'T1',
  'name': 'Solar Engineering',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '☀️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 2,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 2, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Energy +2',
  'effect_summary': '+2 E (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Energy +2 serta menjadi syarat pembangunan proyek bertanda T1 dan solusi krisis '
                 'energi.',
  'picker_label': '[T1] ☀️ Solar Engineering (+2 E Pasif | 🪙5)'},
 {'id': 'T2',
  'code': 'T2',
  'name': 'AI Urban System',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🤖',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 1,
  'E': 0,
  'ENV': 0,
  'QoL': 1,
  'effects': {'M': 1, 'E': 0, 'ENV': 0, 'QoL': 1},
  'effect_str': 'Mobility +1, QoL +1',
  'effect_summary': '+1 M, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +1, QoL +1 serta menjadi syarat pembangunan proyek pintar bertanda T2.',
  'picker_label': '[T2] 🤖 AI Urban System (+1 M, +1 QoL Pasif | 🪙5)'},
 {'id': 'T3',
  'code': 'T3',
  'name': 'Circular Materials',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '♻️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 0},
  'effect_str': 'Environment +2',
  'effect_summary': '+2 ENV (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +2 serta menjadi syarat pembangunan proyek ekologis bertanda T3.',
  'picker_label': '[T3] ♻️ Circular Materials (+2 ENV Pasif | 🪙5)'},
 {'id': 'T4',
  'code': 'T4',
  'name': 'Electric Mobility',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🚝',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 2,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 2, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +2',
  'effect_summary': '+2 M (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +2, melindungi dari Global Fuel Crisis (R2), dan syarat proyek transit '
                 'T4.',
  'picker_label': '[T4] 🚝 Electric Mobility (+2 M Pasif | 🪙5)'},
 {'id': 'T5',
  'code': 'T5',
  'name': 'Water Purification',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '💧',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 1,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 1},
  'effect_str': 'Environment +1, QoL +1',
  'effect_summary': '+1 ENV, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +1, QoL +1 serta syarat proyek air bersih dan ketahanan banjir T5.',
  'picker_label': '[T5] 💧 Water Purification (+1 ENV, +1 QoL Pasif | 🪙5)'}]

CONSUMABLE_SKILL_CARDS: List[Dict[str, Any]] = [{'id': 'S1',
  'code': 'S1',
  'name': 'Emergency Response',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚑',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu Problem Card yang menyebabkan penalti.',
  'effect_summary': 'Batalkan 1 Problem Card',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk membatalkan 1 Problem Card yang menyebabkan penalti.',
  'picker_label': '[S1] 🚑 Emergency Response (Batalkan 1 Problem | 🪙3)'},
 {'id': 'S2',
  'code': 'S2',
  'name': 'Carbon Capture Boost',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🌿',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 0},
  'effect_str': 'Environment +5.',
  'effect_summary': '+5 ENV (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Environment +5 atau mengatasi Severe Air Pollution / Extreme '
                 'Heatwave.',
  'picker_label': '[S2] 🌿 Carbon Capture Boost (+5 ENV Sekali Pakai | 🪙4)'},
 {'id': 'S3',
  'code': 'S3',
  'name': 'Traffic Override',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚦',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 5,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 5, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +5.',
  'effect_summary': '+5 M (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Mobility +5 atau mengatasi Traffic Congestion.',
  'picker_label': '[S3] 🚦 Traffic Override (+5 M Sekali Pakai | 🪙4)'},
 {'id': 'S4',
  'code': 'S4',
  'name': 'Public Health Campaign',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🏥',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': 'Quality of Life +5.',
  'effect_summary': '+5 QoL (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Quality of Life +5 atau mengatasi Public Health Emergency.',
  'picker_label': '[S4] 🏥 Public Health Campaign (+5 QoL Sekali Pakai | 🪙3)'},
 {'id': 'S5',
  'code': 'S5',
  'name': 'Cyber Shield',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🛡️',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu efek negatif Skill atau Event Card yang menargetkan kota sendiri.',
  'effect_summary': 'Proteksi Efek Negatif',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Membatalkan 1 efek negatif Skill atau Event Card pada kota sendiri atau mengatasi Cyber '
                 'Attack.',
  'picker_label': '[S5] 🛡️ Cyber Shield (Batalkan Efek Negatif | 🪙4)'}]

TECH_CARDS_UNIQUE: List[Dict[str, Any]] = PERMANENT_TECH_CARDS + CONSUMABLE_SKILL_CARDS

TECH_CARDS_40: List[Dict[str, Any]] = [{'id': 'TC01',
  'code': 'T1',
  'name': 'Solar Engineering',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '☀️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 2,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 2, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Energy +2',
  'effect_summary': '+2 E (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Energy +2 serta menjadi syarat pembangunan proyek bertanda T1 dan solusi krisis '
                 'energi.',
  'picker_label': '[TC01] ☀️ T1 - Solar Engineering (Salinan #1/4 · +2 E (Pasif))',
  'card_no': 1,
  'copy_no': 1},
 {'id': 'TC02',
  'code': 'T1',
  'name': 'Solar Engineering',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '☀️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 2,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 2, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Energy +2',
  'effect_summary': '+2 E (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Energy +2 serta menjadi syarat pembangunan proyek bertanda T1 dan solusi krisis '
                 'energi.',
  'picker_label': '[TC02] ☀️ T1 - Solar Engineering (Salinan #2/4 · +2 E (Pasif))',
  'card_no': 2,
  'copy_no': 2},
 {'id': 'TC03',
  'code': 'T1',
  'name': 'Solar Engineering',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '☀️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 2,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 2, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Energy +2',
  'effect_summary': '+2 E (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Energy +2 serta menjadi syarat pembangunan proyek bertanda T1 dan solusi krisis '
                 'energi.',
  'picker_label': '[TC03] ☀️ T1 - Solar Engineering (Salinan #3/4 · +2 E (Pasif))',
  'card_no': 3,
  'copy_no': 3},
 {'id': 'TC04',
  'code': 'T1',
  'name': 'Solar Engineering',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '☀️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 2,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 2, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Energy +2',
  'effect_summary': '+2 E (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Energy +2 serta menjadi syarat pembangunan proyek bertanda T1 dan solusi krisis '
                 'energi.',
  'picker_label': '[TC04] ☀️ T1 - Solar Engineering (Salinan #4/4 · +2 E (Pasif))',
  'card_no': 4,
  'copy_no': 4},
 {'id': 'TC05',
  'code': 'T2',
  'name': 'AI Urban System',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🤖',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 1,
  'E': 0,
  'ENV': 0,
  'QoL': 1,
  'effects': {'M': 1, 'E': 0, 'ENV': 0, 'QoL': 1},
  'effect_str': 'Mobility +1, QoL +1',
  'effect_summary': '+1 M, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +1, QoL +1 serta menjadi syarat pembangunan proyek pintar bertanda T2.',
  'picker_label': '[TC05] 🤖 T2 - AI Urban System (Salinan #1/4 · +1 M, +1 QoL (Pasif))',
  'card_no': 5,
  'copy_no': 1},
 {'id': 'TC06',
  'code': 'T2',
  'name': 'AI Urban System',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🤖',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 1,
  'E': 0,
  'ENV': 0,
  'QoL': 1,
  'effects': {'M': 1, 'E': 0, 'ENV': 0, 'QoL': 1},
  'effect_str': 'Mobility +1, QoL +1',
  'effect_summary': '+1 M, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +1, QoL +1 serta menjadi syarat pembangunan proyek pintar bertanda T2.',
  'picker_label': '[TC06] 🤖 T2 - AI Urban System (Salinan #2/4 · +1 M, +1 QoL (Pasif))',
  'card_no': 6,
  'copy_no': 2},
 {'id': 'TC07',
  'code': 'T2',
  'name': 'AI Urban System',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🤖',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 1,
  'E': 0,
  'ENV': 0,
  'QoL': 1,
  'effects': {'M': 1, 'E': 0, 'ENV': 0, 'QoL': 1},
  'effect_str': 'Mobility +1, QoL +1',
  'effect_summary': '+1 M, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +1, QoL +1 serta menjadi syarat pembangunan proyek pintar bertanda T2.',
  'picker_label': '[TC07] 🤖 T2 - AI Urban System (Salinan #3/4 · +1 M, +1 QoL (Pasif))',
  'card_no': 7,
  'copy_no': 3},
 {'id': 'TC08',
  'code': 'T2',
  'name': 'AI Urban System',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🤖',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 1,
  'E': 0,
  'ENV': 0,
  'QoL': 1,
  'effects': {'M': 1, 'E': 0, 'ENV': 0, 'QoL': 1},
  'effect_str': 'Mobility +1, QoL +1',
  'effect_summary': '+1 M, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +1, QoL +1 serta menjadi syarat pembangunan proyek pintar bertanda T2.',
  'picker_label': '[TC08] 🤖 T2 - AI Urban System (Salinan #4/4 · +1 M, +1 QoL (Pasif))',
  'card_no': 8,
  'copy_no': 4},
 {'id': 'TC09',
  'code': 'T3',
  'name': 'Circular Materials',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '♻️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 0},
  'effect_str': 'Environment +2',
  'effect_summary': '+2 ENV (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +2 serta menjadi syarat pembangunan proyek ekologis bertanda T3.',
  'picker_label': '[TC09] ♻️ T3 - Circular Materials (Salinan #1/4 · +2 ENV (Pasif))',
  'card_no': 9,
  'copy_no': 1},
 {'id': 'TC10',
  'code': 'T3',
  'name': 'Circular Materials',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '♻️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 0},
  'effect_str': 'Environment +2',
  'effect_summary': '+2 ENV (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +2 serta menjadi syarat pembangunan proyek ekologis bertanda T3.',
  'picker_label': '[TC10] ♻️ T3 - Circular Materials (Salinan #2/4 · +2 ENV (Pasif))',
  'card_no': 10,
  'copy_no': 2},
 {'id': 'TC11',
  'code': 'T3',
  'name': 'Circular Materials',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '♻️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 0},
  'effect_str': 'Environment +2',
  'effect_summary': '+2 ENV (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +2 serta menjadi syarat pembangunan proyek ekologis bertanda T3.',
  'picker_label': '[TC11] ♻️ T3 - Circular Materials (Salinan #3/4 · +2 ENV (Pasif))',
  'card_no': 11,
  'copy_no': 3},
 {'id': 'TC12',
  'code': 'T3',
  'name': 'Circular Materials',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '♻️',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 0},
  'effect_str': 'Environment +2',
  'effect_summary': '+2 ENV (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +2 serta menjadi syarat pembangunan proyek ekologis bertanda T3.',
  'picker_label': '[TC12] ♻️ T3 - Circular Materials (Salinan #4/4 · +2 ENV (Pasif))',
  'card_no': 12,
  'copy_no': 4},
 {'id': 'TC13',
  'code': 'T4',
  'name': 'Electric Mobility',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🚝',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 2,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 2, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +2',
  'effect_summary': '+2 M (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +2, melindungi dari Global Fuel Crisis (R2), dan syarat proyek transit '
                 'T4.',
  'picker_label': '[TC13] 🚝 T4 - Electric Mobility (Salinan #1/4 · +2 M (Pasif))',
  'card_no': 13,
  'copy_no': 1},
 {'id': 'TC14',
  'code': 'T4',
  'name': 'Electric Mobility',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🚝',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 2,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 2, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +2',
  'effect_summary': '+2 M (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +2, melindungi dari Global Fuel Crisis (R2), dan syarat proyek transit '
                 'T4.',
  'picker_label': '[TC14] 🚝 T4 - Electric Mobility (Salinan #2/4 · +2 M (Pasif))',
  'card_no': 14,
  'copy_no': 2},
 {'id': 'TC15',
  'code': 'T4',
  'name': 'Electric Mobility',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🚝',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 2,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 2, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +2',
  'effect_summary': '+2 M (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +2, melindungi dari Global Fuel Crisis (R2), dan syarat proyek transit '
                 'T4.',
  'picker_label': '[TC15] 🚝 T4 - Electric Mobility (Salinan #3/4 · +2 M (Pasif))',
  'card_no': 15,
  'copy_no': 3},
 {'id': 'TC16',
  'code': 'T4',
  'name': 'Electric Mobility',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '🚝',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 2,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 2, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +2',
  'effect_summary': '+2 M (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Mobility +2, melindungi dari Global Fuel Crisis (R2), dan syarat proyek transit '
                 'T4.',
  'picker_label': '[TC16] 🚝 T4 - Electric Mobility (Salinan #4/4 · +2 M (Pasif))',
  'card_no': 16,
  'copy_no': 4},
 {'id': 'TC17',
  'code': 'T5',
  'name': 'Water Purification',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '💧',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 1,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 1},
  'effect_str': 'Environment +1, QoL +1',
  'effect_summary': '+1 ENV, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +1, QoL +1 serta syarat proyek air bersih dan ketahanan banjir T5.',
  'picker_label': '[TC17] 💧 T5 - Water Purification (Salinan #1/4 · +1 ENV, +1 QoL (Pasif))',
  'card_no': 17,
  'copy_no': 1},
 {'id': 'TC18',
  'code': 'T5',
  'name': 'Water Purification',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '💧',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 1,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 1},
  'effect_str': 'Environment +1, QoL +1',
  'effect_summary': '+1 ENV, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +1, QoL +1 serta syarat proyek air bersih dan ketahanan banjir T5.',
  'picker_label': '[TC18] 💧 T5 - Water Purification (Salinan #2/4 · +1 ENV, +1 QoL (Pasif))',
  'card_no': 18,
  'copy_no': 2},
 {'id': 'TC19',
  'code': 'T5',
  'name': 'Water Purification',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '💧',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 1,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 1},
  'effect_str': 'Environment +1, QoL +1',
  'effect_summary': '+1 ENV, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +1, QoL +1 serta syarat proyek air bersih dan ketahanan banjir T5.',
  'picker_label': '[TC19] 💧 T5 - Water Purification (Salinan #3/4 · +1 ENV, +1 QoL (Pasif))',
  'card_no': 19,
  'copy_no': 3},
 {'id': 'TC20',
  'code': 'T5',
  'name': 'Water Purification',
  'category': 'Tech',
  'sub_type': 'Permanent Technology',
  'district': 'City Center',
  'emoji': '💧',
  'cost': 5,
  'copies': 4,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 1,
  'QoL': 1,
  'effects': {'M': 0, 'E': 0, 'ENV': 1, 'QoL': 1},
  'effect_str': 'Environment +1, QoL +1',
  'effect_summary': '+1 ENV, +1 QoL (Pasif)',
  'description': 'Permanent Technology (Beli di City Center: 5 Koin + 1 AP, tersedia 4 salinan). Efek pasif '
                 'permanen Environment +1, QoL +1 serta syarat proyek air bersih dan ketahanan banjir T5.',
  'picker_label': '[TC20] 💧 T5 - Water Purification (Salinan #4/4 · +1 ENV, +1 QoL (Pasif))',
  'card_no': 20,
  'copy_no': 4},
 {'id': 'TC21',
  'code': 'S1',
  'name': 'Emergency Response',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚑',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu Problem Card yang menyebabkan penalti.',
  'effect_summary': 'Batalkan 1 Problem Card',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk membatalkan 1 Problem Card yang menyebabkan penalti.',
  'picker_label': '[TC21] 🚑 S1 - Emergency Response (Salinan #1/4 · Batalkan 1 Problem Card)',
  'card_no': 21,
  'copy_no': 1},
 {'id': 'TC22',
  'code': 'S1',
  'name': 'Emergency Response',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚑',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu Problem Card yang menyebabkan penalti.',
  'effect_summary': 'Batalkan 1 Problem Card',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk membatalkan 1 Problem Card yang menyebabkan penalti.',
  'picker_label': '[TC22] 🚑 S1 - Emergency Response (Salinan #2/4 · Batalkan 1 Problem Card)',
  'card_no': 22,
  'copy_no': 2},
 {'id': 'TC23',
  'code': 'S1',
  'name': 'Emergency Response',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚑',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu Problem Card yang menyebabkan penalti.',
  'effect_summary': 'Batalkan 1 Problem Card',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk membatalkan 1 Problem Card yang menyebabkan penalti.',
  'picker_label': '[TC23] 🚑 S1 - Emergency Response (Salinan #3/4 · Batalkan 1 Problem Card)',
  'card_no': 23,
  'copy_no': 3},
 {'id': 'TC24',
  'code': 'S1',
  'name': 'Emergency Response',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚑',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu Problem Card yang menyebabkan penalti.',
  'effect_summary': 'Batalkan 1 Problem Card',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk membatalkan 1 Problem Card yang menyebabkan penalti.',
  'picker_label': '[TC24] 🚑 S1 - Emergency Response (Salinan #4/4 · Batalkan 1 Problem Card)',
  'card_no': 24,
  'copy_no': 4},
 {'id': 'TC25',
  'code': 'S2',
  'name': 'Carbon Capture Boost',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🌿',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 0},
  'effect_str': 'Environment +5.',
  'effect_summary': '+5 ENV (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Environment +5 atau mengatasi Severe Air Pollution / Extreme '
                 'Heatwave.',
  'picker_label': '[TC25] 🌿 S2 - Carbon Capture Boost (Salinan #1/4 · +5 ENV (Sekali Pakai))',
  'card_no': 25,
  'copy_no': 1},
 {'id': 'TC26',
  'code': 'S2',
  'name': 'Carbon Capture Boost',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🌿',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 0},
  'effect_str': 'Environment +5.',
  'effect_summary': '+5 ENV (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Environment +5 atau mengatasi Severe Air Pollution / Extreme '
                 'Heatwave.',
  'picker_label': '[TC26] 🌿 S2 - Carbon Capture Boost (Salinan #2/4 · +5 ENV (Sekali Pakai))',
  'card_no': 26,
  'copy_no': 2},
 {'id': 'TC27',
  'code': 'S2',
  'name': 'Carbon Capture Boost',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🌿',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 0},
  'effect_str': 'Environment +5.',
  'effect_summary': '+5 ENV (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Environment +5 atau mengatasi Severe Air Pollution / Extreme '
                 'Heatwave.',
  'picker_label': '[TC27] 🌿 S2 - Carbon Capture Boost (Salinan #3/4 · +5 ENV (Sekali Pakai))',
  'card_no': 27,
  'copy_no': 3},
 {'id': 'TC28',
  'code': 'S2',
  'name': 'Carbon Capture Boost',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🌿',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 5,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 5, 'QoL': 0},
  'effect_str': 'Environment +5.',
  'effect_summary': '+5 ENV (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Environment +5 atau mengatasi Severe Air Pollution / Extreme '
                 'Heatwave.',
  'picker_label': '[TC28] 🌿 S2 - Carbon Capture Boost (Salinan #4/4 · +5 ENV (Sekali Pakai))',
  'card_no': 28,
  'copy_no': 4},
 {'id': 'TC29',
  'code': 'S3',
  'name': 'Traffic Override',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚦',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 5,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 5, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +5.',
  'effect_summary': '+5 M (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Mobility +5 atau mengatasi Traffic Congestion.',
  'picker_label': '[TC29] 🚦 S3 - Traffic Override (Salinan #1/4 · +5 M (Sekali Pakai))',
  'card_no': 29,
  'copy_no': 1},
 {'id': 'TC30',
  'code': 'S3',
  'name': 'Traffic Override',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚦',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 5,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 5, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +5.',
  'effect_summary': '+5 M (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Mobility +5 atau mengatasi Traffic Congestion.',
  'picker_label': '[TC30] 🚦 S3 - Traffic Override (Salinan #2/4 · +5 M (Sekali Pakai))',
  'card_no': 30,
  'copy_no': 2},
 {'id': 'TC31',
  'code': 'S3',
  'name': 'Traffic Override',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚦',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 5,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 5, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +5.',
  'effect_summary': '+5 M (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Mobility +5 atau mengatasi Traffic Congestion.',
  'picker_label': '[TC31] 🚦 S3 - Traffic Override (Salinan #3/4 · +5 M (Sekali Pakai))',
  'card_no': 31,
  'copy_no': 3},
 {'id': 'TC32',
  'code': 'S3',
  'name': 'Traffic Override',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🚦',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 5,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 5, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Mobility +5.',
  'effect_summary': '+5 M (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Mobility +5 atau mengatasi Traffic Congestion.',
  'picker_label': '[TC32] 🚦 S3 - Traffic Override (Salinan #4/4 · +5 M (Sekali Pakai))',
  'card_no': 32,
  'copy_no': 4},
 {'id': 'TC33',
  'code': 'S4',
  'name': 'Public Health Campaign',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🏥',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': 'Quality of Life +5.',
  'effect_summary': '+5 QoL (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Quality of Life +5 atau mengatasi Public Health Emergency.',
  'picker_label': '[TC33] 🏥 S4 - Public Health Campaign (Salinan #1/4 · +5 QoL (Sekali Pakai))',
  'card_no': 33,
  'copy_no': 1},
 {'id': 'TC34',
  'code': 'S4',
  'name': 'Public Health Campaign',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🏥',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': 'Quality of Life +5.',
  'effect_summary': '+5 QoL (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Quality of Life +5 atau mengatasi Public Health Emergency.',
  'picker_label': '[TC34] 🏥 S4 - Public Health Campaign (Salinan #2/4 · +5 QoL (Sekali Pakai))',
  'card_no': 34,
  'copy_no': 2},
 {'id': 'TC35',
  'code': 'S4',
  'name': 'Public Health Campaign',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🏥',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': 'Quality of Life +5.',
  'effect_summary': '+5 QoL (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Quality of Life +5 atau mengatasi Public Health Emergency.',
  'picker_label': '[TC35] 🏥 S4 - Public Health Campaign (Salinan #3/4 · +5 QoL (Sekali Pakai))',
  'card_no': 35,
  'copy_no': 3},
 {'id': 'TC36',
  'code': 'S4',
  'name': 'Public Health Campaign',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🏥',
  'cost': 3,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 5},
  'effect_str': 'Quality of Life +5.',
  'effect_summary': '+5 QoL (Sekali Pakai)',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 3 Koin + 1 AP, tersedia 4 salinan). '
                 'Gunakan 2 AP untuk memperoleh Quality of Life +5 atau mengatasi Public Health Emergency.',
  'picker_label': '[TC36] 🏥 S4 - Public Health Campaign (Salinan #4/4 · +5 QoL (Sekali Pakai))',
  'card_no': 36,
  'copy_no': 4},
 {'id': 'TC37',
  'code': 'S5',
  'name': 'Cyber Shield',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🛡️',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu efek negatif Skill atau Event Card yang menargetkan kota sendiri.',
  'effect_summary': 'Proteksi Efek Negatif',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Membatalkan 1 efek negatif Skill atau Event Card pada kota sendiri atau mengatasi Cyber '
                 'Attack.',
  'picker_label': '[TC37] 🛡️ S5 - Cyber Shield (Salinan #1/4 · Proteksi Efek Negatif)',
  'card_no': 37,
  'copy_no': 1},
 {'id': 'TC38',
  'code': 'S5',
  'name': 'Cyber Shield',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🛡️',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu efek negatif Skill atau Event Card yang menargetkan kota sendiri.',
  'effect_summary': 'Proteksi Efek Negatif',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Membatalkan 1 efek negatif Skill atau Event Card pada kota sendiri atau mengatasi Cyber '
                 'Attack.',
  'picker_label': '[TC38] 🛡️ S5 - Cyber Shield (Salinan #2/4 · Proteksi Efek Negatif)',
  'card_no': 38,
  'copy_no': 2},
 {'id': 'TC39',
  'code': 'S5',
  'name': 'Cyber Shield',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🛡️',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu efek negatif Skill atau Event Card yang menargetkan kota sendiri.',
  'effect_summary': 'Proteksi Efek Negatif',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Membatalkan 1 efek negatif Skill atau Event Card pada kota sendiri atau mengatasi Cyber '
                 'Attack.',
  'picker_label': '[TC39] 🛡️ S5 - Cyber Shield (Salinan #3/4 · Proteksi Efek Negatif)',
  'card_no': 39,
  'copy_no': 3},
 {'id': 'TC40',
  'code': 'S5',
  'name': 'Cyber Shield',
  'category': 'Tech',
  'sub_type': 'Consumable Skill',
  'district': 'City Center',
  'emoji': '🛡️',
  'cost': 4,
  'copies': 4,
  'tech_req': 'Aktifkan: 2 AP',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect_str': 'Batalkan satu efek negatif Skill atau Event Card yang menargetkan kota sendiri.',
  'effect_summary': 'Proteksi Efek Negatif',
  'description': 'Consumable Skill sekali pakai (Beli di City Center: 4 Koin + 1 AP, tersedia 4 salinan). '
                 'Membatalkan 1 efek negatif Skill atau Event Card pada kota sendiri atau mengatasi Cyber '
                 'Attack.',
  'picker_label': '[TC40] 🛡️ S5 - Cyber Shield (Salinan #4/4 · Proteksi Efek Negatif)',
  'card_no': 40,
  'copy_no': 4}]

PROBLEM_CARDS: List[Dict[str, Any]] = [{'id': 'PR01',
  'no': 1,
  'name': 'Severe Air Pollution',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T3 atau S2',
  'tech_req': 'T3 atau S2',
  'M': 0,
  'E': 0,
  'ENV': -6,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': -6, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'ENV -6',
  'effect_str': 'ENV -6',
  'effect_summary': '-6 ENV',
  'description': 'Problem Card #1 (PR01). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T3 atau S2 (2 '
                 'AP). Penalti jika gagal: ENV -6.',
  'picker_label': '⚠️ [PR01] Severe Air Pollution (Penalti: ENV -6)'},
 {'id': 'PR02',
  'no': 2,
  'name': 'Traffic Congestion',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T2 atau S3',
  'tech_req': 'T2 atau S3',
  'M': -6,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': -6, 'E': 0, 'ENV': 0, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'M -6',
  'effect_str': 'M -6',
  'effect_summary': '-6 M',
  'description': 'Problem Card #2 (PR02). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T2 atau S3 (2 '
                 'AP). Penalti jika gagal: M -6.',
  'picker_label': '⚠️ [PR02] Traffic Congestion (Penalti: M -6)'},
 {'id': 'PR03',
  'no': 3,
  'name': 'Energy Crisis',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': 'T1',
  'tech_req': 'T1',
  'M': 0,
  'E': -7,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': -7, 'ENV': 0, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'E -7',
  'effect_str': 'E -7',
  'effect_summary': '-7 E',
  'description': 'Problem Card #3 (PR03). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: T1 (2 AP). '
                 'Penalti jika gagal: E -7.',
  'picker_label': '⚠️ [PR03] Energy Crisis (Penalti: E -7)'},
 {'id': 'PR04',
  'no': 4,
  'name': 'Water Shortage',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T5',
  'tech_req': 'T5',
  'M': 0,
  'E': 0,
  'ENV': -4,
  'QoL': -3,
  'effects': {'M': 0, 'E': 0, 'ENV': -4, 'QoL': -3},
  'coin_loss': 0,
  'pen_str': 'ENV -4, QoL -3',
  'effect_str': 'ENV -4, QoL -3',
  'effect_summary': '-4 ENV, -3 QoL',
  'description': 'Problem Card #4 (PR04). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T5 (2 AP). '
                 'Penalti jika gagal: ENV -4, QoL -3.',
  'picker_label': '⚠️ [PR04] Water Shortage (Penalti: ENV -4, QoL -3)'},
 {'id': 'PR05',
  'no': 5,
  'name': 'Flood Disaster',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': 'T5',
  'tech_req': 'T5',
  'M': -3,
  'E': 0,
  'ENV': 0,
  'QoL': -5,
  'effects': {'M': -3, 'E': 0, 'ENV': 0, 'QoL': -5},
  'coin_loss': 0,
  'pen_str': 'M -3, QoL -5',
  'effect_str': 'M -3, QoL -5',
  'effect_summary': '-3 M, -5 QoL',
  'description': 'Problem Card #5 (PR05). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: T5 (2 AP). '
                 'Penalti jika gagal: M -3, QoL -5.',
  'picker_label': '⚠️ [PR05] Flood Disaster (Penalti: M -3, QoL -5)'},
 {'id': 'PR06',
  'no': 6,
  'name': 'Public Health Emergency',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'S1 atau S4',
  'tech_req': 'S1 atau S4',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': -7,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': -7},
  'coin_loss': 0,
  'pen_str': 'QoL -7',
  'effect_str': 'QoL -7',
  'effect_summary': '-7 QoL',
  'description': 'Problem Card #6 (PR06). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: S1 atau S4 (2 '
                 'AP). Penalti jika gagal: QoL -7.',
  'picker_label': '⚠️ [PR06] Public Health Emergency (Penalti: QoL -7)'},
 {'id': 'PR07',
  'no': 7,
  'name': 'Industrial Waste Leakage',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': 'T3 atau T5',
  'tech_req': 'T3 atau T5',
  'M': 0,
  'E': 0,
  'ENV': -7,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': -7, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'ENV -7',
  'effect_str': 'ENV -7',
  'effect_summary': '-7 ENV',
  'description': 'Problem Card #7 (PR07). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: T3 atau T5 (2 '
                 'AP). Penalti jika gagal: ENV -7.',
  'picker_label': '⚠️ [PR07] Industrial Waste Leakage (Penalti: ENV -7)'},
 {'id': 'PR08',
  'no': 8,
  'name': 'Power Grid Failure',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': 'T1 + T2',
  'tech_req': 'T1 + T2',
  'M': 0,
  'E': -6,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': -6, 'ENV': 0, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'E -6',
  'effect_str': 'E -6',
  'effect_summary': '-6 E',
  'description': 'Problem Card #8 (PR08). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: T1 + T2 (2 AP). '
                 'Penalti jika gagal: E -6.',
  'picker_label': '⚠️ [PR08] Power Grid Failure (Penalti: E -6)'},
 {'id': 'PR09',
  'no': 9,
  'name': 'Public Transportation Strike',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T4',
  'tech_req': 'T4',
  'M': -6,
  'E': 0,
  'ENV': 0,
  'QoL': -2,
  'effects': {'M': -6, 'E': 0, 'ENV': 0, 'QoL': -2},
  'coin_loss': 0,
  'pen_str': 'M -6, QoL -2',
  'effect_str': 'M -6, QoL -2',
  'effect_summary': '-6 M, -2 QoL',
  'description': 'Problem Card #9 (PR09). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T4 (2 AP). '
                 'Penalti jika gagal: M -6, QoL -2.',
  'picker_label': '⚠️ [PR09] Public Transportation Strike (Penalti: M -6, QoL -2)'},
 {'id': 'PR10',
  'no': 10,
  'name': 'Cyber Attack',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T2 atau S5',
  'tech_req': 'T2 atau S5',
  'M': 0,
  'E': -3,
  'ENV': 0,
  'QoL': -4,
  'effects': {'M': 0, 'E': -3, 'ENV': 0, 'QoL': -4},
  'coin_loss': 0,
  'pen_str': 'QoL -4, E -3',
  'effect_str': 'QoL -4, E -3',
  'effect_summary': '-3 E, -4 QoL',
  'description': 'Problem Card #10 (PR10). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T2 atau S5 (2 '
                 'AP). Penalti jika gagal: QoL -4, E -3.',
  'picker_label': '⚠️ [PR10] Cyber Attack (Penalti: QoL -4, E -3)'},
 {'id': 'PR11',
  'no': 11,
  'name': 'Extreme Heatwave',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': 'T1 + T3 atau S2',
  'tech_req': 'T1 + T3 atau S2',
  'M': 0,
  'E': 0,
  'ENV': -5,
  'QoL': -3,
  'effects': {'M': 0, 'E': 0, 'ENV': -5, 'QoL': -3},
  'coin_loss': 0,
  'pen_str': 'ENV -5, QoL -3',
  'effect_str': 'ENV -5, QoL -3',
  'effect_summary': '-5 ENV, -3 QoL',
  'description': 'Problem Card #11 (PR11). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: T1 + T3 atau S2 '
                 '(2 AP). Penalti jika gagal: ENV -5, QoL -3.',
  'picker_label': '⚠️ [PR11] Extreme Heatwave (Penalti: ENV -5, QoL -3)'},
 {'id': 'PR12',
  'no': 12,
  'name': 'Housing Crisis',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': '-',
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': -6,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': -6},
  'coin_loss': 0,
  'pen_str': 'QoL -6',
  'effect_str': 'QoL -6',
  'effect_summary': '-6 QoL',
  'description': 'Problem Card #12 (PR12). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: Wajib Bayar Koin '
                 '(2 AP). Penalti jika gagal: QoL -6.',
  'picker_label': '⚠️ [PR12] Housing Crisis (Penalti: QoL -6)'},
 {'id': 'PR13',
  'no': 13,
  'name': 'River Contamination',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T5',
  'tech_req': 'T5',
  'M': 0,
  'E': 0,
  'ENV': -6,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': -6, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'ENV -6',
  'effect_str': 'ENV -6',
  'effect_summary': '-6 ENV',
  'description': 'Problem Card #13 (PR13). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T5 (2 AP). '
                 'Penalti jika gagal: ENV -6.',
  'picker_label': '⚠️ [PR13] River Contamination (Penalti: ENV -6)'},
 {'id': 'PR14',
  'no': 14,
  'name': 'Economic Recession',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': '-',
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': -4,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': -4},
  'coin_loss': 2,
  'pen_str': 'QoL -4, kehilangan 2 koin',
  'effect_str': 'QoL -4, kehilangan 2 koin',
  'effect_summary': '-4 QoL, -2 🪙',
  'description': 'Problem Card #14 (PR14). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: Wajib Bayar Koin '
                 '(2 AP). Penalti jika gagal: QoL -4, kehilangan 2 koin.',
  'picker_label': '⚠️ [PR14] Economic Recession (Penalti: QoL -4, kehilangan 2 koin)'},
 {'id': 'PR15',
  'no': 15,
  'name': 'Food Supply Disruption',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T3',
  'tech_req': 'T3',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': -5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': -5},
  'coin_loss': 0,
  'pen_str': 'QoL -5',
  'effect_str': 'QoL -5',
  'effect_summary': '-5 QoL',
  'description': 'Problem Card #15 (PR15). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T3 (2 AP). '
                 'Penalti jika gagal: QoL -5.',
  'picker_label': '⚠️ [PR15] Food Supply Disruption (Penalti: QoL -5)'},
 {'id': 'PR16',
  'no': 16,
  'name': 'Infrastructure Collapse',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 6,
  'alt_req': 'T2 + T3',
  'tech_req': 'T2 + T3',
  'M': -4,
  'E': 0,
  'ENV': 0,
  'QoL': -4,
  'effects': {'M': -4, 'E': 0, 'ENV': 0, 'QoL': -4},
  'coin_loss': 0,
  'pen_str': 'M -4, QoL -4',
  'effect_str': 'M -4, QoL -4',
  'effect_summary': '-4 M, -4 QoL',
  'description': 'Problem Card #16 (PR16). Solusi Bayar: 6 Koin (1 AP) | Solusi Tech/Skill: T2 + T3 (2 AP). '
                 'Penalti jika gagal: M -4, QoL -4.',
  'picker_label': '⚠️ [PR16] Infrastructure Collapse (Penalti: M -4, QoL -4)'},
 {'id': 'PR17',
  'no': 17,
  'name': 'Renewable Energy Failure',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 5,
  'alt_req': 'T1',
  'tech_req': 'T1',
  'M': 0,
  'E': -6,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': -6, 'ENV': 0, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'E -6',
  'effect_str': 'E -6',
  'effect_summary': '-6 E',
  'description': 'Problem Card #17 (PR17). Solusi Bayar: 5 Koin (1 AP) | Solusi Tech/Skill: T1 (2 AP). '
                 'Penalti jika gagal: E -6.',
  'picker_label': '⚠️ [PR17] Renewable Energy Failure (Penalti: E -6)'},
 {'id': 'PR18',
  'no': 18,
  'name': 'Waste Management Crisis',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T3',
  'tech_req': 'T3',
  'M': 0,
  'E': 0,
  'ENV': -6,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': -6, 'QoL': 0},
  'coin_loss': 0,
  'pen_str': 'ENV -6',
  'effect_str': 'ENV -6',
  'effect_summary': '-6 ENV',
  'description': 'Problem Card #18 (PR18). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T3 (2 AP). '
                 'Penalti jika gagal: ENV -6.',
  'picker_label': '⚠️ [PR18] Waste Management Crisis (Penalti: ENV -6)'},
 {'id': 'PR19',
  'no': 19,
  'name': 'Urban Security Threat',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 4,
  'alt_req': 'T2 atau S1',
  'tech_req': 'T2 atau S1',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': -5,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': -5},
  'coin_loss': 0,
  'pen_str': 'QoL -5',
  'effect_str': 'QoL -5',
  'effect_summary': '-5 QoL',
  'description': 'Problem Card #19 (PR19). Solusi Bayar: 4 Koin (1 AP) | Solusi Tech/Skill: T2 atau S1 (2 '
                 'AP). Penalti jika gagal: QoL -5.',
  'picker_label': '⚠️ [PR19] Urban Security Threat (Penalti: QoL -5)'},
 {'id': 'PR20',
  'no': 20,
  'name': 'Climate Disaster',
  'category': 'Problem',
  'district': 'Urban Crisis',
  'emoji': '⚠️',
  'cost': 7,
  'alt_req': 'T1 + T3 + T5',
  'tech_req': 'T1 + T3 + T5',
  'M': -3,
  'E': 0,
  'ENV': -5,
  'QoL': -4,
  'effects': {'M': -3, 'E': 0, 'ENV': -5, 'QoL': -4},
  'coin_loss': 0,
  'pen_str': 'M -3, ENV -5, QoL -4',
  'effect_str': 'M -3, ENV -5, QoL -4',
  'effect_summary': '-3 M, -5 ENV, -4 QoL',
  'description': 'Problem Card #20 (PR20). Solusi Bayar: 7 Koin (1 AP) | Solusi Tech/Skill: T1 + T3 + T5 (2 '
                 'AP). Penalti jika gagal: M -3, ENV -5, QoL -4.',
  'picker_label': '⚠️ [PR20] Climate Disaster (Penalti: M -3, ENV -5, QoL -4)'}]

EVENT_CARDS: List[Dict[str, Any]] = [{'id': 'EV01',
  'round': 1,
  'name': 'Green Investment Program',
  'category': 'Event',
  'district': 'Round 1',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect': 'Seluruh pemain memperoleh 2 koin tambahan.',
  'effect_str': 'Seluruh pemain memperoleh 2 koin tambahan.',
  'effect_summary': '+2 🪙 Semua',
  'description': 'Global Event Round 1 (EV01): Seluruh pemain memperoleh 2 koin tambahan.',
  'picker_label': '[EV01] 🌐 Round 1: Green Investment Program (+2 🪙 Semua)'},
 {'id': 'EV02',
  'round': 2,
  'name': 'Global Fuel Crisis',
  'category': 'Event',
  'district': 'Round 2',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': -2,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': -2, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect': 'Seluruh pemain kehilangan Mobility -2, kecuali memiliki T4.',
  'effect_str': 'Seluruh pemain kehilangan Mobility -2, kecuali memiliki T4.',
  'effect_summary': '-2 M',
  'description': 'Global Event Round 2 (EV02): Seluruh pemain kehilangan Mobility -2, kecuali memiliki T4.',
  'picker_label': '[EV02] 🌐 Round 2: Global Fuel Crisis (-2 M)'},
 {'id': 'EV03',
  'round': 3,
  'name': 'Renewable Energy Subsidy',
  'category': 'Event',
  'district': 'Round 3',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect': 'Pembelian Project Card di Energy District mendapat diskon 2 koin.',
  'effect_str': 'Pembelian Project Card di Energy District mendapat diskon 2 koin.',
  'effect_summary': 'Diskon -2 🪙',
  'description': 'Global Event Round 3 (EV03): Pembelian Project Card di Energy District mendapat diskon 2 '
                 'koin.',
  'picker_label': '[EV03] 🌐 Round 3: Renewable Energy Subsidy (Diskon -2 🪙)'},
 {'id': 'EV04',
  'round': 4,
  'name': 'Urban Green Movement',
  'category': 'Event',
  'district': 'Round 4',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 3,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 3, 'QoL': 0},
  'effect': 'Pemain yang memiliki minimal satu Project Card di Green Park memperoleh Environment +3.',
  'effect_str': 'Pemain yang memiliki minimal satu Project Card di Green Park memperoleh Environment +3.',
  'effect_summary': '+3 ENV',
  'description': 'Global Event Round 4 (EV04): Pemain yang memiliki minimal satu Project Card di Green Park '
                 'memperoleh Environment +3.',
  'picker_label': '[EV04] 🌐 Round 4: Urban Green Movement (+3 ENV)'},
 {'id': 'EV05',
  'round': 5,
  'name': 'Smart City Innovation Week',
  'category': 'Event',
  'district': 'Round 5',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect': 'Pembelian Tech Card mendapat diskon 2 koin.',
  'effect_str': 'Pembelian Tech Card mendapat diskon 2 koin.',
  'effect_summary': 'Diskon -2 🪙',
  'description': 'Global Event Round 5 (EV05): Pembelian Tech Card mendapat diskon 2 koin.',
  'picker_label': '[EV05] 🌐 Round 5: Smart City Innovation Week (Diskon -2 🪙)'},
 {'id': 'EV06',
  'round': 6,
  'name': 'Industrial Pollution Regulation',
  'category': 'Event',
  'district': 'Round 6',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': -2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': -2, 'QoL': 0},
  'effect': 'Pemain yang memiliki minimal dua Project Card di Industrial kehilangan Environment -2, kecuali '
            'memiliki T3.',
  'effect_str': 'Pemain yang memiliki minimal dua Project Card di Industrial kehilangan Environment -2, '
                'kecuali memiliki T3.',
  'effect_summary': '-2 ENV',
  'description': 'Global Event Round 6 (EV06): Pemain yang memiliki minimal dua Project Card di Industrial '
                 'kehilangan Environment -2, kecuali memiliki T3.',
  'picker_label': '[EV06] 🌐 Round 6: Industrial Pollution Regulation (-2 ENV)'},
 {'id': 'EV07',
  'round': 7,
  'name': 'Public Transportation Campaign',
  'category': 'Event',
  'district': 'Round 7',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 3,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 3, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect': 'Pemain yang memiliki minimal satu Project Card di Transportation memperoleh Mobility +3.',
  'effect_str': 'Pemain yang memiliki minimal satu Project Card di Transportation memperoleh Mobility +3.',
  'effect_summary': '+3 M',
  'description': 'Global Event Round 7 (EV07): Pemain yang memiliki minimal satu Project Card di '
                 'Transportation memperoleh Mobility +3.',
  'picker_label': '[EV07] 🌐 Round 7: Public Transportation Campaign (+3 M)'},
 {'id': 'EV08',
  'round': 8,
  'name': 'Water Conservation Month',
  'category': 'Event',
  'district': 'Round 8',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 1,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 1},
  'effect': 'Pemain yang memiliki Project Card di Water memperoleh Environment +2 dan QoL +1.',
  'effect_str': 'Pemain yang memiliki Project Card di Water memperoleh Environment +2 dan QoL +1.',
  'effect_summary': '+2 ENV, +1 QoL',
  'description': 'Global Event Round 8 (EV08): Pemain yang memiliki Project Card di Water memperoleh '
                 'Environment +2 dan QoL +1.',
  'picker_label': '[EV08] 🌐 Round 8: Water Conservation Month (+2 ENV, +1 QoL)'},
 {'id': 'EV09',
  'round': 9,
  'name': 'Economic Boom',
  'category': 'Event',
  'district': 'Round 9',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 0},
  'effect': 'Seluruh pemain memperoleh 3 koin tambahan.',
  'effect_str': 'Seluruh pemain memperoleh 3 koin tambahan.',
  'effect_summary': '+3 🪙 Semua',
  'description': 'Global Event Round 9 (EV09): Seluruh pemain memperoleh 3 koin tambahan.',
  'picker_label': '[EV09] 🌐 Round 9: Economic Boom (+3 🪙 Semua)'},
 {'id': 'EV10',
  'round': 10,
  'name': 'Extreme Weather Alert',
  'category': 'Event',
  'district': 'Round 10',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': -2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': -2, 'QoL': 0},
  'effect': 'Seluruh pemain kehilangan Environment -2, kecuali memiliki T3 atau T5.',
  'effect_str': 'Seluruh pemain kehilangan Environment -2, kecuali memiliki T3 atau T5.',
  'effect_summary': '-2 ENV',
  'description': 'Global Event Round 10 (EV10): Seluruh pemain kehilangan Environment -2, kecuali memiliki '
                 'T3 atau T5.',
  'picker_label': '[EV10] 🌐 Round 10: Extreme Weather Alert (-2 ENV)'},
 {'id': 'EV11',
  'round': 11,
  'name': 'Digital Transformation',
  'category': 'Event',
  'district': 'Round 11',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 0,
  'QoL': 3,
  'effects': {'M': 0, 'E': 0, 'ENV': 0, 'QoL': 3},
  'effect': 'Pemain yang memiliki T2 memperoleh QoL +3.',
  'effect_str': 'Pemain yang memiliki T2 memperoleh QoL +3.',
  'effect_summary': '+3 QoL',
  'description': 'Global Event Round 11 (EV11): Pemain yang memiliki T2 memperoleh QoL +3.',
  'picker_label': '[EV11] 🌐 Round 11: Digital Transformation (+3 QoL)'},
 {'id': 'EV12',
  'round': 12,
  'name': 'Clean Energy Revolution',
  'category': 'Event',
  'district': 'Round 12',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 3,
  'ENV': 0,
  'QoL': 0,
  'effects': {'M': 0, 'E': 3, 'ENV': 0, 'QoL': 0},
  'effect': 'Pemain yang memiliki T1 memperoleh Energy +3.',
  'effect_str': 'Pemain yang memiliki T1 memperoleh Energy +3.',
  'effect_summary': '+3 E',
  'description': 'Global Event Round 12 (EV12): Pemain yang memiliki T1 memperoleh Energy +3.',
  'picker_label': '[EV12] 🌐 Round 12: Clean Energy Revolution (+3 E)'},
 {'id': 'EV13',
  'round': 13,
  'name': 'Sustainable Future Festival',
  'category': 'Event',
  'district': 'Round 13',
  'emoji': '🌐',
  'cost': 0,
  'tech_req': '-',
  'M': 0,
  'E': 0,
  'ENV': 2,
  'QoL': 0,
  'effects': {'M': 0, 'E': 0, 'ENV': 2, 'QoL': 0},
  'effect': 'Setiap pemain memperoleh 2 koin dan Environment +2.',
  'effect_str': 'Setiap pemain memperoleh 2 koin dan Environment +2.',
  'effect_summary': '+2 🪙, +2 ENV',
  'description': 'Global Event Round 13 (EV13): Setiap pemain memperoleh 2 koin dan Environment +2.',
  'picker_label': '[EV13] 🌐 Round 13: Sustainable Future Festival (+2 🪙, +2 ENV)'}]

RULEBOOK_SECTIONS: List[Dict[str, Any]] = [{'id': 'BAB_I',
  'title': 'I. Gambaran Umum Permainan & 4 Aspek Kota',
  'keywords': ['tujuan',
               'gambaran',
               'aspek',
               'mobility',
               'energy',
               'environment',
               'quality of life',
               'qol',
               'env',
               'skor awal',
               '50',
               '100',
               'district',
               'wilayah',
               'board'],
  'content': 'EcoNova: Sustainable City Builder adalah board game strategi pembangunan kota untuk 4 pemain '
             'selama 13 round.\n'
             '• Tujuan: Memperoleh Average Score tertinggi dari 4 aspek kota: Mobility (M), Energy (E), '
             'Environment (ENV), dan Quality of Life (QoL).\n'
             '• Nilai Awal: Setiap pemain memulai di City Center dengan 5 Koin dan skor 50 pada '
             'masing-masing aspek (rentang skor resmi dikunci 0–100).\n'
             '• 8 District + City Center: Residential, Green Park, Industrial, Transportation, Public '
             'Services, Commercial, Energy, Water, serta City Center di tengah.'},
 {'id': 'BAB_II',
  'title': 'II. Komponen & Persiapan (Setup Awal)',
  'keywords': ['komponen',
               'setup',
               'persiapan',
               'jumlah kartu',
               '120',
               '40',
               '20',
               '13',
               'pasar terbuka',
               'market',
               'koin awal'],
  'content': 'Total Kartu: 120 Project Card (15 kartu per 8 district), 40 Tech Card (20 Permanent Technology '
             'T1–T5 + 20 Consumable Skill S1–S5, masing-masing 4 salinan), 20 Problem Card, dan 13 Event '
             'Card.\n'
             '• Setup: Seluruh bidak mulai di City Center dengan 5 koin dan skor M=50, E=50, ENV=50, '
             'QoL=50.\n'
             '• Pasar Terbuka: Buka 3 Project Card pada setiap district dan 4 Tech Card di City Center.'},
 {'id': 'BAB_III',
  'title': 'III. Alur Permainan, Action Points (3 AP), & Movement',
  'keywords': ['alur',
               'fase',
               'round',
               'ap',
               'action point',
               '3 ap',
               'move',
               'pindah',
               'movement',
               'city center',
               '3 koin',
               'pre-action',
               'start round',
               'end round'],
  'content': 'Setiap Round terdiri dari 4 Fase:\n'
             '1. Start Round: Buka 1 Event Card (efek berlaku sepanjang round).\n'
             '2. Pre-Action: Setiap pemain menerima +2 koin dan mengambil 1 Problem Card.\n'
             '3. Action Phase: Setiap pemain memiliki 3 Action Points (AP) untuk kombinasi aksi:\n'
             '   - Move a Tile (1 AP): Berpindah ke 1 wilayah bersebelahan.\n'
             '   - Buy Project Card (1 AP): Membeli kartu proyek di district tempat bidak berada.\n'
             '   - Buy Tech Card (1 AP): Membeli kartu Tech/Skill di City Center.\n'
             '   - Use Tech / Skill Effect (2 AP): Mengaktifkan efek Consumable Skill.\n'
             '   - Resolve Problem dengan kartu Tech/Skill (2 AP): Mengatasi Problem Card tanpa bayar koin.\n'
             '   - Resolve Problem dengan pembayaran koin (1 AP): Membayar koin sesuai biaya Problem Card.\n'
             '4. End Round: Terapkan penalti Problem Card yang gagal diselesaikan, buang Event Card, rotasi '
             'pemain pertama.\n'
             '• Aturan City Center: Setiap kali tiba di City Center, pemain memperoleh +3 Koin (maksimal 1 '
             'kali per round).'},
 {'id': 'BAB_IV_V',
  'title': 'IV & V. Sistem Koin, Pembelian Kartu, Tech (T1–T5), Skill (S1–S5), & Problem',
  'keywords': ['beli',
               'syarat',
               'tech',
               'requirement',
               't1',
               't2',
               't3',
               't4',
               't5',
               's1',
               's2',
               's3',
               's4',
               's5',
               'permanent',
               'consumable',
               'skill',
               'problem',
               'penalti',
               'dibuang'],
  'content': '• Sumber Koin: +2 Koin di Pre-Action Phase, +3 Koin saat tiba di City Center (maks 1x/round), '
             'dan bonus Event Card.\n'
             "• Syarat Tech Proyek: Kode T1–T5 wajib dimiliki sebelum membeli Project Card. Tanda '+' (misal "
             'T1 + T3) berarti keduanya wajib dimiliki. Kartu Permanent Tech TIDAK dibuang saat dipakai '
             'membangun proyek atau menyelesaikan Problem.\n'
             '• 5 Permanent Technology (Harga 5 Koin di City Center, 1 AP, Pasif Permanen):\n'
             '  - T1 Solar Engineering: Energy +2\n'
             '  - T2 AI Urban System: Mobility +1, QoL +1\n'
             '  - T3 Circular Materials: Environment +2\n'
             '  - T4 Electric Mobility: Mobility +2\n'
             '  - T5 Water Purification: Environment +1, QoL +1\n'
             '• 5 Consumable Skill (Beli di City Center 1 AP, Aktifkan 2 AP, Sekali Pakai lalu dibuang):\n'
             '  - S1 Emergency Response (3 Koin): Batalkan 1 Problem Card penalti\n'
             '  - S2 Carbon Capture Boost (4 Koin): Environment +5\n'
             '  - S3 Traffic Override (4 Koin): Mobility +5\n'
             '  - S4 Public Health Campaign (3 Koin): Quality of Life +5\n'
             '  - S5 Cyber Shield (4 Koin): Batalkan 1 efek negatif Skill/Event pada kota sendiri'},
 {'id': 'BAB_VI_XI',
  'title': 'VI & XI. Endgame, Bonus Koin Akhir, Tie-Breaker, & Profil Kota AI Auditor',
  'keywords': ['endgame',
               'pemenang',
               'juara',
               'bonus koin',
               '20 koin',
               'tie-breaker',
               'tie breaker',
               'seri',
               'imbang',
               'average score',
               'archetype',
               'profil kota',
               'audit'],
  'content': '• Bonus Koin Akhir (Setelah Round 13 selesai): Setiap kelipatan 20 koin penuh memberikan +5 '
             'pada MASING-MASING dari 4 aspek:\n'
             '  - 0–19 Koin: +0 semua aspek\n'
             '  - 20–39 Koin: +5 semua aspek\n'
             '  - 40–59 Koin: +10 semua aspek\n'
             '  - 60–79 Koin: +15 semua aspek\n'
             '• Rumus Skor Akhir: Average Score = (Mobility + Energy + Environment + Quality of Life) / 4 '
             '(setelah seluruh aspek dikunci pada rentang 0–100).\n'
             '• Hierarki Tie-Breaker Resmi:\n'
             '  1. Average Score tertinggi\n'
             '  2. Jumlah Project Card terbanyak\n'
             '  3. Jumlah Permanent Technology terbanyak\n'
             '  4. Sisa Koin terbanyak\n'
             '• 7 Archetype Kota Masa Depan: Balanced Sustainable Metropolis, Green Eco City, Smart Energy '
             'City, Connected Mobility City, People-First City, Uneven / At-Risk City, dan Emerging Smart '
             'City.'}]

# ==============================================================================
# INDEX MAPS & HELPER LOOKUPS (TANPA ASSET GAMBAR)
# ==============================================================================
# 4 Action Reference Cards untuk 4 Pemain (Round Flow, 3 AP, City Center & Tie-Breaker)
REFERENCE_CARDS: List[Dict[str, Any]] = [
    {
        "id": f"REF0{i}",
        "code": f"REF0{i}",
        "global_no": 193 + i,
        "name": f"Player Action Reference Card #{i}",
        "category": "Reference",
        "district": "City Center",
        "emoji": "📋",
        "cost": 0,
        "tech_req": "-",
        "tech_list": [],
        "M": 0,
        "E": 0,
        "ENV": 0,
        "QoL": 0,
        "effects": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
        "effect_str": "Panduan Cepat Pemain",
        "effect_summary": "3 AP / Round · City Center (+3 🪙) · Bonus Koin (+5 all / 20 🪙)",
        "description": "Kartu panduan alur giliran resmi EcoNova: Pindah (1 AP), Beli Proyek/Tech (1 AP), Selesaikan Problem via Tech (2 AP) atau Koin (1 AP). Tie-breaker: Avg -> Proyek -> Tech -> Koin.",
        "picker_label": f"[REF0{i}] 📋 Player Action Reference Sheet #{i}",
    }
    for i in range(1, 5)
]

ALL_CARDS: List[Dict[str, Any]] = (
    PROJECT_CARDS + TECH_CARDS_UNIQUE + PROBLEM_CARDS + EVENT_CARDS + REFERENCE_CARDS
)

# 197 Kartu Koleksi Fisik Lengkap Box EcoNova (120 Proyek + 40 Tech Deck + 20 Problem + 13 Event + 4 Reference)
ALL_CARDS_197: List[Dict[str, Any]] = (
    PROJECT_CARDS + TECH_CARDS_40 + PROBLEM_CARDS + EVENT_CARDS + REFERENCE_CARDS
)

def get_card_image_path(card_id_or_code: str, prefer_webp: bool = True) -> Optional[str]:
    """Mengembalikan None karena aset gambar telah dinonaktifkan/dihapus dari dataset kartu."""
    return None

PROJECT_BY_ID: Dict[str, Dict[str, Any]] = {c["id"]: c for c in PROJECT_CARDS}
PROJECT_BY_LABEL: Dict[str, Dict[str, Any]] = {c["picker_label"]: c for c in PROJECT_CARDS}

PERMANENT_TECH_BY_CODE: Dict[str, Dict[str, Any]] = {t["code"]: t for t in PERMANENT_TECH_CARDS}
SKILL_BY_CODE: Dict[str, Dict[str, Any]] = {s["code"]: s for s in CONSUMABLE_SKILL_CARDS}
TECH_UNIQUE_BY_CODE: Dict[str, Dict[str, Any]] = {t["code"]: t for t in TECH_CARDS_UNIQUE}

PROBLEM_BY_ID: Dict[str, Dict[str, Any]] = {p["id"]: p for p in PROBLEM_CARDS}
PROBLEM_BY_LABEL: Dict[str, Dict[str, Any]] = {p["picker_label"]: p for p in PROBLEM_CARDS}

EVENT_BY_ROUND: Dict[int, Dict[str, Any]] = {e["round"]: e for e in EVENT_CARDS}
EVENT_BY_ID: Dict[str, Dict[str, Any]] = {e["id"]: e for e in EVENT_CARDS}

CATEGORY_COLOR_THEMES: Dict[str, Dict[str, str]] = {
    "Energy": {
        "name": "Energy",
        "primary": "#F59E0B",
        "accent": "#FBBF24",
        "bg_glass": "rgba(245, 158, 11, 0.16)",
        "border_glass": "rgba(245, 158, 11, 0.45)",
        "text": "#B45309",
        "badge_bg": "#FEF3C7",
        "gradient": "linear-gradient(135deg, rgba(245, 158, 11, 0.22) 0%, rgba(251, 191, 36, 0.12) 100%)",
    },
    "Problem": {
        "name": "Problem",
        "primary": "#EF4444",
        "accent": "#DC2626",
        "bg_glass": "rgba(239, 68, 68, 0.16)",
        "border_glass": "rgba(239, 68, 68, 0.45)",
        "text": "#BE123C",
        "badge_bg": "#FFE4E6",
        "gradient": "linear-gradient(135deg, rgba(239, 68, 68, 0.22) 0%, rgba(220, 38, 38, 0.12) 100%)",
    },
    "Green Park": {
        "name": "Green Park",
        "primary": "#059669",
        "accent": "#10B981",
        "bg_glass": "rgba(5, 150, 105, 0.16)",
        "border_glass": "rgba(5, 150, 105, 0.4)",
        "text": "#047857",
        "badge_bg": "#DCFCE7",
        "gradient": "linear-gradient(135deg, rgba(5, 150, 105, 0.22) 0%, rgba(16, 185, 129, 0.12) 100%)",
    },
    "Transportation": {
        "name": "Transportation",
        "primary": "#0284C7",
        "accent": "#06B6D4",
        "bg_glass": "rgba(2, 132, 199, 0.16)",
        "border_glass": "rgba(2, 132, 199, 0.4)",
        "text": "#0369A1",
        "badge_bg": "#E0F2FE",
        "gradient": "linear-gradient(135deg, rgba(2, 132, 199, 0.22) 0%, rgba(6, 182, 212, 0.12) 100%)",
    },
    "Residential": {
        "name": "Residential",
        "primary": "#8B5CF6",
        "accent": "#7C3AED",
        "bg_glass": "rgba(139, 92, 246, 0.16)",
        "border_glass": "rgba(139, 92, 246, 0.4)",
        "text": "#6D28D9",
        "badge_bg": "#EDE9FE",
        "gradient": "linear-gradient(135deg, rgba(139, 92, 246, 0.22) 0%, rgba(124, 58, 237, 0.12) 100%)",
    },
    "Industrial": {
        "name": "Industrial",
        "primary": "#64748B",
        "accent": "#475569",
        "bg_glass": "rgba(100, 116, 139, 0.16)",
        "border_glass": "rgba(100, 116, 139, 0.4)",
        "text": "#334155",
        "badge_bg": "#F1F5F9",
        "gradient": "linear-gradient(135deg, rgba(100, 116, 139, 0.22) 0%, rgba(71, 85, 105, 0.12) 100%)",
    },
    "Public Services": {
        "name": "Public Services",
        "primary": "#EC4899",
        "accent": "#DB2777",
        "bg_glass": "rgba(236, 72, 153, 0.16)",
        "border_glass": "rgba(236, 72, 153, 0.4)",
        "text": "#BE185D",
        "badge_bg": "#FCE7F3",
        "gradient": "linear-gradient(135deg, rgba(236, 72, 153, 0.22) 0%, rgba(219, 39, 119, 0.12) 100%)",
    },
    "Commercial": {
        "name": "Commercial",
        "primary": "#0D9488",
        "accent": "#14B8A6",
        "bg_glass": "rgba(13, 148, 136, 0.16)",
        "border_glass": "rgba(13, 148, 136, 0.4)",
        "text": "#0F766E",
        "badge_bg": "#CCFBF1",
        "gradient": "linear-gradient(135deg, rgba(13, 148, 136, 0.22) 0%, rgba(20, 184, 166, 0.12) 100%)",
    },
    "Water": {
        "name": "Water",
        "primary": "#2563EB",
        "accent": "#3B82F6",
        "bg_glass": "rgba(37, 99, 235, 0.16)",
        "border_glass": "rgba(37, 99, 235, 0.4)",
        "text": "#1D4ED8",
        "badge_bg": "#DBEAFE",
        "gradient": "linear-gradient(135deg, rgba(37, 99, 235, 0.22) 0%, rgba(59, 130, 246, 0.12) 100%)",
    },
    "Tech": {
        "name": "Permanent Tech",
        "primary": "#0284C7",
        "accent": "#06B6D4",
        "bg_glass": "rgba(2, 132, 199, 0.16)",
        "border_glass": "rgba(2, 132, 199, 0.4)",
        "text": "#0369A1",
        "badge_bg": "#E0F2FE",
        "gradient": "linear-gradient(135deg, rgba(2, 132, 199, 0.22) 0%, rgba(6, 182, 212, 0.12) 100%)",
    },
    "Skill": {
        "name": "Consumable Skill",
        "primary": "#8B5CF6",
        "accent": "#A855F7",
        "bg_glass": "rgba(139, 92, 246, 0.16)",
        "border_glass": "rgba(139, 92, 246, 0.4)",
        "text": "#6D28D9",
        "badge_bg": "#EDE9FE",
        "gradient": "linear-gradient(135deg, rgba(139, 92, 246, 0.22) 0%, rgba(168, 85, 247, 0.12) 100%)",
    },
    "Event": {
        "name": "Global Event",
        "primary": "#059669",
        "accent": "#10B981",
        "bg_glass": "rgba(5, 150, 105, 0.16)",
        "border_glass": "rgba(5, 150, 105, 0.4)",
        "text": "#047857",
        "badge_bg": "#DCFCE7",
        "gradient": "linear-gradient(135deg, rgba(5, 150, 105, 0.22) 0%, rgba(16, 185, 129, 0.12) 100%)",
    },
}

# Sinkronisasi atribut warna dan dictionary effects (uppercase & lowercase) ke seluruh kartu
for _c in ALL_CARDS_197:
    _dist = _c.get("district", "")
    _cat = _c.get("category", "")
    _subtype = _c.get("sub_type", "")
    _code = str(_c.get("code", _c.get("id", "")))
    
    if _cat == "Problem":
        _c["color_theme"] = CATEGORY_COLOR_THEMES["Problem"]
    elif _cat == "Tech":
        if _subtype == "Consumable Skill" or _code.startswith("S"):
            _c["color_theme"] = CATEGORY_COLOR_THEMES["Skill"]
        else:
            _c["color_theme"] = CATEGORY_COLOR_THEMES["Tech"]
    elif _cat == "Event":
        _c["color_theme"] = CATEGORY_COLOR_THEMES["Event"]
    elif _dist in CATEGORY_COLOR_THEMES:
        _c["color_theme"] = CATEGORY_COLOR_THEMES[_dist]
    else:
        _c["color_theme"] = CATEGORY_COLOR_THEMES["Green Park"]

    _m = int(_c.get("M", 0))
    _e = int(_c.get("E", 0))
    _env = int(_c.get("ENV", 0))
    _qol = int(_c.get("QoL", 0))
    _coins = int(_c.get("cost", 0))
    _c["effects"] = {
        "M": _m,
        "E": _e,
        "ENV": _env,
        "QoL": _qol,
        "mobility": _m,
        "energy": _e,
        "env": _env,
        "qol": _qol,
        "coins": _coins,
    }


def get_card_clean_name(card_or_id: Any) -> str:
    """Mengembalikan HANYA nama kartu bersih tanpa embel-embel statistik."""
    if isinstance(card_or_id, dict):
        return card_or_id.get("name", "")
    cid = str(card_or_id).strip()
    if cid in PROJECT_BY_ID:
        return PROJECT_BY_ID[cid]["name"]
    if cid in PERMANENT_TECH_BY_CODE:
        return PERMANENT_TECH_BY_CODE[cid]["name"]
    if cid in SKILL_BY_CODE:
        return SKILL_BY_CODE[cid]["name"]
    if cid in TECH_UNIQUE_BY_CODE:
        return TECH_UNIQUE_BY_CODE[cid]["name"]
    if cid in PROBLEM_BY_ID:
        return PROBLEM_BY_ID[cid]["name"]
    if cid in EVENT_BY_ID:
        return EVENT_BY_ID[cid]["name"]
    for c in ALL_CARDS_197:
        if c.get("id") == cid or c.get("code") == cid:
            return c.get("name", cid)
    return cid


def get_card_color_theme(card_or_id: Any) -> Dict[str, str]:
    """Mengembalikan color_theme untuk styling kartu 3D glassmorphism."""
    card = None
    if isinstance(card_or_id, dict):
        card = card_or_id
    else:
        cid = str(card_or_id).strip()
        card = (
            PROJECT_BY_ID.get(cid)
            or PERMANENT_TECH_BY_CODE.get(cid)
            or SKILL_BY_CODE.get(cid)
            or TECH_UNIQUE_BY_CODE.get(cid)
            or PROBLEM_BY_ID.get(cid)
            or EVENT_BY_ID.get(cid)
        )
    th = dict(card.get("color_theme", {})) if card and "color_theme" in card else dict(CATEGORY_COLOR_THEMES.get("Green Park", {}))
    # Safety aliases for styling
    if "bg" not in th:
        th["bg"] = th.get("badge_bg", th.get("bg_glass", "rgba(255, 255, 255, 0.85)"))
    if "border" not in th:
        th["border"] = th.get("border_glass", "rgba(5, 150, 105, 0.4)")
    return th


def evaluate_single_event_live(
    event_id: Optional[str],
    project_ids: List[str],
    tech_codes: List[str],
    is_immune: bool = False,
) -> Dict[str, Any]:
    """
    Menghitung live modifier langsung dari Event Card yang sedang aktif di ronde berjalan:
    - EV01: +2 Koin
    - EV02: -2 Mobility (kebal jika punya T4 atau S5 aktif)
    - EV03: Diskon 2 Koin Energy (aturan pasar/fiskal)
    - EV04: +3 Environment jika punya minimal 1 Green Park
    - EV05: Diskon 2 Koin Tech (aturan pasar/fiskal)
    - EV06: -2 Environment jika punya >=2 Industrial (kebal jika punya T3 atau S5 aktif)
    - EV07: +3 Mobility jika punya minimal 1 Transportation
    - EV08: +2 ENV, +1 QoL jika punya minimal 1 Water
    - EV09: +3 Koin
    - EV10: -2 Environment (kebal jika punya T3 atau T5 atau S5 aktif)
    - EV11: +3 QoL jika punya T2
    - EV12: +3 Energy jika punya T1
    - EV13: +2 Koin, +2 Environment
    """
    if not event_id or str(event_id).strip() not in EVENT_BY_ID:
        return {
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "note": "Belum ada Event Card yang dibuka di papan fisik ronde ini.",
        }

    tech_set = set(tech_codes or [])
    dist_counts: Dict[str, int] = {}
    for pid in (project_ids or []):
        p = PROJECT_BY_ID.get(pid) or PROJECT_BY_LABEL.get(pid)
        if p:
            d = p.get("district", "")
            dist_counts[d] = dist_counts.get(d, 0) + 1

    delta = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    bonus_coins = 0
    note = ""

    eid = str(event_id).strip()
    if eid == "EV01":
        bonus_coins += 2
        note = "Subsidi global ronde 1: +2 Koin"
    elif eid == "EV02":
        if "T4" in tech_set:
            note = "Kebal krisis bahan bakar (T4 Electric Mobility)"
        else:
            delta["M"] -= 2
            note = "Penalti krisis bahan bakar: -2 Mobility (butuh T4)"
    elif eid == "EV03":
        note = "Diskon 2 Koin Project Card di Energy District"
    elif eid == "EV04":
        if dist_counts.get("Green Park", 0) >= 1:
            delta["ENV"] += 3
            note = f"Gerakan hijau aktif: +3 Environment ({dist_counts['Green Park']} Green Park)"
        else:
            note = "Tidak berlaku (belum memiliki proyek Green Park)"
    elif eid == "EV05":
        note = "Diskon 2 Koin Tech Card di City Center"
    elif eid == "EV06":
        if dist_counts.get("Industrial", 0) >= 2:
            if "T3" in tech_set:
                note = "Kebal regulasi polusi industri (T3 Circular Materials)"
            else:
                delta["ENV"] -= 2
                note = f"Penalti regulasi emisi: -2 Environment ({dist_counts['Industrial']} Industrial tanpa T3)"
        else:
            note = "Aman (kurang dari 2 proyek kawasan Industrial)"
    elif eid == "EV07":
        if dist_counts.get("Transportation", 0) >= 1:
            delta["M"] += 3
            note = f"Kampanye transit aktif: +3 Mobility ({dist_counts['Transportation']} Transportation)"
        else:
            note = "Tidak berlaku (belum memiliki proyek Transportation)"
    elif eid == "EV08":
        if dist_counts.get("Water", 0) >= 1:
            delta["ENV"] += 2
            delta["QoL"] += 1
            note = f"Konservasi air aktif: +2 ENV, +1 QoL ({dist_counts['Water']} Water)"
        else:
            note = "Tidak berlaku (belum memiliki proyek Water)"
    elif eid == "EV09":
        bonus_coins += 3
        note = "Boom ekonomi pasar: +3 Koin"
    elif eid == "EV10":
        if "T3" in tech_set or "T5" in tech_set:
            note = "Kebal cuaca ekstrem (T3 Circular Materials / T5 Water Purification)"
        else:
            delta["ENV"] -= 2
            note = "Penalti cuaca ekstrem: -2 Environment (butuh T3 / T5)"
    elif eid == "EV11":
        if "T2" in tech_set:
            delta["QoL"] += 3
            note = "Transformasi digital aktif: +3 QoL (T2 AI Urban System)"
        else:
            note = "Tidak berlaku (belum memiliki T2 AI Urban System)"
    elif eid == "EV12":
        if "T1" in tech_set:
            delta["E"] += 3
            note = "Revolusi energi bersih aktif: +3 Energy (T1 Solar Engineering)"
        else:
            note = "Tidak berlaku (belum memiliki T1 Solar Engineering)"
    elif eid == "EV13":
        bonus_coins += 2
        delta["ENV"] += 2
        note = "Festival masa depan berkelanjutan: +2 Koin, +2 Environment"

    # Jika imunitas S5 aktif, abaikan seluruh penalti / nilai negatif
    if is_immune:
        penalties_prevented = []
        for k in ("M", "E", "ENV", "QoL"):
            if delta[k] < 0:
                penalties_prevented.append(f"{k} {delta[k]}")
                delta[k] = 0
        if penalties_prevented:
            note = f"[S5 Cyber Shield: Kebal Penalti ({', '.join(penalties_prevented)})!] " + note
        else:
            note = "[S5 Cyber Shield Aktif: Siaga Imunitas] " + note

    return {
        "delta": delta,
        "coins": bonus_coins,
        "note": note,
    }



def clamp_stat(value: int) -> int:
    """Mengunci nilai stat aspek kota pada rentang resmi [0, 100]."""
    return max(0, min(100, int(value)))


def calculate_coin_bonus(coins: int) -> int:
    """
    Menghitung bonus koin akhir resmi Rulebook Bab VI.1:
    Setiap kelipatan 20 koin penuh memberikan +5 poin ke masing-masing 4 aspek.
    """
    c = max(0, int(coins))
    return (c // 20) * 5


def classify_city_archetype(M: int, E: int, ENV: int, QoL: int) -> Dict[str, Any]:
    """
    Klasifikasi deterministik Archetype Kota Masa Depan berdasarkan skor akhir 4 aspek.
    Aturan Prioritas:
    1. Uneven / At-Risk City: Ada minimal satu aspek < 40 atau Average Score < 50 (atau ketimpangan ekstrem >= 30).
    2. Balanced Sustainable Metropolis: Avg >= 75 dan semua aspek >= 65 (atau semua aspek >= 60 dengan selisih <= 15).
    3. Green Eco City: ENV adalah skor tertinggi dan ENV >= 70.
    4. Smart Energy City: E adalah skor tertinggi dan E >= 70.
    5. Connected Mobility City: M adalah skor tertinggi dan M >= 70.
    6. People-First City: QoL adalah skor tertinggi dan QoL >= 70.
    7. Emerging Smart City: Kondisi lainnya (kota sedang berkembang).
    """
    scores = {
        "Mobility": int(M),
        "Energy": int(E),
        "Environment": int(ENV),
        "Quality of Life": int(QoL),
    }
    avg_score = round((M + E + ENV + QoL) / 4.0, 2)
    min_aspect = min(scores, key=scores.get)
    max_aspect = max(scores, key=scores.get)
    min_val = scores[min_aspect]
    max_val = scores[max_aspect]
    spread = max_val - min_val

    if min_val < 40 or avg_score < 50:
        archetype = "Uneven / At-Risk City"
        emoji = "⚠️"
        color = "#BE123C"
        tagline = "Kota dengan Ketimpangan Struktural & Kerentanan Krisis"
        reason = (
            f"Terdapat pilar kota di bawah ambang aman (<40) yaitu {min_aspect} ({min_val}) "
            f"atau rata-rata skor kota ({avg_score}) masih di bawah 50."
        )
    elif avg_score >= 75 and min_val >= 65:
        archetype = "Balanced Sustainable Metropolis"
        emoji = "🌟"
        color = "#15803D"
        tagline = "Metropolis Solarpunk Paripurna & Berketahanan Holistik"
        reason = (
            f"Rata-rata skor mencapai {avg_score} (>=75) dan seluruh 4 aspek berada di atas 65 "
            f"(terendah: {min_aspect} {min_val}, tertinggi: {max_aspect} {max_val})."
        )
    elif ENV >= 70 and ENV == max_val:
        archetype = "Green Eco City"
        emoji = "🌿"
        color = "#15803D"
        tagline = "Kota Hutan Biosfer & Pelopor Ekologi Sirkular"
        reason = f"Environment ({ENV}) menjadi kekuatan tertinggi kota (>=70) dengan ekosistem hijau yang mendominasi."
    elif E >= 70 and E == max_val:
        archetype = "Smart Energy City"
        emoji = "⚡"
        color = "#B45309"
        tagline = "Sentra Megagrid Surya & Kemandirian Energi Bersih"
        reason = f"Energy ({E}) menjadi pilar tertinggi kota (>=70) berkat infrastruktur energi terbarukan yang masif."
    elif M >= 70 and M == max_val:
        archetype = "Connected Mobility City"
        emoji = "🚝"
        color = "#0369A1"
        tagline = "Poros Transit Otonom & Konektivitas Niremisi"
        reason = f"Mobility ({M}) menjadi kekuatan tertinggi kota (>=70) dengan jaringan transportasi publik berkecepatan tinggi."
    elif QoL >= 70 and QoL == max_val:
        archetype = "People-First City"
        emoji = "🏢"
        color = "#BE123C"
        tagline = "Kota Humanis Berstandar Kesejahteraan & Layanan Publik Prima"
        reason = f"Quality of Life ({QoL}) menjadi skor tertinggi kota (>=70) yang memprioritaskan kesehatan, hunian, dan warga."
    else:
        archetype = "Emerging Smart City"
        emoji = "🌱"
        color = "#0284C7"
        tagline = "Kota Pintar Transisional yang Sedang Bertumbuh"
        reason = (
            f"Fondasi kota berkembang stabil (Avg {avg_score}) dengan keunggulan awal pada {max_aspect} ({max_val}) "
            f"dan ruang akselerasi pada {min_aspect} ({min_val})."
        )

    def tier_info(v: int) -> Dict[str, str]:
        if v >= 80:
            return {"tier": "Unggul", "range": "80–100", "color": "#15803D", "desc": "Kekuatan utama kota"}
        if v >= 60:
            return {"tier": "Baik", "range": "60–79", "color": "#0369A1", "desc": "Berfungsi baik mendukung kota"}
        if v >= 40:
            return {"tier": "Berkembang", "range": "40–59", "color": "#B45309", "desc": "Fondasi dasar, butuh investasi"}
        return {"tier": "Rendah", "range": "0–39", "color": "#BE123C", "desc": "Rentan & menghambat kota"}

    return {
        "name": archetype,
        "badge": archetype,
        "emoji": "",
        "color": color,
        "tagline": tagline,
        "reason": reason,
        "min_aspect": min_aspect,
        "max_aspect": max_aspect,
        "spread": spread,
        "tiers": {k: tier_info(v) for k, v in scores.items()},
    }


def evaluate_events_for_player(
    project_ids: List[str],
    tech_codes: List[str],
) -> Dict[str, Any]:
    """
    Evaluasi Otomatis Backend 13 Global Event Card (Round 1–13):
    Menghitung dampak penalti/bonus dari rulebook berdasarkan Project dan Tech yang dimiliki pemain.
    """
    tech_set = set(tech_codes or [])
    dist_counts: Dict[str, int] = {}
    for pid in (project_ids or []):
        p = PROJECT_BY_ID.get(pid) or PROJECT_BY_LABEL.get(pid)
        if p:
            d = p.get("district", "")
            dist_counts[d] = dist_counts.get(d, 0) + 1

    events_log = []
    delta = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    bonus_coins = 0

    # EV01: Round 1 Green Investment Program (+2 Koin)
    bonus_coins += 2
    events_log.append({
        "round": 1,
        "id": "EV01",
        "name": "Green Investment Program",
        "status": "Diterima (+2 🪙)",
        "badge": "💰 +2 Koin",
        "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
        "coins": 2,
        "detail": "Seluruh pemain menerima subsidi awal +2 Koin.",
    })

    # EV02: Round 2 Global Fuel Crisis (-2 M, kebal jika punya T4)
    if "T4" in tech_set:
        events_log.append({
            "round": 2,
            "id": "EV02",
            "name": "Global Fuel Crisis",
            "status": "Kebal 🛡️ (T4 Electric Mobility)",
            "badge": "🛡️ 0 M",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Krisis bahan bakar ditangkal oleh teknologi T4 Electric Mobility.",
        })
    else:
        delta["M"] -= 2
        events_log.append({
            "round": 2,
            "id": "EV02",
            "name": "Global Fuel Crisis",
            "status": "Penalti ⚠️ (-2 M)",
            "badge": "🚗 -2 M",
            "delta": {"M": -2, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Kehilangan -2 Mobility akibat ketergantungan bahan bakar fosil tanpa T4.",
        })

    # EV03: Round 3 Renewable Energy Subsidy (Diskon 2 Koin Energy)
    events_log.append({
        "round": 3,
        "id": "EV03",
        "name": "Renewable Energy Subsidy",
        "status": "Fasilitas Pasar ℹ️",
        "badge": "🏷️ Diskon 2 🪙",
        "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
        "coins": 0,
        "detail": "Subsidi diskon 2 koin saat membeli Project Card di Energy District.",
    })

    # EV04: Round 4 Urban Green Movement (+3 ENV jika ada Green Park)
    if dist_counts.get("Green Park", 0) >= 1:
        delta["ENV"] += 3
        events_log.append({
            "round": 4,
            "id": "EV04",
            "name": "Urban Green Movement",
            "status": "Aktif 🌿 (+3 ENV)",
            "badge": "🌿 +3 ENV",
            "delta": {"M": 0, "E": 0, "ENV": 3, "QoL": 0},
            "coins": 0,
            "detail": f"Memperoleh +3 ENV berkat kepemilikan {dist_counts['Green Park']} proyek Green Park.",
        })
    else:
        events_log.append({
            "round": 4,
            "id": "EV04",
            "name": "Urban Green Movement",
            "status": "Tidak Berlaku ⚪",
            "badge": "0 ENV",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Belum memiliki proyek di Green Park District.",
        })

    # EV05: Round 5 Smart City Innovation Week (Diskon 2 Koin Tech)
    events_log.append({
        "round": 5,
        "id": "EV05",
        "name": "Smart City Innovation Week",
        "status": "Fasilitas Pasar ℹ️",
        "badge": "🔬 Diskon 2 🪙",
        "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
        "coins": 0,
        "detail": "Diskon 2 koin saat membeli kartu teknologi di City Center.",
    })

    # EV06: Round 6 Industrial Pollution Regulation (-2 ENV jika >=2 Industrial, kebal jika punya T3)
    if dist_counts.get("Industrial", 0) >= 2:
        if "T3" in tech_set:
            events_log.append({
                "round": 6,
                "id": "EV06",
                "name": "Industrial Pollution Regulation",
                "status": "Kebal 🛡️ (T3 Circular Materials)",
                "badge": "🛡️ 0 ENV",
                "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
                "coins": 0,
                "detail": "Sirkularitas T3 menyerap emisi kawasan industri.",
            })
        else:
            delta["ENV"] -= 2
            events_log.append({
                "round": 6,
                "id": "EV06",
                "name": "Industrial Pollution Regulation",
                "status": "Penalti ⚠️ (-2 ENV)",
                "badge": "🌿 -2 ENV",
                "delta": {"M": 0, "E": 0, "ENV": -2, "QoL": 0},
                "coins": 0,
                "detail": "Kawasan industri >= 2 menimbulkan polusi tanpa T3.",
            })
    else:
        events_log.append({
            "round": 6,
            "id": "EV06",
            "name": "Industrial Pollution Regulation",
            "status": "Aman ⚪ (<2 Proyek Industri)",
            "badge": "0 ENV",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Beban industri kota berada di bawah batas regulasi.",
        })

    # EV07: Round 7 Public Transportation Campaign (+3 M jika ada Transportation)
    if dist_counts.get("Transportation", 0) >= 1:
        delta["M"] += 3
        events_log.append({
            "round": 7,
            "id": "EV07",
            "name": "Public Transportation Campaign",
            "status": "Aktif 🚝 (+3 M)",
            "badge": "🚗 +3 M",
            "delta": {"M": 3, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": f"Mendapat +3 Mobility berkat {dist_counts['Transportation']} proyek Transportation.",
        })
    else:
        events_log.append({
            "round": 7,
            "id": "EV07",
            "name": "Public Transportation Campaign",
            "status": "Tidak Berlaku ⚪",
            "badge": "0 M",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Belum memiliki proyek di Transportation District.",
        })

    # EV08: Round 8 Water Conservation Month (+2 ENV, +1 QoL jika ada Water)
    if dist_counts.get("Water", 0) >= 1:
        delta["ENV"] += 2
        delta["QoL"] += 1
        events_log.append({
            "round": 8,
            "id": "EV08",
            "name": "Water Conservation Month",
            "status": "Aktif 💧 (+2 ENV, +1 QoL)",
            "badge": "🌿 +2 ENV | 🏢 +1 QoL",
            "delta": {"M": 0, "E": 0, "ENV": 2, "QoL": 1},
            "coins": 0,
            "detail": f"Mendapat +2 ENV dan +1 QoL berkat {dist_counts['Water']} proyek Water District.",
        })
    else:
        events_log.append({
            "round": 8,
            "id": "EV08",
            "name": "Water Conservation Month",
            "status": "Tidak Berlaku ⚪",
            "badge": "0 Stat",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Belum memiliki proyek di Water District.",
        })

    # EV09: Round 9 Economic Boom (+3 Koin)
    bonus_coins += 3
    events_log.append({
        "round": 9,
        "id": "EV09",
        "name": "Economic Boom",
        "status": "Diterima (+3 🪙)",
        "badge": "💰 +3 Koin",
        "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
        "coins": 3,
        "detail": "Pertumbuhan ekonomi pasar memberikan deviden +3 Koin.",
    })

    # EV10: Round 10 Extreme Weather Alert (-2 ENV, kebal jika punya T3 atau T5)
    if "T3" in tech_set or "T5" in tech_set:
        events_log.append({
            "round": 10,
            "id": "EV10",
            "name": "Extreme Weather Alert",
            "status": "Kebal 🛡️ (T3 / T5)",
            "badge": "🛡️ 0 ENV",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Infrastruktur tahan cuaca ekstrem berkat T3 Circular Materials / T5 Water Purification.",
        })
    else:
        delta["ENV"] -= 2
        events_log.append({
            "round": 10,
            "id": "EV10",
            "name": "Extreme Weather Alert",
            "status": "Penalti ⚠️ (-2 ENV)",
            "badge": "🌿 -2 ENV",
            "delta": {"M": 0, "E": 0, "ENV": -2, "QoL": 0},
            "coins": 0,
            "detail": "Kerusakan cuaca ekstrem akibat minimnya mitigasi material & hidrologi (-2 ENV).",
        })

    # EV11: Round 11 Digital Transformation (+3 QoL jika punya T2)
    if "T2" in tech_set:
        delta["QoL"] += 3
        events_log.append({
            "round": 11,
            "id": "EV11",
            "name": "Digital Transformation",
            "status": "Aktif 🏛️ (+3 QoL)",
            "badge": "🏢 +3 QoL",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 3},
            "coins": 0,
            "detail": "Transformasi digital terintegrasi mulus dengan T2 AI Urban System.",
        })
    else:
        events_log.append({
            "round": 11,
            "id": "EV11",
            "name": "Digital Transformation",
            "status": "Tidak Berlaku ⚪",
            "badge": "0 QoL",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Kota belum mengadopsi teknologi T2 AI Urban System.",
        })

    # EV12: Round 12 Clean Energy Revolution (+3 E jika punya T1)
    if "T1" in tech_set:
        delta["E"] += 3
        events_log.append({
            "round": 12,
            "id": "EV12",
            "name": "Clean Energy Revolution",
            "status": "Aktif ☀️ (+3 E)",
            "badge": "⚡ +3 E",
            "delta": {"M": 0, "E": 3, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Revolusi energi bersih memuncak berkat T1 Solar Engineering.",
        })
    else:
        events_log.append({
            "round": 12,
            "id": "EV12",
            "name": "Clean Energy Revolution",
            "status": "Tidak Berlaku ⚪",
            "badge": "0 E",
            "delta": {"M": 0, "E": 0, "ENV": 0, "QoL": 0},
            "coins": 0,
            "detail": "Kota belum mengadopsi teknologi T1 Solar Engineering.",
        })

    # EV13: Round 13 Sustainable Future Festival (+2 Koin, +2 ENV)
    bonus_coins += 2
    delta["ENV"] += 2
    events_log.append({
        "round": 13,
        "id": "EV13",
        "name": "Sustainable Future Festival",
        "status": "Festival Penutup 🎉 (+2 🪙, +2 ENV)",
        "badge": "🌿 +2 ENV | 💰 +2 🪙",
        "delta": {"M": 0, "E": 0, "ENV": 2, "QoL": 0},
        "coins": 2,
        "detail": "Puncak perayaan kota berkelanjutan memberikan deviden warga dan penghijauan.",
    })

    return {
        "events_delta": delta,
        "bonus_coins": bonus_coins,
        "log": events_log,
    }


def compute_player_score(
    player_name: str,
    city_name: str,
    project_ids: List[str],
    tech_codes: List[str],
    failed_problem_ids: List[str],
    coins: int,
    used_skill_codes: Optional[List[str]] = None,
    include_events: bool = True,
    active_event_id: Optional[str] = None,
    skill_bonus: Optional[Dict[str, int]] = None,
    active_tech_codes: Optional[List[str]] = None,
    accumulated_event_delta: Optional[Dict[str, int]] = None,
    accumulated_event_coins: int = 0,
    is_immune: bool = False,
    manual_delta: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Pure Python Deterministic Score Engine sesuai spesifikasi resmi EcoNova:
    - Baseline: M=50, E=50, ENV=50, QoL=50
    - Tambah stat dari Project Cards yang dibangun
    - Tambah stat dari Permanent Tech (T1–T5) yang telah diaktifkan via tombol aksi (atau seluruhnya pada Final Audit)
    - Tambah stat dari Consumable Skill (S1–S5) yang dikonsumsi (via skill_bonus accumulator)
    - Kurangi penalti dari Failed Problem Cards
    - Tambah akumulasi dampak Event Card masa lalu + modifier live Event Card aktif (dengan imunitas S5 jika aktif)
    - Tambah penyesuaian manual nilai poin (manual_delta) jika diaktifkan oleh pengguna/juri
    - Tambah Bonus Koin Akhir: (effective_coins // 20) * 5 ke masing-masing 4 aspek
    - Clamp setiap aspek ke [0, 100]
    - Hitung Average Score = (M + E + ENV + QoL) / 4
    """
    used_skill_codes = used_skill_codes or []
    skill_bonus = skill_bonus or {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    manual_delta = manual_delta or {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    base = {"M": 50, "E": 50, "ENV": 50, "QoL": 50}
    proj_delta = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    tech_delta = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    skill_delta = {
        "M": skill_bonus.get("M", 0),
        "E": skill_bonus.get("E", 0),
        "ENV": skill_bonus.get("ENV", 0),
        "QoL": skill_bonus.get("QoL", 0),
    }
    prob_delta = {"M": 0, "E": 0, "ENV": 0, "QoL": 0}

    selected_projects: List[Dict[str, Any]] = []
    district_counts: Dict[str, int] = {d: 0 for d in DISTRICT_META}

    for pid in project_ids:
        card = PROJECT_BY_ID.get(pid) or PROJECT_BY_LABEL.get(pid)
        if card:
            selected_projects.append(card)
            proj_delta["M"] += card["M"]
            proj_delta["E"] += card["E"]
            proj_delta["ENV"] += card["ENV"]
            proj_delta["QoL"] += card["QoL"]
            district_counts[card["district"]] = district_counts.get(card["district"], 0) + 1

    selected_techs: List[Dict[str, Any]] = []
    # Efek stat kartu Tech hanya berlaku saat tombol aksi ditekan (atau seluruhnya saat Final Audit)
    eval_tech_codes = active_tech_codes if active_tech_codes is not None else tech_codes
    for tcode in eval_tech_codes:
        tcard = PERMANENT_TECH_BY_CODE.get(tcode)
        if tcard:
            selected_techs.append(tcard)
            tech_delta["M"] += tcard["M"]
            tech_delta["E"] += tcard["E"]
            tech_delta["ENV"] += tcard["ENV"]
            tech_delta["QoL"] += tcard["QoL"]

    selected_skills: List[Dict[str, Any]] = []
    for scode in used_skill_codes:
        scard = SKILL_BY_CODE.get(scode)
        if scard:
            selected_skills.append(scard)
            skill_delta["M"] += scard["M"]
            skill_delta["E"] += scard["E"]
            skill_delta["ENV"] += scard["ENV"]
            skill_delta["QoL"] += scard["QoL"]

    selected_problems: List[Dict[str, Any]] = []
    coin_penalty_from_problems = 0
    for prid in failed_problem_ids:
        pcard = PROBLEM_BY_ID.get(prid) or PROBLEM_BY_LABEL.get(prid)
        if pcard:
            selected_problems.append(pcard)
            prob_delta["M"] += pcard["M"]
            prob_delta["E"] += pcard["E"]
            prob_delta["ENV"] += pcard["ENV"]
            prob_delta["QoL"] += pcard["QoL"]
            coin_penalty_from_problems += pcard.get("coin_loss", 0)

    # Evaluasi Event Cards Backend (13 Ronde Penuh vs Akumulasi & Live Single Event Modifier)
    accum_ev = accumulated_event_delta or {"M": 0, "E": 0, "ENV": 0, "QoL": 0}
    event_delta = {
        "M": accum_ev.get("M", 0),
        "E": accum_ev.get("E", 0),
        "ENV": accum_ev.get("ENV", 0),
        "QoL": accum_ev.get("QoL", 0),
    }
    event_coins = int(accumulated_event_coins or 0)
    events_log = []
    live_event_note = ""

    if include_events:
        ev_eval = evaluate_events_for_player(project_ids, tech_codes)
        event_delta = ev_eval["events_delta"]
        event_coins = ev_eval["bonus_coins"]
        events_log = ev_eval["log"]
    elif active_event_id and str(active_event_id).strip() in EVENT_BY_ID:
        single_ev = evaluate_single_event_live(
            active_event_id, project_ids, tech_codes, is_immune=is_immune
        )
        for k in ("M", "E", "ENV", "QoL"):
            event_delta[k] += single_ev["delta"][k]
        event_coins += single_ev["coins"]
        live_event_note = single_ev["note"]

    effective_coins = max(0, int(coins) - coin_penalty_from_problems + event_coins)
    coin_bonus = calculate_coin_bonus(effective_coins)

    raw_totals = {
        k: (
            base[k]
            + proj_delta[k]
            + tech_delta[k]
            + skill_delta[k]
            + prob_delta[k]
            + event_delta[k]
            + coin_bonus
            + manual_delta.get(k, 0)
        )
        for k in ("M", "E", "ENV", "QoL")
    }
    clamped = {k: clamp_stat(v) for k, v in raw_totals.items()}
    net_deltas = {k: clamped[k] - 50 for k in ("M", "E", "ENV", "QoL")}
    avg_score = round(sum(clamped.values()) / 4.0, 2)

    archetype_info = classify_city_archetype(
        clamped["M"], clamped["E"], clamped["ENV"], clamped["QoL"]
    )

    # Check tech requirements satisfaction across built projects
    owned_tech_set = {t["code"] for t in selected_techs}
    unmet_warnings = []
    for pr in selected_projects:
        missing = [req for req in pr.get("tech_list", []) if req not in owned_tech_set]
        if missing:
            unmet_warnings.append(f"{pr['name']} (butuh {', '.join(missing)})")

    return {
        "player_name": player_name.strip() or "Pemain",
        "city_name": city_name.strip() or "EcoNova City",
        "M": clamped["M"],
        "E": clamped["E"],
        "ENV": clamped["ENV"],
        "QoL": clamped["QoL"],
        "raw_M": raw_totals["M"],
        "raw_E": raw_totals["E"],
        "raw_ENV": raw_totals["ENV"],
        "raw_QoL": raw_totals["QoL"],
        "delta_M": net_deltas["M"],
        "delta_E": net_deltas["E"],
        "delta_ENV": net_deltas["ENV"],
        "delta_QoL": net_deltas["QoL"],
        "manual_delta": manual_delta,
        "avg_score": avg_score,
        "coins": effective_coins,
        "coin_bonus": coin_bonus,
        "proj_delta": proj_delta,
        "tech_delta": tech_delta,
        "skill_delta": skill_delta,
        "prob_delta": prob_delta,
        "event_delta": event_delta,
        "event_coins": event_coins,
        "events_log": events_log,
        "live_event_note": live_event_note,
        "active_event_id": active_event_id,
        "projects": selected_projects,
        "techs": selected_techs,
        "skills": selected_skills,
        "failed_problems": selected_problems,
        "project_count": len(selected_projects),
        "tech_count": len(selected_techs),
        "problem_count": len(selected_problems),
        "district_counts": district_counts,
        "archetype": archetype_info,
        "unmet_tech_warnings": unmet_warnings,
        "tie_tuple": (avg_score, len(selected_projects), len(selected_techs), effective_coins),
    }


def rank_players_audit(player_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Mengurutkan 4 pemain berdasarkan Hierarki Tie-Breaker Resmi Rulebook Bab VI.3:
    1. Average Score tertinggi
    2. Jumlah Project Card terbanyak
    3. Jumlah Permanent Technology terbanyak
    4. Sisa Koin terbanyak
    Menambahkan penjelasan eksplisit jika terjadi tie-breaker!
    """
    sorted_res = sorted(player_results, key=lambda r: r["tie_tuple"], reverse=True)
    for idx, item in enumerate(sorted_res):
        item["rank"] = idx + 1
        item["tie_breaker_reason"] = None

    for i in range(len(sorted_res) - 1):
        curr = sorted_res[i]
        nxt = sorted_res[i + 1]
        if curr["avg_score"] == nxt["avg_score"]:
            if curr["project_count"] != nxt["project_count"]:
                reason = (
                    f"Seri Average Score ({curr['avg_score']:.2f}) dengan {nxt['player_name']} — "
                    f"Unggul Tie-Breaker #1: Jumlah Project Card ({curr['project_count']} vs {nxt['project_count']})."
                )
            elif curr["tech_count"] != nxt["tech_count"]:
                reason = (
                    f"Seri Average Score ({curr['avg_score']:.2f}) & Proyek ({curr['project_count']}) dengan {nxt['player_name']} — "
                    f"Unggul Tie-Breaker #2: Jumlah Permanent Tech ({curr['tech_count']} vs {nxt['tech_count']})."
                )
            elif curr["coins"] != nxt["coins"]:
                reason = (
                    f"Seri Average Score, Proyek, & Tech dengan {nxt['player_name']} — "
                    f"Unggul Tie-Breaker #3: Sisa Koin ({curr['coins']} vs {nxt['coins']} 🪙)."
                )
            else:
                reason = f"Imbang mutlak pada seluruh parameter dengan {nxt['player_name']} (Co-Champion)."
            curr["tie_breaker_reason"] = reason
            if not nxt.get("tie_breaker_reason"):
                nxt["tie_breaker_reason"] = (
                    f"Seri Average Score ({nxt['avg_score']:.2f}) dengan {curr['player_name']}, "
                    f"kalah pada tie-breaker resmi."
                )

    return sorted_res


def generate_city_narrative_report(audit: Dict[str, Any]) -> Dict[str, str]:
    """
    Template Generator Dinamis Berbasis Data untuk 4 Kartu Laporan Audit Kota Masa Depan.
    Selalu menyebutkan nama proyek, teknologi, distrik dominan, dan sejarah krisis (Problem Card) pemain.
    """
    M, E, ENV, QoL = audit["M"], audit["E"], audit["ENV"], audit["QoL"]
    avg = audit["avg_score"]
    city = audit["city_name"]
    mayor = audit["player_name"]
    arch = audit["archetype"]
    projs = audit["projects"]
    techs = audit["techs"]
    probs = audit["failed_problems"]

    aspect_map = {
        "Mobility (M)": M,
        "Energy (E)": E,
        "Environment (ENV)": ENV,
        "Quality of Life (QoL)": QoL,
    }
    sorted_aspects = sorted(aspect_map.items(), key=lambda x: x[1], reverse=True)
    top1_name, top1_val = sorted_aspects[0]
    top2_name, top2_val = sorted_aspects[1]
    weak_name, weak_val = sorted_aspects[-1]

    proj_names = [p["name"] for p in projs[:4]]
    proj_highlight = (
        f"pembangunan **{', '.join(proj_names)}**"
        + (f" beserta {len(projs) - 4} proyek strategis lainnya" if len(projs) > 4 else "")
        if proj_names
        else "fondasi tata ruang awal City Center"
    )
    tech_names = [f"{t['code']} ({t['name']})" for t in techs]
    tech_highlight = (
        f"Sinergi teknologi permanen **{', '.join(tech_names)}** memberikan akselerasi pasif yang konsisten."
        if tech_names
        else "Kota ini berkembang secara organik mengandalkan proyek distrik tanpa ketergantungan pada lisensi teknologi pusat."
    )

    # 1. Kekuatan Utama Kota
    strengths_text = (
        f"**{city}** di bawah kepemimpinan Wali Kota **{mayor}** menonjol sebagai **{arch['name']}** "
        f"dengan kekuatan utama pada **{top1_name} ({top1_val}/100)** dan **{top2_name} ({top2_val}/100)**. "
        f"Keunggulan ini ditopang langsung oleh {proj_highlight}. {tech_highlight}"
    )
    if audit["coin_bonus"] > 0:
        strengths_text += (
            f" Cadangan fiskal akhir sebesar **{audit['coins']} Koin** turut menyuntikkan "
            f"bonus kemakmuran **+{audit['coin_bonus']} poin** ke seluruh empat pilar kota."
        )

    # 2. Tantangan & Sejarah Krisis
    if probs:
        prob_names = [f"**{p['name']}** ({p['pen_str']})" for p in probs]
        crisis_story = (
            f"Rekam jejak sejarah mencatat **{city}** sempat diguncang {len(probs)} krisis perkotaan yang gagal "
            f"termitigasi tepat waktu, yaitu {', '.join(prob_names)}. "
            f"Guncangan tersebut meninggalkan tekanan struktural terutama pada **{weak_name} ({weak_val}/100)**."
        )
    else:
        crisis_story = (
            f"Manajemen risiko Wali Kota **{mayor}** sangat disiplin: **0 Problem Card yang gagal** sepanjang 13 putaran! "
            f"Meskipun kota bebas dari bencana masa lalu, aspek **{weak_name} ({weak_val}/100)** tetap memerlukan "
            f"perhatian ekstra agar tidak tertinggal dari pilar **{top1_name} ({top1_val}/100)** (selisih {arch['spread']} poin)."
        )

    # 3. Simulasi Kehidupan Masa Depan (Tahun 2075)
    m_scene = (
        "kapsul monorel magnetik meluncur hening di antara koridor kanopi hijau tanpa kemacetan"
        if M >= 70
        else (
            "bus elektrik otonom dan jalur komuter sepeda melayani pergerakan warga dengan tertib"
            if M >= 50
            else "kepadatan lalu lintas jam sibuk masih menjadi pemandangan harian di persimpangan utama"
        )
    )
    e_scene = (
        "menara surya biomimetik dan turbin angin vertikal menyuplai 100% energi bersih surplus"
        if E >= 70
        else (
            "jaringan microgrid pintar mendistribusikan listrik terbarukan secara stabil ke seluruh distrik"
            if E >= 50
            else "pasokan daya masih berfluktuasi saat beban puncak sore hari"
        )
    )
    env_scene = (
        "hutan vertikal, kubah biodome, dan sungai sebening kristal menyatu langsung dengan ruang hidup warga"
        if ENV >= 70
        else (
            "taman-taman ekologis dan sistem daur ulang sirkular menjaga udara kota tetap segar"
            if ENV >= 50
            else "kabut tipis residu urban masih terlihat di sekitar zona produktif"
        )
    )
    qol_scene = (
        "warga menikmati fasilitas kesehatan pintar, pendidikan digital, dan ruang komunal dengan indeks kebahagiaan tertinggi"
        if QoL >= 70
        else (
            "komunitas warga hidup harmonis dengan layanan publik distrik yang inklusif"
            if QoL >= 50
            else "warga menantikan perluasan hunian terjangkau dan fasilitas rekreasi baru"
        )
    )

    future_simulation = (
        f"Memasuki pagi hari tahun **2075 di {city}** (Indeks Keberlanjutan **{avg:.2f}/100**), "
        f"{m_scene}. Di cakrawala kota, {e_scene}, sementara di tingkat tapak, {env_scene}. "
        f"Dalam keseharian sosialnya, {qol_scene}."
    )

    # 4. Rekomendasi Pembangunan Selanjutnya
    rec_by_weak = {
        "Mobility (M)": (
            "Prioritaskan pembangunan di **Transportation District** (seperti *Metro Station*, *High Speed Rail*, "
            "atau *Autonomous Public Transport*) serta akuisisi teknologi **T4 (Electric Mobility)**."
        ),
        "Energy (E)": (
            "Akselerasi investasi di **Energy District** (seperti *Smart Power Grid*, *Solar Farm*, atau "
            "*Renewable Energy Megagrid*) yang dipadukan dengan teknologi **T1 (Solar Engineering)**."
        ),
        "Environment (ENV)": (
            "Perluas sabuk ekologis melalui **Green Park & Water District** (*Biodiversity Sanctuary*, "
            "*Carbon Absorption Forest*, *Zero Wastewater City*) dengan dukungan **T3 (Circular Materials)** & **T5**."
        ),
        "Quality of Life (QoL)": (
            "Tingkatkan kesejahteraan warga melalui **Public Services & Residential District** (*Smart Healthcare Center*, "
            "*Universal Public Service Hub*, *Smart Residential Network*) bersama **T2 (AI Urban System)**."
        ),
    }
    recommendation_text = (
        f"1. **Fokus Penyeimbangan ({weak_name}):** {rec_by_weak[weak_name]}\n"
        f"2. **Mitigasi Krisis:** Siapkan cadangan **Consumable Skill S1 (Emergency Response)** atau **T2/T3** di City Center "
        f"agar penalti Problem Card tidak menggerus skor aspek di putaran akhir.\n"
        f"3. **Optimalisasi Fiskal:** Pertahankan tabungan akhir di kelipatan **20 Koin** (20 / 40 Koin) untuk mengunci "
        f"bonus instan **+5 hingga +10 poin** di seluruh aspek."
    )

    return {
        "strengths": strengths_text,
        "challenges": crisis_story,
        "future_simulation": future_simulation,
        "recommendations": recommendation_text,
    }


def smart_rulebook_search(query: str) -> str:
    """
    Fallback Smart Keyword Search Engine lokal jika API Key LLM belum diaktifkan.
    Mencari jawaban relevan dari RULEBOOK_SECTIONS dan seluruh database kartu (Project, Tech, Problem, Event).
    """
    q = query.strip().lower()
    if not q:
        return "Silakan ketik pertanyaan seputar aturan EcoNova, Action Points (AP), diskon Event, syarat Tech, atau nama kartu."

    matched_sections = []
    for sec in RULEBOOK_SECTIONS:
        score = 0
        if any(kw in q for kw in sec["keywords"]):
            score += 3
        for word in re.findall(r"[a-z0-9]+", q):
            if len(word) >= 2 and (word in sec["title"].lower() or word in sec["content"].lower()):
                score += 1
        if score > 0:
            matched_sections.append((score, sec))

    matched_sections.sort(key=lambda x: x[0], reverse=True)

    matched_cards = []
    for c in ALL_CARDS:
        c_score = 0
        if q in c["id"].lower() or q == c.get("code", "").lower():
            c_score += 10
        if q in c["name"].lower():
            c_score += 8
        for word in re.findall(r"[a-z0-9]+", q):
            if len(word) >= 2:
                if word == c["id"].lower() or word == c.get("code", "").lower():
                    c_score += 6
                elif word in c["name"].lower():
                    c_score += 4
                elif word in c.get("district", "").lower() or word in c.get("description", "").lower():
                    c_score += 1
        if c_score >= 3:
            matched_cards.append((c_score, c))

    matched_cards.sort(key=lambda x: x[0], reverse=True)

    out_lines = ["### 🤖 Jawaban Asisten Rulebook EcoNova *(Smart Local Knowledge Engine)*"]

    if matched_sections:
        for _, sec in matched_sections[:2]:
            out_lines.append(f"#### 📖 {sec['title']}\n{sec['content']}")

    if matched_cards:
        out_lines.append("#### 🃏 Kartu Terkait yang Ditemukan di Database:")
        for _, c in matched_cards[:5]:
            out_lines.append(
                f"- **{c['emoji']} [{c['id']}] {c['name']}** ({c['category']} · {c['district']}) — "
                f"Efek: `{c['effect_summary']}` | {c['description']}"
            )

    if not matched_sections and not matched_cards:
        out_lines.append(
            "Berikut ringkasan cepat aturan inti **EcoNova: Sustainable City Builder**:\n"
            "- **Baseline Awal:** Semua pemain mulai di City Center dengan **5 Koin** dan skor **M=50, E=50, ENV=50, QoL=50**.\n"
            "- **Action Points (3 AP/Round):** Pindah wilayah = **1 AP**, Beli Project/Tech = **1 AP**, Aktifkan Skill / Selesaikan Problem via Tech = **2 AP**, Bayar Problem via Koin = **1 AP**.\n"
            "- **City Center:** Berhenti/tiba di City Center mendapat **+3 Koin** (maks 1x per round).\n"
            "- **Bonus Koin Akhir (R13):** Setiap kelipatan **20 Koin penuh** memberikan **+5 poin ke seluruh 4 aspek**.\n"
            "- **Tie-Breaker Resmi:** `Average Score` $\\rightarrow$ `Jumlah Project Card` $\\rightarrow$ `Jumlah Permanent Tech` $\\rightarrow$ `Sisa Koin`."
        )

    return "\n\n".join(out_lines)
