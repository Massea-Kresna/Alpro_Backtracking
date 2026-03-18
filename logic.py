import random
from typing import Optional

WALL  = 0   # dinding
PATH  = 1   # jalur terbuka
RAT   = 2   # posisi tikus aktif
VISIT = 3   # sudah dikunjungi (jalur solusi sementara)
DEAD  = 4   # jalan buntu (backtrack)
GOAL  = 5   # tujuan

#membuat maze
def generate_maze(rows: int, cols: int,
                  seed: Optional[int] = None) -> list[list[int]]:

    #rows & cols harus ganjil; jika genap otomatis +1.
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1

    rng  = random.Random(seed)
    maze = [[WALL] * cols for _ in range(rows)]

    DIRS = [(0, 2), (0, -2), (2, 0), (-2, 0)]

    #iteratif DFS dengan stack eksplisit
    start = (1, 1)
    maze[1][1] = PATH
    stack = [start]

    while stack:
        r, c = stack[-1]

        #mengumpulkan neighbors yang belum dikunjungi
        neighbors = []
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == WALL:
                neighbors.append((nr, nc, dr, dc))

        if neighbors:
            nr, nc, dr, dc = rng.choice(neighbors)
            #buka dinding di antara
            maze[r + dr // 2][c + dc // 2] = PATH
            maze[nr][nc] = PATH
            stack.append((nr, nc))
        else:
            stack.pop()

    # memastikan start & goal terbuka
    maze[1][1]               = PATH
    maze[rows - 2][cols - 2] = PATH

    return maze

#solve maze(iteratif backtracking)
class MazeSolver:
    #menyelesaikan maze dengan algoritma backtracking secara iteraif
    #setiap perubahan sel disimpan ke `steps` untuk animasi

    def __init__(self, maze: list[list[int]]):
        self.rows  = len(maze)
        self.cols  = len(maze[0])
        self.maze  = [row[:] for row in maze]
        self.steps: list[list[list[int]]] = []
        self.solved = False

        self.start = (1, 1)
        self.goal  = (self.rows - 2, self.cols - 2)

        self.maze[self.start[0]][self.start[1]] = PATH
        self.maze[self.goal[0]][self.goal[1]]   = PATH

    def solve(self) -> bool:
        #stack menyimpan (r, c, move_index) — move_index melacak arah mana yang sudah dicoba dari sel ini, persis seperti yang dilakukan rekursi secara implisit lewat call-stack.
        MOVES = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        board = [
            [WALL if cell == WALL else PATH for cell in row]
            for row in self.maze
        ]

        sr, sc = self.start
        gr, gc = self.goal

        #menandai start
        board[sr][sc] = RAT
        self._snapshot(board)

        #stack: (row, col, next_move_index)
        stack = [(sr, sc, 0)]

        while stack:
            r, c, mi = stack[-1]

            #cek apa udh sampai tujuan
            if (r, c) == (gr, gc):
                board[r][c] = GOAL
                self._snapshot(board)
                self.solved = True
                return True

            #arah selanjutnya yg valid
            found_next = False
            while mi < len(MOVES):
                dr, dc = MOVES[mi]
                nr, nc = r + dr, c + dc
                mi += 1
                if self._valid(nr, nc, board):
                    #update move_index di stack
                    stack[-1] = (r, c, mi)
                    # Masuk ke sel berikutnya
                    board[nr][nc] = (GOAL if (nr, nc) == (gr, gc)
                                     else VISIT)
                    self._snapshot(board)
                    stack.append((nr, nc, 0))
                    found_next = True
                    break

            if not found_next:
                #backtrack dimana tandai sel ini buntu
                stack.pop()
                if (r, c) != (sr, sc):   #jangan tandai start sebagai buntu
                    board[r][c] = DEAD
                    self._snapshot(board)

        self.solved = False
        return False

    def _valid(self, r: int, c: int, board: list[list[int]]) -> bool:
        return (0 <= r < self.rows and
                0 <= c < self.cols and
                board[r][c] in (PATH, GOAL))

    def _snapshot(self, board: list[list[int]]) -> None:
        self.steps.append([row[:] for row in board])