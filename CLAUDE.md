# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Connect Four AI, built as a portfolio project to demonstrate minimax and alpha-beta pruning. Python, `src` layout, tested with pytest.

## Commands

```bash
# create venv (first time)
python -m venv .venv

# install package + dev deps (editable)
.venv/Scripts/python.exe -m pip install -e ".[dev]"

# run full test suite
.venv/Scripts/python.exe -m pytest -v

# run a single test file / test
.venv/Scripts/python.exe -m pytest tests/test_board.py -v
.venv/Scripts/python.exe -m pytest tests/test_board.py::test_horizontal_win -v
```

On this machine, Python is installed at `C:\Users\hussa\AppData\Local\Programs\Python\Python312\python.exe` but is not yet on PATH for new shells — use the full path (or the venv's `python.exe`) if a bare `python` invocation fails with the "Python was not found" App Execution Alias error.

## Architecture

- `src/connect4/board.py` — `Board` class: the 6-row x 7-column grid, piece dropping (gravity), win detection, valid-move listing, and draw detection. This is the only implemented module so far.
- `tests/test_board.py` — pytest tests for `Board`.
- No AI/search module exists yet (minimax, alpha-beta pruning are planned but not started — do not implement them unless asked).

### Board representation

- `Board.grid` is a list of lists, `grid[row][col]`, size `ROWS=6` x `COLS=7`.
- `grid[0]` is the **top** row, `grid[ROWS-1]` is the **bottom** row. `drop_piece` scans from the bottom row upward to find the first empty cell in a column (gravity), so pieces stack correctly.
- Cell values: `0` = empty, `1` / `2` = the two players. Nothing enforces turn order or which player value is "correct" — callers pass the player id explicitly on each `drop_piece`/`check_win` call.
- `check_win(player)` checks all four directions (horizontal, vertical, `\` diagonal, `/` diagonal) independently by scanning every possible 4-in-a-row window; it is not incremental (recomputes from scratch, not just around the last move).
