#!/usr/bin/env python3
"""
Reusable Bingo Card Generator
==============================
Language: Python 3
Library:  reportlab (pip install reportlab)

Generates a multi-page PDF of bingo cards from a plain-text list of items.
One card per page. Works with any theme — Super Bowl, classroom, party, etc.

Install:
    pip install reportlab

Usage examples:
    # 15 cards, 5x5, center free space, from events.txt
    python bingo_generator.py events.txt --rows 5 --cols 5 --cards 15 --free-space

    # 10 cards, 4x4, no free space, custom title
    python bingo_generator.py items.txt --rows 4 --cols 4 --cards 10 --title "Movie Night Bingo"

    # 8 cards, 3x3, custom free space label
    python bingo_generator.py vocab.txt --rows 3 --cols 3 --cards 8 --free-space --free-text "WILD"

    # Specify output filename
    python bingo_generator.py events.txt --cards 20 --output party_bingo.pdf
"""

import argparse
import random
import sys
import textwrap
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas


# ---------------------------------------------------------------------------
# Configuration defaults (edit these or override via CLI args)
# ---------------------------------------------------------------------------
DEFAULT_ROWS = 5
DEFAULT_COLS = 5
DEFAULT_NUM_CARDS = 10
DEFAULT_TITLE = "BINGO"
DEFAULT_FREE_SPACE_TEXT = "FREE"
DEFAULT_OUTPUT = "bingo_cards.pdf"

# Layout constants
PAGE_WIDTH, PAGE_HEIGHT = LETTER  # 8.5 × 11 inches
MARGIN = 0.75 * inch
TITLE_FONT_SIZE = 28
FOOTER_FONT_SIZE = 10
CELL_FONT_SIZE = 11  # will auto-shrink for long text
HEADER_GAP = 0.35 * inch  # space between title and grid
FOOTER_GAP = 0.30 * inch  # space between grid and footer

