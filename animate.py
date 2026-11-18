#!/usr/bin/env python3
"""Moving ASCII art in the terminal.

Usage:
    python animate.py            # starfield (default)
    python animate.py matrix     # falling "digital rain"
    python animate.py wave       # rolling sine-wave ocean
    python animate.py bounce     # bouncing ball

Press Ctrl+C to quit.
"""

import math
import random
import shutil
import sys
import time

FPS = 30

# ANSI escape codes (work on macOS, Linux and Windows 10+ terminals)
CLEAR = "\033[2J"
HOME = "\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
GREEN = "\033[32m"
BRIGHT_GREEN = "\033[92m"
CYAN = "\033[36m"
RESET = "\033[0m"


def term_size():
    cols, rows = shutil.get_terminal_size((80, 24))
    return cols, rows - 1  # leave one line so the screen doesn't scroll


def blank(cols, rows):
    return [[" "] * cols for _ in range(rows)]


def render(grid):
    return HOME + "\n".join("".join(row) for row in grid)


# ---------------------------------------------------------------- animations

def starfield():
    """Stars fly toward you from the center of the screen."""
    stars = [[random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0.1, 1)]
             for _ in range(200)]
    while True:
        cols, rows = term_size()
        grid = blank(cols, rows)
        for s in stars:
            s[2] -= 0.02  # move closer
            if s[2] <= 0.01:
                s[:] = [random.uniform(-1, 1), random.uniform(-1, 1), 1]
            x = int(cols / 2 + s[0] / s[2] * cols / 2)
            y = int(rows / 2 + s[1] / s[2] * rows / 2)
            if 0 <= x < cols and 0 <= y < rows:
                grid[y][x] = "@" if s[2] < 0.3 else "*" if s[2] < 0.6 else "."
        yield render(grid)


def matrix():
    """Columns of random characters raining down."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789$+-*/=%\"'#&_(),.;:?!|{}<>[]^~"
    drops = {}
    while True:
        cols, rows = term_size()
        grid = blank(cols, rows)
        for x in range(cols):
            if x not in drops or drops[x] - 15 > rows:
                drops[x] = random.randint(-rows, 0)
            drops[x] += 1
            head = drops[x]
            for tail in range(15):  # trail length
                y = head - tail
                if 0 <= y < rows:
                    color = BRIGHT_GREEN if tail == 0 else GREEN
                    grid[y][x] = color + random.choice(chars) + RESET
        yield render(grid)


def wave():
    """A rolling ocean made of sine waves."""
    t = 0.0
    shades = " .-~=*#"
    while True:
        cols, rows = term_size()
        grid = blank(cols, rows)
        for x in range(cols):
            h = (math.sin(x * 0.15 + t) + math.sin(x * 0.07 - t * 0.6)) / 2
            surface = int(rows / 2 + h * rows / 4)
            for y in range(max(surface, 0), rows):
                depth = min(len(shades) - 1, (y - surface) // 2 + 1)
                grid[y][x] = CYAN + shades[depth] + RESET
        t += 0.15
        yield render(grid)


def bounce():
    """A ball bouncing off the edges, leaving a fading trail."""
    x, y, dx, dy = 5.0, 3.0, 1.2, 0.6
    trail = []
    while True:
        cols, rows = term_size()
        x += dx
        y += dy
        if x <= 0 or x >= cols - 1:
            dx = -dx
            x = max(0, min(x, cols - 1))
        if y <= 0 or y >= rows - 1:
            dy = -dy
            y = max(0, min(y, rows - 1))
        trail = (trail + [(int(x), int(y))])[-10:]
        grid = blank(cols, rows)
        for i, (tx, ty) in enumerate(trail):
            if 0 <= tx < cols and 0 <= ty < rows:
                grid[ty][tx] = "O" if i == len(trail) - 1 else ".oo"[i * 3 // len(trail)]
        yield render(grid)


ANIMATIONS = {"starfield": starfield, "matrix": matrix, "wave": wave, "bounce": bounce}


# ---------------------------------------------------------------- main loop

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "starfield"
    if name not in ANIMATIONS:
        print(f"Unknown animation '{name}'. Choose from: {', '.join(ANIMATIONS)}")
        sys.exit(1)

    sys.stdout.write(CLEAR + HIDE_CURSOR)
    try:
        for frame in ANIMATIONS[name]():
            sys.stdout.write(frame)
            sys.stdout.flush()
            time.sleep(1 / FPS)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + SHOW_CURSOR + CLEAR + HOME)


if __name__ == "__main__":
    main()
