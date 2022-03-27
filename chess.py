from pygame import init, quit, QUIT, MOUSEBUTTONDOWN
from pygame.display import set_mode, flip, set_caption
from pygame.draw import rect
from pygame.event import get
from pygame.font import SysFont
from pygame.image import load
BOTH, WHITE, BLACK, NULL = 2, 1, 0, -1
P, N, B, R, Q, K = range(1, 7) # black pieces
p, n, b, r, q, k = range(7, 13) # white pieces
im = lambda x: load("images/" + x + ".png")
init()
screen = set_mode((480, 480))
set_caption("LSChess")
SPRITES = {P: im('bp'), N: im('bn'), B: im('bb'), R: im('br'), Q: im('bq'), K: im('bk'),
           p: im('wp'), n: im('wn'), b: im('wb'), r: im('wr'), q: im('wq'), k: im('wk')}
move = [-1, -1]
moves = [-1, -1]
class Board:
    def __init__(self) -> None:
        self.state = [R, N, B, Q, K, B, N, R] + [P] * 8 + [0] * 8 * 4 + [p] * 8 + [r, n, b, q, k, b, n, r]
    def __call__(self, pos: int) -> int:
        return self.state[pos]
    def color_at(self, pos: int) -> int:
        if not self(pos): return NULL
        if self(pos) < 7: return BLACK
        if self(pos) > 6: return WHITE
    def is_valid(self, move: list, commiter: bool) -> bool:
        piece = self(move[0])
        if self.color_at(move[0]) != commiter: return False
        if self.color_at(move[1]) == commiter: return False
        if move[0] == move[1]: return False
        disy = move[0] // 8 - move[1] // 8
        disx = move[0] % 8 - move[1] % 8
        diry = disy // abs(disy) if disy else 0 # positive if up
        dirx = disx // abs(disx) if disx else 0 # positive if left
        if piece % 6 == P:
            if commiter == BLACK: disy = -disy
            if disy == 1 and abs(move[0] % 8 - move[1] % 8) == 1 and self.color_at(move[1]) == (not commiter): return True
            if move[0] % 8 != move[1] % 8: return False
            if disy > 2: return False
            if move[0] // 8 != (6 if commiter == WHITE else 1) and disy == 2: return False
            if disy and self.color_at(move[1]) == (not commiter): return False
        if piece % 6 == N:
            if {disx * dirx, disy * diry} != {1, 2}: return False
        if piece % 6 in [B, R, Q]:
            if piece % 6 == B and disy * diry != disx * dirx: return False
            if piece % 6 == R and disy * disx: return False
            if piece % 6 == Q and disy * disx and disy * diry != disx * dirx: return False
            for i in range(1, max(disx * dirx, disy * diry)):
                if self(move[0] - dirx * i - diry * i * 8): return False
        if piece % 6 == k % 6:
            if max(disx * dirx, disy * diry) > 1: return False
        return True
    def commit_move(self, moves: list) -> None:
        disyw = moves[0][0] // 8 - moves[0][1] // 8
        disxw = moves[0][0] % 8 - moves[0][1] % 8
        disyb = moves[1][0] // 8 - moves[1][1] // 8
        disxb = moves[1][0] % 8 - moves[1][1] % 8
        diryb = disyb // abs(disyb) if disyb else 0 # positive if up
        dirxb = disxb // abs(disxb) if disxb else 0 # positive if left
        diryw = disyw // abs(disyw) if disyw else 0 # positive if up
        dirxw = disxw // abs(disxw) if disxw else 0 # positive if left
        pathw = {moves[0][1]}
        pathb = {moves[1][1]}
        if not disyw or not disxw or disyw * diryw == disxw * diryw:
            pathw = pathw.union({moves[0][0] - dirxw * i - diryw * i * 8 for i in range(1, max(disxw * dirxw, disyw * diryw))})
        if not disyb or not disxb or disyb * diryb == disxb * diryb:
            pathb = pathb.union({moves[1][0] - dirxb * i - diryb * i * 8 for i in range(1, max(disxb * dirxb, disyb * diryb))})
        if moves[0][0] == moves[1][1] and moves[1][0] == moves[0][1]:
            self.state[moves[0][0]] = 0
            self.state[moves[1][0]] = 0
            return
        if not pathb & pathw:
            self.state[moves[0][1]], self.state[moves[1][1]] = self(moves[0][0]), self(moves[1][0])
            if self(moves[1][1]) == P and moves[1][1] // 8 == 7: self.state[moves[1][1]] = Q
            if self(moves[0][1]) == p and moves[0][1] // 8 == 0: self.state[moves[0][1]] = q
        if moves[1][1] != moves[0][0] or pathb & pathw:
            self.state[moves[0][0]] = 0
        if moves[1][0] != moves[0][1] or pathb & pathw:
            self.state[moves[1][0]] = 0
    def winner(self) -> int:
        if not set(self.state) & {K, k}: return BOTH
        if K not in self.state: return WHITE
        if k not in self.state: return BLACK
        return NULL
    def draw(self) -> None:
        for i in range(64):
            rect(screen, (128, 128, 128) if (i + i // 8) % 2 else (255, 255, 255), (i % 8 * 60, i // 8 * 60, 60, 60))
        for i in range(64):
            if self(i):
                screen.blit(SPRITES[self(i)], (i % 8 * 60, i // 8 * 60))
        flip()
board = Board()
while board.winner() == NULL:
    board.draw()
    for event in get():
        if event.type == QUIT:
            exit(quit())
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = event.pos
                if pos[0] // 60 < 8 and pos[1] // 60 < 8:
                    move = [move[1], pos[0] // 60 + 8 * (pos[1] // 60)]
                    commiter = board.color_at(move[0])
                    if board.is_valid(move, commiter):
                        moves[not commiter] = move
                        move = [-1, -1]
                        if -1 not in moves:
                            board.commit_move(moves)
                            moves = [-1, -1]
    flip()
board.draw()
screen.blit(SysFont("arial", 60).render("Draw" if board.winner() == BOTH else ("Winner: " + ("Black" if board.winner() == BLACK else "White")), True, (100, 0, 0)), (0, 240))
flip()
while True:
    for event in get():
        if event.type == QUIT:
            exit(quit())