# Colors
GRID_LINE_COLOR = HexColor("#222222")
FREE_SPACE_BG = HexColor("#FFF3CD")
HEADER_COLOR = HexColor("#1A1A2E")
CELL_TEXT_COLOR = HexColor("#1A1A2E")


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def load_items(filepath: str) -> list[str]:
    """Load items from a plain-text file (one item per line). Blank lines and
    leading/trailing whitespace are stripped. Lines starting with # are
    treated as comments and skipped."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    items: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            items.append(stripped)
    return items


def generate_card(
    items: list[str],
    rows: int,
    cols: int,
    use_free_space: bool,
    free_space_text: str,
) -> list[list[str]]:
    """Build one bingo card as a 2D list of strings."""
    cells_needed = rows * cols
    if use_free_space and rows % 2 == 1 and cols % 2 == 1:
        cells_needed -= 1  # center cell will be the free space

    chosen = random.sample(items, cells_needed)
    idx = 0
    card: list[list[str]] = []
    center_r, center_c = rows // 2, cols // 2

    for r in range(rows):
        row: list[str] = []
        for c in range(cols):
            if (
                use_free_space
                and rows % 2 == 1
                and cols % 2 == 1
                and r == center_r
                and c == center_c
            ):
                row.append(free_space_text)
            else:
                row.append(chosen[idx])
                idx += 1
        card.append(row)
    return card


def _draw_card(
    canvas: Canvas,
    card: list[list[str]],
    card_number: int,
    title: str,
    rows: int,
    cols: int,
    use_free_space: bool,
    free_space_text: str,
):
    """Render a single bingo card on the current PDF page."""
    # Usable area
    usable_w = PAGE_WIDTH - 2 * MARGIN
    usable_h = PAGE_HEIGHT - 2 * MARGIN

    # Title
    canvas.setFont("Helvetica-Bold", TITLE_FONT_SIZE)
    canvas.setFillColor(HEADER_COLOR)
    title_y = PAGE_HEIGHT - MARGIN
    canvas.drawCentredString(PAGE_WIDTH / 2, title_y - TITLE_FONT_SIZE, title)

    # Footer
    canvas.setFont("Helvetica", FOOTER_FONT_SIZE)
    canvas.setFillColor(HEADER_COLOR)
    footer_y = MARGIN
    canvas.drawCentredString(PAGE_WIDTH / 2, footer_y, f"Card #{card_number}")

    # Grid dimensions
    grid_top = title_y - TITLE_FONT_SIZE - HEADER_GAP
    grid_bottom = footer_y + FOOTER_FONT_SIZE + FOOTER_GAP
    grid_height = grid_top - grid_bottom
    grid_width = usable_w

    cell_w = grid_width / cols
    cell_h = grid_height / rows

    grid_x = MARGIN
    grid_y = grid_bottom  # bottom-left of grid

    center_r, center_c = rows // 2, cols // 2

    # Draw cells
    for r in range(rows):
        for c in range(cols):
            x = grid_x + c * cell_w
            y = grid_y + (rows - 1 - r) * cell_h  # row 0 at top

            # Free-space highlight
            is_free = (
                use_free_space
                and rows % 2 == 1
                and cols % 2 == 1
                and r == center_r
                and c == center_c
            )
            if is_free:
                canvas.setFillColor(FREE_SPACE_BG)
                canvas.rect(x, y, cell_w, cell_h, stroke=0, fill=1)

            # Border
            canvas.setStrokeColor(GRID_LINE_COLOR)
            canvas.setLineWidth(1)
            canvas.rect(x, y, cell_w, cell_h, stroke=1, fill=0)

            # Cell text — wrap and auto-size
            text = card[r][c]
            _draw_cell_text(canvas, text, x, y, cell_w, cell_h, is_free)


def _draw_cell_text(
    canvas: Canvas,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    is_free: bool,
):
    """Draw text centered inside a cell, wrapping and shrinking as needed."""
    padding = 4
    max_w = w - 2 * padding
    max_h = h - 2 * padding

    font_name = "Helvetica-Bold" if is_free else "Helvetica"

    # Try decreasing font sizes until text fits
    for size in range(CELL_FONT_SIZE, 5, -1):
        canvas.setFont(font_name, size)
        wrapped = textwrap.wrap(text, width=max(int(max_w / (size * 0.5)), 8))
        line_height = size * 1.2
        total_text_h = len(wrapped) * line_height

        # Check width of each line
        fits = total_text_h <= max_h
        if fits:
            for line in wrapped:
                if canvas.stringWidth(line, font_name, size) > max_w:
                    fits = False
                    break
        if fits:
            break
    else:
        size = 6
        wrapped = textwrap.wrap(text, width=max(int(max_w / (size * 0.5)), 8))
        line_height = size * 1.2
        total_text_h = len(wrapped) * line_height

    # Vertical centering
    start_y = y + h / 2 + total_text_h / 2 - line_height + (line_height - size) / 2

    canvas.setFillColor(CELL_TEXT_COLOR)
    canvas.setFont(font_name, size)
    for i, line in enumerate(wrapped):
        line_y = start_y - i * line_height
        canvas.drawCentredString(x + w / 2, line_y, line)


def generate_pdf(
    items: list[str],
    rows: int = DEFAULT_ROWS,
    cols: int = DEFAULT_COLS,
    num_cards: int = DEFAULT_NUM_CARDS,
    title: str = DEFAULT_TITLE,
    use_free_space: bool = False,
    free_space_text: str = DEFAULT_FREE_SPACE_TEXT,
    output: str = DEFAULT_OUTPUT,
):
    """Generate the full bingo-card PDF."""
    cells_needed = rows * cols
    if use_free_space and rows % 2 == 1 and cols % 2 == 1:
        cells_needed -= 1

    if len(items) < cells_needed:
        print(
            f"Error: need at least {cells_needed} unique items to fill a "
            f"{rows}x{cols} card, but only {len(items)} were provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    c = Canvas(output, pagesize=LETTER)
    for n in range(1, num_cards + 1):
        card = generate_card(items, rows, cols, use_free_space, free_space_text)
        _draw_card(c, card, n, title, rows, cols, use_free_space, free_space_text)
        c.showPage()
    c.save()
    print(f"Saved {num_cards} bingo card(s) to {output}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate printable bingo cards as a PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python bingo_generator.py events.txt --rows 5 --cols 5 --cards 15 --free-space
              python bingo_generator.py items.txt --rows 4 --cols 4 --cards 10 --title "Movie Night"
              python bingo_generator.py vocab.txt --rows 3 --cols 3 --cards 8 --free-space --free-text "WILD"
        """),
    )
    parser.add_argument(
        "items_file",
        help="Path to a text file with one item per line.",
    )
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help=f"Number of rows (default {DEFAULT_ROWS})")
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS, help=f"Number of columns (default {DEFAULT_COLS})")
    parser.add_argument("--cards", type=int, default=DEFAULT_NUM_CARDS, help=f"Number of cards to generate (default {DEFAULT_NUM_CARDS})")
    parser.add_argument("--title", default=DEFAULT_TITLE, help=f'Card title (default "{DEFAULT_TITLE}")')
    parser.add_argument("--free-space", action="store_true", help="Enable center free space (only for odd×odd grids)")
    parser.add_argument("--free-text", default=DEFAULT_FREE_SPACE_TEXT, help=f'Free space label (default "{DEFAULT_FREE_SPACE_TEXT}")')
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help=f'Output PDF filename (default "{DEFAULT_OUTPUT}")')

    args = parser.parse_args()

    if args.rows < 1 or args.cols < 1:
        parser.error("Rows and columns must be at least 1.")
    if args.cards < 1:
        parser.error("Must generate at least 1 card.")

    items = load_items(args.items_file)
    generate_pdf(
        items=items,
        rows=args.rows,
        cols=args.cols,
        num_cards=args.cards,
        title=args.title,
        use_free_space=args.free_space,
        free_space_text=args.free_text,
        output=args.output,
    )


if __name__ == "__main__":
    main()
