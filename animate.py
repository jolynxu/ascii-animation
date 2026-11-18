#!/usr/bin/env python3
"""moving ASCII art in the terminal

Usage:
    python animate.py            # starfield (default)
    python animate.py matrix     # falling "digital rain"
    python animate.py wave       # rolling sine-wave ocean
    python animate.py bounce     # bouncing ball
    python animate.py jellyfish  # moving jellyfish
    python animate.py space      # ringed planet, moon and shooting stars
Press Ctrl+C to quit
"""

import math
import random
import shutil
import sys
import time

FPS = 30

# ANSI escape codes 
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
    """stars fly toward you from the center of the screen"""
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
    """columns of random characters raining down"""
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
    """a rolling ocean made of sine waves"""
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
    """a ball bouncing off the edges, leaving a fading trail"""
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

# 256-color ANSI codes, in a loop: navy -> light blue -> purple -> magenta -> navy
JELLY_COLORS = [17, 18, 19, 20, 26, 32, 38, 74, 117, 153, 147, 141, 135, 99,
                93, 129, 165, 201, 199, 163, 127, 91, 55, 54]
 
 
def jellyfish():
    """a pulsing jellyfish drifting, cycling through colors"""
    t = 0.0
    # specks of "marine snow" floating in the background (stored as 0-1 coords)
    snow = [[random.random(), random.random(), random.uniform(0.0005, 0.002)]
            for _ in range(90)]
 
    while True:
        cols, rows = term_size()
        grid = blank(cols, rows)
 
        def put(x, y, ch, color_code):
            x, y = int(round(x)), int(round(y))
            if 0 <= x < cols and 0 <= y < rows:
                grid[y][x] = f"\033[38;5;{color_code}m{ch}"
 
        def color(phase):
            return JELLY_COLORS[int(phase) % len(JELLY_COLORS)]
 
        # --- background: dim specks drifting slowly upward
        for s in snow:
            s[1] -= s[2]
            if s[1] < 0:
                s[0], s[1] = random.random(), 1.0
            sway = math.sin(t + s[0] * 10) * 0.005
            put((s[0] + sway) * cols, s[1] * rows, ".", random.choice((17, 18, 24)))
 
        # --- size and position (scales with the terminal)
        pulse = math.sin(t * 1.5)                # >0 = bell squeezes
        base_ry = max(3, rows // 6)              # bell height
        base_rx = base_ry * 2.4                  # characters are tall, so widen
        rx = base_rx * (1 - 0.12 * pulse)
        ry = base_ry * (1 + 0.08 * pulse)
        cx = cols / 2 + math.sin(t * 0.13) * cols * 0.25
        top = rows * 0.15 + math.sin(t * 0.25) * rows * 0.08 - pulse * 0.8
        shift = t * 3                            # how fast the colors flow
 
        # --- bell (dome): shaded darker inside, brighter at the edge
        for dy in range(int(ry) + 1):
            for dx in range(-int(rx), int(rx) + 1):
                d = math.hypot(dx / rx, (ry - dy) / ry)
                if d > 1:
                    continue
                ch = "@" if d > 0.88 else "O" if d > 0.7 else "o" if d > 0.45 else ":"
                put(cx + dx, top + dy, ch, color(shift + dy * 0.8 + abs(dx) * 0.15))
 
        # --- frilly rim under the bell
        rim = top + ry + 1
        for dx in range(-int(rx), int(rx) + 1):
            ch = "~" if (dx + int(t * 6)) % 2 else "'"
            put(cx + dx, rim, ch, color(shift + ry * 0.8 + 1))
 
        # --- long trailing tentacles
        n_tentacles = 8
        for k in range(n_tentacles):
            tx = cx - rx * 0.8 + k * (rx * 1.6 / (n_tentacles - 1))
            length = int(rows * 0.45 * (0.7 + 0.3 * math.sin(k * 2.3) ** 2))
            prev_x = tx
            for i in range(1, length):
                x = tx + math.sin(t * 2.2 - i * 0.35 + k * 1.3) * (0.5 + i * 0.12)
                step = x - prev_x
                if i > length * 0.75:
                    ch = "." if i % 2 else ":"   # faded tips
                elif step > 0.35:
                    ch = "\\"
                elif step < -0.35:
                    ch = "/"
                else:
                    ch = "|"
                put(x, rim + i, ch, color(shift + (ry + i) * 0.8))
                prev_x = x
 
        # --- two thicker, curly oral arms in the middle
        for side in (-1, 1):
            ax = cx + side * rx * 0.2
            for i in range(1, int(rows * 0.25)):
                x = ax + math.sin(t * 1.6 - i * 0.5 + side) * (0.8 + i * 0.08)
                put(x, rim + i, "}" if side < 0 else "{", color(shift + 4 + (ry + i) * 0.8))
                put(x + side, rim + i, ")" if side < 0 else "(", color(shift + 5 + (ry + i) * 0.8))
 
        t += 0.05
        yield render(grid)
 
 
def space():
    """a spinning ringed planet, an orbiting moon, twinkling and shooting stars"""
    t = 0.0
    # background stars: x, y (0-1), twinkle speed, twinkle phase
    stars = [[random.random(), random.random(), random.uniform(1, 4), random.uniform(0, 6.3)]
             for _ in range(150)]
    shooting = []            # each: [x, y, dx, dy, frames_left]
    ramp = ".:-=+*#%@"       # dark -> bright shading characters
    light = (-0.6, -0.5, 0.62)  # light comes from the upper left
    aspect = 2.2             # terminal characters are about twice as tall as wide

    while True:
        cols, rows = term_size()
        grid = blank(cols, rows)

        def put(x, y, ch, color_code):
            x, y = int(round(x)), int(round(y))
            if 0 <= x < cols and 0 <= y < rows:
                grid[y][x] = f"\033[38;5;{color_code}m{ch}"

        def sphere(cx, cy, r, palette, spin):
            """Draw a shaded ball. palette(lat, lon, brightness) -> color code."""
            for y in range(int(cy - r) - 1, int(cy + r) + 2):
                for x in range(int(cx - r * aspect) - 1, int(cx + r * aspect) + 2):
                    px, py = (x - cx) / (r * aspect), (y - cy) / r
                    d2 = px * px + py * py
                    if d2 > 1:
                        continue
                    pz = math.sqrt(1 - d2)
                    b = max(0.0, px * light[0] + py * light[1] + pz * light[2])
                    ch = ramp[min(len(ramp) - 1, int(b * len(ramp)))]
                    lon = math.atan2(px, pz) + spin
                    put(x, y, ch, palette(py, lon, b))

        # --- twinkling stars
        for s in stars:
            tw = math.sin(t * s[2] + s[3])
            ch = "*" if tw > 0.9 else "+" if tw > 0.5 else "."
            put(s[0] * cols, s[1] * rows, ch, 231 if tw > 0.5 else random.choice((240, 244, 153)))

        # --- shooting stars: spawn now and then, streak diagonally with a fading tail
        if random.random() < 0.02:
            shooting.append([random.uniform(0, cols * 0.6), random.uniform(0, rows * 0.3),
                             random.uniform(1.5, 2.5), random.uniform(0.4, 0.8), 40])
        for s in shooting:
            s[0] += s[2]
            s[1] += s[3]
            s[4] -= 1
            for k, c in enumerate((231, 195, 153, 111, 67, 61)):
                put(s[0] - s[2] * k * 0.6, s[1] - s[3] * k * 0.6, "*" if k == 0 else ".", c)
        shooting = [s for s in shooting if s[4] > 0]

        # --- planet size and position (scales with the terminal)
        R = max(3.0, min(rows * 0.22, cols / 11))
        cx, cy = cols / 2, rows / 2
        tilt = 0.35                       # how flat the ring looks

        def ring(front):
            """Draw the half of the ring in front of (or behind) the planet."""
            for y in range(int(cy - 2.2 * R * tilt) - 1, int(cy + 2.2 * R * tilt) + 2):
                for x in range(int(cx - 2.2 * R * aspect), int(cx + 2.2 * R * aspect) + 1):
                    u, v = (x - cx) / aspect, (y - cy) / tilt
                    r = math.hypot(u, v) / R
                    if not 1.35 < r < 2.1 or 1.74 < r < 1.82 or (v > 0) != front:
                        continue  # outside ring, in the gap, or the other half
                    a = math.atan2(v, u)
                    if int(a * 20 - t * 4 + r * 7) % 9 == 0:
                        ch = "."  # ring particles drifting around
                    else:
                        ch = ":" if r < 1.55 else "=" if r < 1.74 else "-"
                    put(x, y, ch, 223 if r < 1.55 else 180 if r < 1.74 else 144)

        # --- moon orbit: lower half of the orbit is in front of the planet
        ma = t * 0.4
        mx = cx + math.cos(ma) * 2.9 * R * aspect
        my = cy + math.sin(ma) * 2.9 * R * 0.45
        mr = max(1.2, R * 0.28)
        moon_front = math.sin(ma) > 0

        def draw_moon():
            sphere(mx, my, mr, lambda lat, lon, b: (238, 242, 246, 250, 254)[min(4, int(b * 5))], 0)

        def planet_color(lat, lon, b):
            if b < 0.12:
                return 236  # night side
            bands = (94, 130, 136, 172, 179, 180, 215, 222)
            stripe = math.sin(lat * 9 + 0.6 * math.sin(lon * 2 + lat * 4))
            return bands[int((stripe + 1) / 2 * (len(bands) - 1))]

        # draw back to front so closer things cover farther ones
        if not moon_front:
            draw_moon()
        ring(front=False)
        sphere(cx, cy, R, planet_color, t * 0.5)
        ring(front=True)
        if moon_front:
            draw_moon()

        t += 0.05
        yield render(grid)


ANIMATIONS = {"starfield": starfield, "matrix": matrix, "wave": wave,
              "bounce": bounce, "jellyfish": jellyfish, "space": space}
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