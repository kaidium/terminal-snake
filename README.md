# Terminal Snake 🐍

A colorful terminal Snake game written in Python using `curses`. No dependencies beyond the Python standard library.

## Features

- Smooth, responsive controls (arrow keys or WASD)
- Three speed tiers that increase as your score grows
- Bonus food (★) worth 3 points that appears randomly and flashes before disappearing
- High score tracking within a session
- Welcome screen and game-over screen with restart support
- Works in any terminal that supports colors (most do)

## Requirements

- Python 3.6+
- A terminal with color support (xterm, iTerm2, most Linux terminals)
- At least 20×10 terminal size (bigger is better — fullscreen recommended)

## Usage

```bash
python3 snake.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow keys or WASD | Move |
| `r` | Restart after game over |
| `q` | Quit |

## Scoring

| Item | Points |
|------|--------|
| ● Regular food | +1 |
| ★ Bonus food | +3 |

Speed increases at score 10 (fast) and score 25 (TURBO).
