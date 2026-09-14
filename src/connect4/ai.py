"""
Minimax search with an optional alpha-beta pruning, plus the position evaluation heuristic it relies on.

Both search modes share one recursive function on purpose:
The benchmark's claim is to have an identical search with pruning toggled on/off, 
which only works if there is only one implementation to toggle.
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from connect4.board import Board

WIN_SCORE = 1000000

WINDOW = 4

@dataclass(frozen=True)
class Weights:

    """
    Tunable weights for the evaluation heuristic.

    Defaults are deliberately defensive, an opponent threat outweighs an identical threat of our own,
    thus the AI blocks rather than races. 
    """

    four: int = 100_000
    three: int = 5
    two: int = 2
    opp_three: int = 8
    opp_two: int = 3
    center: int = 3

@dataclass
class SearchResult:

    """
    What choose_move returns: the move, its score, and search cost.
    """

    column: int
    score: int
    nodes_explored: int

class NodeCounter:
    """
    Mutable counter threaded through the recursion.
    """
    def __init__(self):
        self.nodes = 0

def build_window_indices():
    
    """
    Flat indices of all possible 4-in-a-row windows on the board (69, 4).
    """

    rows, cols = Board.ROWS, Board.COLS
    flat = lambda r, c: r * cols + c
    windows = []

    #Horizontal windows
    for r in range(rows):
        for c in range(cols - 3):
            windows.append([flat(r, c + i) for i in range(WINDOW)])

    #Vertical windows
    for c in range(cols):
        for r in range(rows - 3):
            windows.append([flat(r + i, c) for i in range(WINDOW)])

    #Diagonal windows (bottom-right to top-left)
    for r in range(rows - 3):
        for c in range(cols - 3):
            windows.append([flat(r + i, c + i) for i in range(WINDOW)])

    #Diagonal windows (bottom-left to top-right)
    for r in range(3, rows):
        for c in range(cols - 3):
            windows.append([flat(r - i, c + i) for i in range(WINDOW)])

    return np.array(windows, dtype=np.int32)

WINDOW_INDICES = build_window_indices()
CENTER_COL = Board.COLS // 2

def score_window(window, player, weights):
    """
    Score a single window of 4 cells for the given player.
    """

    opponent = 3 - player
    mine = sum(1 for cell in window if cell == player)
    theirs = sum(1 for cell in window if cell == opponent)
    empty = sum(1 for cell in window if cell == 0)

    if mine and theirs:
        return 0
    
    if mine == 4:
        return weights.four
    if mine == 3 and empty == 1:
        return weights.three
    if mine == 2 and empty == 2:
        return weights.two

    if theirs == 4:
        return -weights.four
    if theirs == 3 and empty == 1:
        return -weights.opp_three
    if theirs == 2 and empty == 2:
        return -weights.opp_two
    
    return 0

@lru_cache(maxsize=None)
def score_table(weights):
    """
    5x5 lookup table: table[mine, theirs] -> score for a window with that mix.
    """

    table = np.zeros((WINDOW + 1, WINDOW + 1), dtype=np.int64)
    for mine in range (WINDOW + 1):
        for theirs in range(WINDOW + 1 - mine):
            cells = [1] * mine + [2] * theirs + [0] * (WINDOW - mine - theirs)
            table[mine, theirs] = score_window(cells, 1, weights)
    return table

def get_windows(board):
    """
    Every 4-cell line on the board as a (69, 4) array of cell values
    """

    return np.asarray(board.grid, dtype=np.int8).ravel()[WINDOW_INDICES]

def evaluate(board, player, weights=None):
    """
    Heuristic score for a non-terminal position.
    Positive is good for player.
    """

    weights = weights or Weights()
    opponent = 3 - player

    windows = get_windows(board)

    mine = (windows == player).sum(axis=1)
    theirs = (windows == opponent).sum(axis=1)
    score = int(score_table(weights)[mine, theirs].sum())

    center = np.asarray(board.grid, dtype=np.int8)[:, CENTER_COL]
    score += weights.center * int((center == player).sum() - (center == opponent).sum())

    return score

def order_moves(moves, cols):
    """
    Sort candidate moves center-outwards.
    """

    center = cols // 2

    return sorted(moves, key=lambda c: abs(c - center))

def search(board, depth, alpha, beta, maximizing, ai_player, counter, use_alpha_beta, weights):

    """
    One recursive minimax node

    alpha = best score the maximiser can already guarantee;
    beta  = best score the minimiser can already guarantee.
    """

    counter.nodes += 1
    opponent = 3 - ai_player

    if board.check_win(ai_player):
        return WIN_SCORE + depth, None
    if board.check_win(opponent):
        return -(WIN_SCORE + depth), None

    moves = board.valid_moves()
    if not moves:
        return 0, None
    if depth == 0:
        return evaluate(board, ai_player, weights), None

    moves = order_moves(moves, board.COLS)
    best_col = moves[0]

    if maximizing: 
        best_score = -float("inf")
        for col in moves:
            board.drop_piece(col, ai_player)
            score,  _ = search(
                board, depth - 1, alpha, beta, False, ai_player, counter, use_alpha_beta, weights
            )
            board.undo_move(col)

            if score > best_score:
                best_score, best_col = score, col
            alpha = max(alpha, best_score)
            if use_alpha_beta and alpha >= beta:
                break

    else:
        best_score = float("inf")
        for col in moves:
            board.drop_piece(col, opponent)
            score, _ = search(
                board, depth - 1, alpha, beta, True, ai_player, counter, use_alpha_beta, weights
            )
            board.undo_move(col)

            if score < best_score:
                best_score, best_col = score, col
            beta = min(beta, best_score)
            if use_alpha_beta and beta <= alpha:
                break

    return best_score, best_col

def choose_move(board, player, depth=5, use_alpha_beta=True, weights=None):
    """
    Pick a column for player.
    """
    counter = NodeCounter()
    score, column = search(
        board,
        depth,
        -float("inf"),
        float("inf"),
        True,
        player,
        counter,
        use_alpha_beta,
        weights or Weights(),
    )
    return SearchResult(column=column, score=score, nodes_explored=counter.nodes)

