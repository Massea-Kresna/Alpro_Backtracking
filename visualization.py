import tkinter as tk
from tkinter import ttk
from logic import (
    WALL, PATH, RAT, VISIT, DEAD, GOAL,
    generate_maze, MazeSolver,
)

#palet warna
C = {
    WALL:  "#212121",
    PATH:  "#f5f5f5",
    RAT:   "#ff9800",
    VISIT: "#29b6f6",
    DEAD:  "#ef5350",
    GOAL:  "#66bb6a",
}

BG       = "#1e1e1e"
TOOLBAR  = "#252526"
STATUSBG = "#007acc"
FG       = "#d4d4d4"
FG_DIM   = "#858585"
BTN_H    = "#2d2d2d"


def _auto_cell(rows: int, cols: int) -> int:
    cs_r = max(4, min(40, 700 // rows))
    cs_c = max(4, min(40, 900 // cols))
    return min(cs_r, cs_c)


#tombol
class _Btn(tk.Label):
    def __init__(self, parent, text, command, fg=FG, bg=TOOLBAR,
                 padx=10, pady=4, **kw):
        super().__init__(parent, text=text, fg=fg, bg=bg,
                         padx=padx, pady=pady, cursor="hand2",
                         font=("Segoe UI", 9), **kw)
        self._cmd = command
        self._fg  = fg
        self._bg  = bg
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>",    lambda _: self._hover(True))
        self.bind("<Leave>",    lambda _: self._hover(False))

    def _hover(self, on):
        if str(self.cget("state")) != "disabled":
            self.config(bg=BTN_H if on else self._bg)

    def _click(self, _):
        if str(self.cget("state")) != "disabled":
            self._cmd()

    def enable(self):
        self.config(state="normal", fg=self._fg, bg=self._bg)

    def disable(self):
        self.config(state="disabled", fg=FG_DIM)

class MazeVisualizer:

    def __init__(self, root: tk.Tk, rows: int = 15, cols: int = 21):
        self.root = root
        self.root.title("Rat in a Maze Backtracking")
        self.root.configure(bg=BG)
        self.root.minsize(620, 440)
        self.root.resizable(True, True)

        self.rows      = rows if rows % 2 == 1 else rows + 1
        self.cols      = cols if cols % 2 == 1 else cols + 1
        self.cell_size = _auto_cell(self.rows, self.cols)
        self.delay_ms  = 40
        self.anim_id   = None
        self.step_idx  = 0
        self.phase     = "idle"
        self.maze      = None
        self.solver    = None

        self._build_ui()
        self._redraw_blank()

    #layout utama
    def _build_ui(self):
        self._build_toolbar()
        self._build_canvas_area()
        self._build_statusbar()

    #toolbar
    def _build_toolbar(self):
        tb = tk.Frame(self.root, bg=TOOLBAR, height=38)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)

        #title
        tk.Label(tb, text="Massea Kresna_Alpro C",
                 bg=TOOLBAR, fg=FG,
                 font=("Segoe UI", 10, "bold"),
                 padx=10).pack(side="left")

        _vsep(tb)

        #input ukuran maze
        tk.Label(tb, text="Baris:", bg=TOOLBAR, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(side="left", padx=(8, 2))
        self.row_var = tk.IntVar(value=self.rows)
        tk.Spinbox(tb, from_=7, to=101, increment=2,
                   textvariable=self.row_var, width=4,
                   bg=TOOLBAR, fg=FG, relief="flat",
                   buttonbackground="#3c3c3c",
                   insertbackground=FG,
                   font=("Consolas", 9)).pack(side="left")

        tk.Label(tb, text="Kolom:", bg=TOOLBAR, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(side="left", padx=(6, 2))
        self.col_var = tk.IntVar(value=self.cols)
        tk.Spinbox(tb, from_=7, to=101, increment=2,
                   textvariable=self.col_var, width=4,
                   bg=TOOLBAR, fg=FG, relief="flat",
                   buttonbackground="#3c3c3c",
                   insertbackground=FG,
                   font=("Consolas", 9)).pack(side="left")

        _vsep(tb)

        #tombol action
        self.btn_gen = _Btn(tb, "⊞  Buat Maze",
                            self.start_generate, fg="#4ec9b0")
        self.btn_gen.pack(side="left", padx=2)

        self.btn_sol = _Btn(tb, "▶  Solve",
                            self.start_solve, fg="#569cd6")
        self.btn_sol.pack(side="left", padx=2)
        self.btn_sol.disable()

        self.btn_rst = _Btn(tb, "↺  Reset",
                            self.reset, fg="#f44747")
        self.btn_rst.pack(side="left", padx=2)

        _vsep(tb)

        #slidebar keceparan
        tk.Label(tb, text="Kecepatan:", bg=TOOLBAR, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(side="left", padx=(6, 2))
        self.speed_var = tk.IntVar(value=60)
        tk.Scale(tb, from_=1, to=100, orient="horizontal",
                 variable=self.speed_var, length=85,
                 bg=TOOLBAR, fg=FG, troughcolor="#3c3c3c",
                 highlightthickness=0, showvalue=False,
                 command=self._on_speed).pack(side="left")

        _vsep(tb)

        #zoom
        tk.Label(tb, text="Zoom:", bg=TOOLBAR, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(side="left", padx=(6, 2))
        _Btn(tb, "+", self._zoom_in,  padx=7).pack(side="left")
        _Btn(tb, "−", self._zoom_out, padx=7).pack(side="left")
        self.zoom_lbl = tk.Label(tb, text=f"{self.cell_size}px",
                                 bg=TOOLBAR, fg=FG_DIM,
                                 font=("Consolas", 8), width=5)
        self.zoom_lbl.pack(side="left")

        _vsep(tb)

        #legend
        for code, label in [(PATH, "Jalur"), (RAT, "Tikus"),
                            (VISIT, "Dikunjungi"), (DEAD, "Buntu"),
                            (GOAL, "Tujuan")]:
            tk.Frame(tb, bg=C[code], width=12, height=12).pack(
                side="left", pady=12, padx=(4, 1))
            tk.Label(tb, text=label, bg=TOOLBAR, fg=FG_DIM,
                     font=("Segoe UI", 7)).pack(side="left", padx=(0, 3))

    #canvas n scrollbar
    def _build_canvas_area(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True)

        vbar = ttk.Scrollbar(frame, orient="vertical")
        hbar = ttk.Scrollbar(frame, orient="horizontal")
        vbar.pack(side="right",  fill="y")
        hbar.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(
            frame, bg=C[WALL], highlightthickness=0,
            yscrollcommand=vbar.set,
            xscrollcommand=hbar.set,
        )
        self.canvas.pack(fill="both", expand=True)

        vbar.config(command=self.canvas.yview)
        hbar.config(command=self.canvas.xview)

        #scroll mouse wheel
        self.canvas.bind("<MouseWheel>",
                         lambda e: self.canvas.yview_scroll(
                             int(-1 * e.delta / 120), "units"))
        self.canvas.bind("<Shift-MouseWheel>",
                         lambda e: self.canvas.xview_scroll(
                             int(-1 * e.delta / 120), "units"))

        self.canvas.bind("<Button-4>",
                         lambda _: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>",
                         lambda _: self.canvas.yview_scroll(1, "units"))

        #drag to pan
        self.canvas.bind("<ButtonPress-1>",
                         lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>",
                         lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

    #status bar
    def _build_statusbar(self):
        sb = tk.Frame(self.root, bg=STATUSBG, height=22)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)

        self.status_var = tk.StringVar(
            value="Siap - Atur ukuran lalu klik ⊞ Buat Maze")
        self.step_var   = tk.StringVar(value="")

        tk.Label(sb, textvariable=self.status_var,
                 bg=STATUSBG, fg="white",
                 font=("Segoe UI", 8), padx=8).pack(side="left")
        tk.Label(sb, textvariable=self.step_var,
                 bg=STATUSBG, fg="#cce5ff",
                 font=("Consolas", 8), padx=8).pack(side="right")

    #draw sel
    def _draw_cell(self, r: int, c: int, code: int):
        cs    = self.cell_size
        x, y  = c * cs, r * cs
        tag   = f"k{r}_{c}"
        color = C.get(code, C[WALL])

        self.canvas.delete(tag)
        self.canvas.create_rectangle(
            x, y, x + cs, y + cs,
            fill=color,
            outline=C[WALL] if cs >= 6 else color,
            width=1 if cs >= 6 else 0,
            tags=tag,
        )

    def _redraw_blank(self):
        cs = self.cell_size
        w, h = self.cols * cs, self.rows * cs
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, w, h))
        self.canvas.create_rectangle(
            0, 0, w, h, fill=C[WALL], outline="", tags="bg")

    def _draw_full(self, board):
        for r in range(self.rows):
            for c in range(self.cols):
                if board[r][c] != WALL:
                    self._draw_cell(r, c, board[r][c])

    def _update_scrollregion(self):
        cs = self.cell_size
        self.canvas.config(
            scrollregion=(0, 0, self.cols * cs, self.rows * cs))

    #zoom
    def _zoom_in(self):
        self.cell_size = min(48, self.cell_size + 2)
        self._apply_zoom()

    def _zoom_out(self):
        self.cell_size = max(3, self.cell_size - 2)
        self._apply_zoom()

    def _apply_zoom(self):
        self.zoom_lbl.config(text=f"{self.cell_size}px")
        if self.maze is None:
            self._redraw_blank()
            return
        board = (self.solver.steps[self.step_idx - 1]
                 if self.solver and self.step_idx > 0
                 else self.maze)
        self._redraw_blank()
        self._draw_full(board)
        self._update_scrollregion()

    #kecepatan
    def _on_speed(self, _=None):
        v = self.speed_var.get()
        self.delay_ms = max(1, 110 - int(v * 1.08))

    #generate maze
    def start_generate(self):
        if self.anim_id:
            self.root.after_cancel(self.anim_id)

        r = self.row_var.get()
        c = self.col_var.get()
        self.rows = r if r % 2 == 1 else r + 1
        self.cols = c if c % 2 == 1 else c + 1
        self.cell_size = _auto_cell(self.rows, self.cols)
        self.zoom_lbl.config(text=f"{self.cell_size}px")

        self.maze   = None
        self.solver = None
        self.step_idx = 0

        self._redraw_blank()
        self.btn_gen.disable()
        self.btn_sol.disable()
        self.phase = "generating"
        self.status_var.set(
            f"Membuat maze {self.rows}×{self.cols}...")

        self.maze = generate_maze(self.rows, self.cols)

        self._gen_queue = [
            (rr, cc)
            for rr in range(self.rows)
            for cc in range(self.cols)
            if self.maze[rr][cc] == PATH
        ]
        self._gen_idx = 0
        self._animate_generate()

    def _animate_generate(self):
        total = len(self._gen_queue)
        batch = max(1, total // 60)
        for _ in range(batch):
            if self._gen_idx >= total:
                self._gen_done()
                return
            r, c = self._gen_queue[self._gen_idx]
            self._draw_cell(r, c, PATH)
            self._gen_idx += 1

        pct = int(self._gen_idx / total * 100)
        self.status_var.set(f"Membuat maze...{pct}%")
        self.step_var.set(f"Sel: {self._gen_idx}/{total}")
        self.anim_id = self.root.after(
            max(1, self.delay_ms // 3), self._animate_generate)

    def _gen_done(self):
        self._draw_cell(1, 1, RAT)
        self._draw_cell(self.rows - 2, self.cols - 2, GOAL)
        self._update_scrollregion()
        self.phase = "idle"

        total = self.rows * self.cols
        walls = sum(self.maze[r][c] == WALL
                    for r in range(self.rows) for c in range(self.cols))
        self.status_var.set(
            f"Maze {self.rows}×{self.cols} siap - "
            f"Jalur: {total - walls}   Dinding: {walls}")
        self.step_var.set("")
        self.btn_gen.enable()
        self.btn_sol.enable()

    #solve
    def start_solve(self):
        if self.maze is None:
            return
        if self.anim_id:
            self.root.after_cancel(self.anim_id)

        self.btn_gen.disable()
        self.btn_sol.disable()
        self.phase = "solving"
        self.status_var.set("Menyelesaikan maze...")

        self.solver   = MazeSolver(self.maze)
        solved        = self.solver.solve()
        self.step_idx = 0
        total         = len(self.solver.steps)

        self.status_var.set(
            "Mencari solusi"
            if solved else "Tidak ada solusi!")
        self._animate_solve()

    def _animate_solve(self):
        steps = self.solver.steps
        if self.step_idx >= len(steps):
            self._solve_done()
            return

        board = steps[self.step_idx]
        if self.step_idx == 0:
            self._draw_full(board)
        else:
            prev = steps[self.step_idx - 1]
            for r in range(self.rows):
                for c in range(self.cols):
                    if board[r][c] != prev[r][c]:
                        self._draw_cell(r, c, board[r][c])

        self.step_idx += 1
        self.step_var.set(f"{self.step_idx} / {len(steps)}")
        self.anim_id = self.root.after(self.delay_ms, self._animate_solve)

    def _solve_done(self):
        self.phase = "done"
        if self.solver.solved:
            last = self.solver.steps[-1]
            path_len = sum(last[r][c] in (VISIT, GOAL, RAT)
                           for r in range(self.rows)
                           for c in range(self.cols))
            dead_len = sum(last[r][c] == DEAD
                           for r in range(self.rows)
                           for c in range(self.cols))
            self.status_var.set(
                f"✔ Selesai - Solusi: {path_len} sel  |  "
                f"Jalan buntu: {dead_len} sel")
        else:
            self.status_var.set("✘ Tidak ada solusi")
        self.step_var.set("")
        self.btn_gen.enable()

    # ── Reset ─────────────────────────────────────────────────────────────────
    def reset(self):
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
            self.anim_id = None

        self.maze     = None
        self.solver   = None
        self.step_idx = 0
        self.phase    = "idle"

        self._redraw_blank()
        self.status_var.set(
            "Siap - Atur ukuran lalu klik ⊞ Buat Maze")
        self.step_var.set("")
        self.btn_gen.enable()
        self.btn_sol.disable()


#separator
def _vsep(parent):
    tk.Frame(parent, bg="#3c3c3c", width=1).pack(
        side="left", fill="y", pady=6, padx=3)