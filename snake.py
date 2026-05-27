#!/usr/bin/env python3
"""
Terminal Snake — a colorful curses snake game.
Controls: arrow keys or WASD | q to quit | r to restart
"""

import curses
import random
import time

# ── Constants ────────────────────────────────────────────────────────────────

TICK_NORMAL = 0.12
TICK_FAST   = 0.07   # speed boost above score 10
TICK_TURBO  = 0.045  # speed boost above score 25

COLORS = {
    "snake_head": (curses.COLOR_GREEN,   curses.COLOR_BLACK),
    "snake_body": (curses.COLOR_CYAN,    curses.COLOR_BLACK),
    "food":       (curses.COLOR_RED,     curses.COLOR_BLACK),
    "bonus":      (curses.COLOR_YELLOW,  curses.COLOR_BLACK),
    "wall":       (curses.COLOR_WHITE,   curses.COLOR_BLACK),
    "score":      (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    "dead":       (curses.COLOR_RED,     curses.COLOR_BLACK),
    "title":      (curses.COLOR_CYAN,    curses.COLOR_BLACK),
}

DIR_MAP = {
    curses.KEY_UP:    (-1,  0),
    curses.KEY_DOWN:  ( 1,  0),
    curses.KEY_LEFT:  ( 0, -1),
    curses.KEY_RIGHT: ( 0,  1),
    ord('w'): (-1,  0),
    ord('s'): ( 1,  0),
    ord('a'): ( 0, -1),
    ord('d'): ( 0,  1),
    ord('W'): (-1,  0),
    ord('S'): ( 1,  0),
    ord('A'): ( 0, -1),
    ord('D'): ( 0,  1),
}

OPPOSITE = {(-1,0):(1,0), (1,0):(-1,0), (0,-1):(0,1), (0,1):(0,-1)}


# ── Colour helpers ────────────────────────────────────────────────────────────

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    pairs = {}
    for idx, (name, (fg, bg)) in enumerate(COLORS.items(), start=1):
        curses.init_pair(idx, fg, bg)
        pairs[name] = curses.color_pair(idx)
    return pairs


# ── Game state ────────────────────────────────────────────────────────────────

class Snake:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        mid_r, mid_c = rows // 2, cols // 2
        self.body = [(mid_r, mid_c), (mid_r, mid_c - 1), (mid_r, mid_c - 2)]
        self.direction = (0, 1)
        self.score = 0
        self.high_score = 0
        self.alive = True
        self.food = self._place_item()
        self.bonus = None
        self.bonus_timer = 0
        self._bonus_countdown = random.randint(8, 15)

    def _occupied(self):
        s = set(self.body)
        if self.food:
            s.add(self.food)
        if self.bonus:
            s.add(self.bonus)
        return s

    def _place_item(self):
        occupied = self._occupied()
        candidates = [
            (r, c)
            for r in range(1, self.rows - 1)
            for c in range(1, self.cols - 1)
            if (r, c) not in occupied
        ]
        return random.choice(candidates) if candidates else None

    def change_direction(self, new_dir):
        if new_dir != OPPOSITE.get(self.direction):
            self.direction = new_dir

    def step(self):
        if not self.alive:
            return
        dr, dc = self.direction
        head = self.body[0]
        new_head = (head[0] + dr, head[1] + dc)

        # Wall collision
        if not (1 <= new_head[0] < self.rows - 1 and 1 <= new_head[1] < self.cols - 1):
            self.alive = False
            return

        # Self collision
        if new_head in self.body:
            self.alive = False
            return

        self.body.insert(0, new_head)

        # Eat food
        if new_head == self.food:
            self.score += 1
            self.food = self._place_item()
            self._bonus_countdown -= 1
            if self._bonus_countdown <= 0:
                self.bonus = self._place_item()
                self.bonus_timer = 20
                self._bonus_countdown = random.randint(8, 15)
        elif new_head == self.bonus:
            self.score += 3
            self.bonus = None
            self.bonus_timer = 0
        else:
            self.body.pop()

        # Bonus expiry
        if self.bonus:
            self.bonus_timer -= 1
            if self.bonus_timer <= 0:
                self.bonus = None

        self.high_score = max(self.high_score, self.score)

    def tick_rate(self):
        if self.score >= 25:
            return TICK_TURBO
        if self.score >= 10:
            return TICK_FAST
        return TICK_NORMAL


# ── Rendering ─────────────────────────────────────────────────────────────────

def draw_border(win, pairs):
    rows, cols = win.getmaxyx()
    attr = pairs["wall"] | curses.A_BOLD
    try:
        win.addch(0, 0, curses.ACS_ULCORNER, attr)
        win.addch(0, cols - 1, curses.ACS_URCORNER, attr)
        win.addch(rows - 1, 0, curses.ACS_LLCORNER, attr)
        # bottom-right corner — avoid writing to last cell (raises exception)
        win.insch(rows - 1, cols - 1, curses.ACS_LRCORNER, attr)
    except curses.error:
        pass
    for c in range(1, cols - 1):
        try:
            win.addch(0, c, curses.ACS_HLINE, attr)
            win.addch(rows - 1, c, curses.ACS_HLINE, attr)
        except curses.error:
            pass
    for r in range(1, rows - 1):
        try:
            win.addch(r, 0, curses.ACS_VLINE, attr)
            win.addch(r, cols - 1, curses.ACS_VLINE, attr)
        except curses.error:
            pass


def draw_game(win, snake, pairs):
    win.erase()
    draw_border(win, pairs)
    rows, cols = win.getmaxyx()

    # Score bar
    speed = ["normal", "fast", "TURBO"][0 if snake.score < 10 else 1 if snake.score < 25 else 2]
    score_str = f"  Score: {snake.score}  High: {snake.high_score}  Speed: {speed}  "
    controls  = " ↑↓←→/WASD · q=quit · r=restart "
    try:
        win.addstr(0, 2, score_str, pairs["score"] | curses.A_BOLD)
        win.addstr(rows - 1, max(2, cols - len(controls) - 2), controls, pairs["wall"])
    except curses.error:
        pass

    # Food
    if snake.food:
        try:
            win.addch(snake.food[0], snake.food[1], "●", pairs["food"] | curses.A_BOLD)
        except curses.error:
            pass

    # Bonus
    if snake.bonus:
        flash = pairs["bonus"] | (curses.A_BLINK if snake.bonus_timer < 8 else curses.A_BOLD)
        try:
            win.addch(snake.bonus[0], snake.bonus[1], "★", flash)
        except curses.error:
            pass

    # Snake body (draw tail→neck first, head last)
    for seg in reversed(snake.body[1:]):
        try:
            win.addch(seg[0], seg[1], "■", pairs["snake_body"])
        except curses.error:
            pass
    # Head
    try:
        win.addch(snake.body[0][0], snake.body[0][1], "▶", pairs["snake_head"] | curses.A_BOLD)
    except curses.error:
        pass

    win.refresh()


def draw_dead(win, snake, pairs):
    rows, cols = win.getmaxyx()
    msg1 = "  GAME OVER  "
    msg2 = f"  Score: {snake.score}  High: {snake.high_score}  "
    msg3 = "  r = restart   q = quit  "
    cy = rows // 2
    cx = cols // 2
    try:
        win.addstr(cy - 1, cx - len(msg1) // 2, msg1, pairs["dead"] | curses.A_BOLD | curses.A_REVERSE)
        win.addstr(cy,     cx - len(msg2) // 2, msg2, pairs["score"] | curses.A_BOLD)
        win.addstr(cy + 1, cx - len(msg3) // 2, msg3, pairs["wall"])
    except curses.error:
        pass
    win.refresh()


def draw_welcome(win, pairs):
    rows, cols = win.getmaxyx()
    lines = [
        ("  TERMINAL SNAKE  ", "title"),
        ("", "title"),
        ("  ↑↓←→ or WASD to move  ", "wall"),
        ("  Eat ● for +1 point    ", "food"),
        ("  Eat ★ for +3 points   ", "bonus"),
        ("  Speed increases with score  ", "score"),
        ("", "wall"),
        ("  Press any key to start  ", "snake_head"),
    ]
    cy = rows // 2 - len(lines) // 2
    for i, (text, color) in enumerate(lines):
        try:
            win.addstr(cy + i, cols // 2 - len(text) // 2, text,
                       pairs[color] | curses.A_BOLD)
        except curses.error:
            pass
    win.refresh()


# ── Main loop ─────────────────────────────────────────────────────────────────

def game_loop(stdscr):
    pairs = init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    rows, cols = stdscr.getmaxyx()
    if rows < 10 or cols < 20:
        stdscr.addstr(0, 0, "Terminal too small! Need at least 20x10.")
        stdscr.refresh()
        time.sleep(3)
        return

    # Welcome screen
    draw_border(stdscr, pairs)
    draw_welcome(stdscr, pairs)
    stdscr.nodelay(False)
    key = stdscr.getch()
    if key in (ord('q'), ord('Q')):
        return
    stdscr.nodelay(True)

    high_score = 0

    while True:
        rows, cols = stdscr.getmaxyx()
        snake = Snake(rows, cols)
        snake.high_score = high_score
        last_tick = time.time()

        while snake.alive:
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                return
            if key in DIR_MAP:
                snake.change_direction(DIR_MAP[key])

            now = time.time()
            if now - last_tick >= snake.tick_rate():
                snake.step()
                last_tick = now
                draw_game(stdscr, snake, pairs)

            time.sleep(0.01)

        # Death screen
        draw_dead(stdscr, snake, pairs)
        high_score = snake.high_score
        stdscr.nodelay(False)
        while True:
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                return
            if key in (ord('r'), ord('R')):
                break
        stdscr.nodelay(True)


def main():
    curses.wrapper(game_loop)


if __name__ == "__main__":
    main()
