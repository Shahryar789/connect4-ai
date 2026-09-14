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
.venv/Scripts/python.exe -m pytest tests/test_ai.py -v
.venv/Scripts/python.exe -m pytest tests/test_ai.py::test_default_weights_favour_the_defender -v
```

## Architecture

- `src/connect4/board.py` — `Board` class: the 6-row x 7-column grid, piece dropping (gravity), win detection, valid-move listing, and draw detection.
- `src/connect4/ai.py` — minimax search with alpha-beta pruning behind a flag (`use_alpha_beta`), plus a numpy-vectorised position evaluation heuristic (`evaluate`, `Weights`). `choose_move(board, player, depth=5, use_alpha_beta=True, weights=None)` is the entry point, returning a `SearchResult` (column, score, nodes explored).
- `tests/test_board.py`, `tests/test_ai.py` — pytest tests for `Board` and `ai`.

### Runtime dependencies

- `numpy` is a runtime dependency (used by `ai.py`'s evaluation heuristic), not just dev tooling.

### Board representation

- `Board.grid` is a list of lists, `grid[row][col]`, size `ROWS=6` x `COLS=7`.
- `grid[0]` is the **top** row, `grid[ROWS-1]` is the **bottom** row. `drop_piece` scans from the bottom row upward to find the first empty cell in a column (gravity), so pieces stack correctly.
- Cell values: `0` = empty, `1` / `2` = the two players. Nothing enforces turn order or which player value is "correct" — callers pass the player id explicitly on each `drop_piece`/`check_win` call.
- `check_win(player)` checks all four directions (horizontal, vertical, `\` diagonal, `/` diagonal) independently by scanning every possible 4-in-a-row window; it is not incremental (recomputes from scratch, not just around the last move).

### Evaluation

- `WINDOW_INDICES` is built once at import time (flat indices of all 69 four-in-a-row lines on the board). `evaluate` fancy-indexes the flattened grid with it, so scoring every window is vectorised rather than looping in Python.
- `score_table(weights)` is a cached 5x5 lookup, since a window's score depends only on how many of `mine`/`theirs` pieces it holds, not on position. `score_window` is the scalar source of truth used to build that table.
- Default `Weights` are deliberately asymmetric (`opp_three=8 > three=5`) so the AI blocks rather than races. This means `evaluate` is **not** antisymmetric between players by default — `test_default_weights_favour_the_defender` asserts this on purpose. Don't "fix" it; antisymmetry only holds when weights are explicitly made symmetric (see `test_evaluation_is_antisymmetric_with_symmetric_weights`).

## Conventions

- Comments explain *why*, not *what* — skip comments that just restate the code.
- Tests use plain `assert` statements, not a helper/matcher library.
- Search logic (minimax) lives in a single recursive function with a flag (e.g. `use_alpha_beta`) to toggle behavior, rather than duplicating near-identical search implementations.
