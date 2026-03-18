# Rat in a Maze Backtracking Visualizer

Visualisasi interaktif algoritma **Rat in a Maze** menggunakan Python dan Tkinter. Menampilkan proses pembuatan labirin dan penyelesaiannya secara animasi langkah demi langkah.

---

## Tampilan

| State | Warna |
|---|---|
| ⬛ Dinding | Hitam |
| ⬜ Jalur terbuka | Putih |
| 🟧 Posisi tikus | Oranye |
| 🟦 Dikunjungi | Biru muda |
| 🟥 Jalan buntu | Merah |
| 🟩 Tujuan | Hijau |

---

## Algoritma

### Pembuatan Maze — Iterative DFS
Labirin dibuat menggunakan **Iterative Depth-First Search** dengan stack eksplisit. Semua sel dimulai sebagai dinding, lalu algoritma "mengukir" jalur secara acak hingga seluruh area terhubung.

```
1. Mulai dari sel (1,1), tandai sebagai PATH, push ke stack
2. Selama stack tidak kosong:
   a. Lihat sel teratas stack
   b. Cari tetangga (jarak 2 sel) yang masih WALL
   c. Jika ada → pilih acak, buka dinding di antaranya, push tetangga
   d. Jika tidak ada → pop stack (backtrack)
3. Selesai
```

### Penyelesaian Maze — Iterative Backtracking
Solver menggunakan **Iterative Backtracking** dengan stack yang menyimpan `(baris, kolom, indeks_arah)`. Indeks arah melacak arah mana yang sudah dicoba dari setiap sel, meniru persis perilaku rekursi tanpa risiko stack overflow.

```
1. Push (start, arah=0) ke stack
2. Selama stack tidak kosong:
   a. Ambil elemen teratas (r, c, mi)
   b. Jika (r,c) == goal → selesai, solusi ditemukan
   c. Coba arah ke-mi: jika valid → masuk ke sel baru, push (nr,nc,0)
   d. Jika semua arah dicoba → pop stack, tandai sel sebagai DEAD (buntu)
3. Jika stack kosong tanpa menemukan goal → tidak ada solusi
```

> Semua langkah disimpan sebagai snapshot untuk diputar sebagai animasi di GUI.

---

## Struktur File

```
├── main.py              #titik masuk aplikasi
├── logic.py        #logika algoritma (tanpa dependensi GUI)
├── visualization.py   #tampilan GUI dengan Tkinter
└── README.md
```

Pemisahan file mengikuti prinsip **Separation of Concerns**:
- `logic.py` tidak mengimport Tkinter → bisa diuji atau dijalankan tanpa GUI
- `visualization.py` hanya mengonsumsi output berupa array 2D → visualizer bisa diganti tanpa menyentuh logika
- Dependensi berjalan satu arah: `main → visualization → logic`

---

## Cara Menjalankan

**Persyaratan:**
- Python 3.10+
- `tkinter` (sudah termasuk dalam instalasi Python bawaan)
- Tidak memerlukan library pihak ketiga

**Jalankan:**
```bash
python main.py
```

---

## Fitur GUI

- **Animasi pembuatan maze** — jalur terbuka satu per satu
- **Animasi penyelesaian** — setiap langkah backtracking ditampilkan secara real-time
- **Canvas scrollable** — scroll vertikal/horizontal dan drag-to-pan
- **Zoom in/out** — ukuran sel 3px hingga 48px per sel
- **Slider kecepatan** — atur kecepatan animasi secara dinamis
- **Ukuran maze fleksibel** — dari 7×7 hingga 101×101

---

## Kompleksitas

| | Generate | Solve |
|---|---|---|
| Waktu | O(n) | O(n) |
| Ruang | O(n) | O(n) |

dengan `n` = jumlah total sel (rows × cols).
