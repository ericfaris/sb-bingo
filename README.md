# SB Bingo - Bingo Card Generator

A Python script that generates printable bingo cards as a multi-page PDF from a plain-text list of items. Each card gets a unique, randomized arrangement. Works with any theme — Super Bowl watch parties, classrooms, holidays, team events, etc.

Included is a sample `events.txt` with 100 Super Bowl game-day events (plays, commercials, broadcast moments) ready to use.

## Requirements

- Python 3.10+
- [reportlab](https://pypi.org/project/reportlab/)

## Installation

```bash
pip install reportlab
```

## Usage

```bash
python bingo_generator.py <items_file> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `items_file` | **Required.** Path to a text file with one item per line. Blank lines and lines starting with `#` are ignored. |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--rows` | `5` | Number of rows per card |
| `--cols` | `5` | Number of columns per card |
| `--cards` | `10` | Number of cards to generate |
| `--title` | `"BINGO"` | Title displayed at the top of each card |
| `--free-space` | off | Enable a center free space (only works for odd x odd grids) |
| `--free-text` | `"FREE"` | Label for the free space cell |
| `--output`, `-o` | `"bingo_cards.pdf"` | Output PDF filename |

### Examples

```bash
# 15 cards, 5x5 grid, center free space, using the included Super Bowl events
python bingo_generator.py events.txt --rows 5 --cols 5 --cards 15 --free-space

# 10 cards, 4x4 grid, no free space, custom title
python bingo_generator.py events.txt --rows 4 --cols 4 --cards 10 --title "Game Day Bingo"

# 8 cards, 3x3 grid, custom free space label
python bingo_generator.py events.txt --rows 3 --cols 3 --cards 8 --free-space --free-text "WILD"

# Specify output filename
python bingo_generator.py events.txt --cards 20 --output party_bingo.pdf
```

## Items File Format

One item per line. Blank lines are skipped. Lines starting with `#` are treated as comments.

```text
# My Bingo Items
First item
Second item
Third item
```

You need at least enough items to fill one card (rows x cols, minus 1 if using free space). For example, a 5x5 grid with free space needs at least 24 unique items.

## Generating Events with AI

Use the following prompt template with ChatGPT, Claude, or any LLM to generate a themed events list for your Super Bowl party. Replace the team names, key players, and year as needed.

```
Generate 100 unique bingo-card events for a Super Bowl LIX watch party
(2025: Kansas City Chiefs vs. Philadelphia Eagles).

Constraints:
- Every event MUST be something that can realistically happen before halftime
  (no "final score", "game MVP", "overtime", "second half kickoff", etc.).
- ~40% football-related events — use real player names and positions from both
  rosters (e.g. "Patrick Mahomes (KC) throws a touchdown pass",
  "Jalen Hurts (PHI) scrambles for positive yards").
  Include a mix of offensive plays, defensive plays, penalties, and special teams.
- ~60% non-football events — commercials (types/themes, not specific brands),
  broadcast moments, crowd shots, sideline activity, graphics, and
  pre-game ceremony moments.
- Keep each event short enough to fit in a bingo card cell (roughly 8-12 words max).
- Output as plain text, one event per line, no numbering.
- Add a comment header line starting with # that describes the list.
```

Save the output to a `.txt` file and pass it to the generator:

```bash
python bingo_generator.py my_events.txt --cards 15 --free-space --title "Super Bowl Bingo"
```

## Output

The script generates a PDF with one card per page on US Letter size (8.5" x 11"). Each card has:

- A title header
- A grid of randomly assigned items
- An optional highlighted free space in the center
- A card number footer

Text automatically wraps and shrinks to fit within cells.
