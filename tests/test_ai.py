import numpy as np
import pytest

from connect4.board import Board
from connect4.ai import (
    WINDOW_INDICES,
    WIN_SCORE,
    Weights,
    choose_move,
    evaluate,
    get_windows,
    order_moves,
    score_table,
    score_window,
)

W = Weights()

#Score window tests:

def test_score_window_rewards_own_threats():
    assert score_window([1, 1, 1, 0], 1, W) == W.three
    assert score_window([1, 1, 0, 0], 1, W) == W.two

def test_score_window_punishes_opponent_threats_harder():
    assert score_window([2, 2, 2, 0], 1, W) == -W.opp_three
    assert W.opp_three > W.three  

def test_mixed_window_is_dead():
    assert score_window([1, 2, 1, 0], 1, W) == 0

def test_score_window_is_symmetric_between_players():
    assert score_window([1, 1, 1, 0], 1, W) == score_window([2, 2, 2, 0], 2, W)

#Window geometry tests:

def test_window_index_table_has_the_right_shape():
    assert WINDOW_INDICES.shape == (69, 4)

def test_every_window_index_is_on_the_board():
    assert WINDOW_INDICES.min() >= 0
    assert WINDOW_INDICES.max() < Board.ROWS * Board.COLS

def test_all_windows_are_distinct():
    assert len({tuple(w) for w in WINDOW_INDICES}) == 69

def test_get_windows_reads_actual_cell_values():
    board = Board()
    board.drop_piece(0, 1)
    windows = get_windows(board)
    assert windows.shape == (69, 4)
    assert (windows == 1).sum() == 3 

#Score table tests:

def test_score_table_agrees_with_score_window():
    table = score_table(W)
    for mine in range(5):
        for theirs in range(5 - mine):
            cells = [1] * mine + [2] * theirs + [0] * (4 - mine - theirs)
            assert table[mine, theirs] == score_window(cells, 1, W)

def test_score_table_is_cached():
    assert score_table(W) is score_table(Weights())

#Evaluation tests:

def test_empty_board_evaluates_to_zero():
    assert evaluate(Board(), 1) == 0

def test_centre_column_is_preferred_over_the_edge():
    centre = Board()
    centre.drop_piece(3, 1)

    edge = Board()
    edge.drop_piece(0, 1)

    assert evaluate(centre, 1) > evaluate(edge, 1)

def test_evaluation_is_antisymmetric_with_symmetric_weights():
    symmetric = Weights(opp_three=5, opp_two=2)
    board = Board()
    board.drop_piece(3, 1)
    board.drop_piece(3, 1)
    assert evaluate(board, 1, symmetric) == -evaluate(board, 2, symmetric)

def test_default_weights_favour_the_defender():
    board = Board()
    board.drop_piece(3, 1)
    board.drop_piece(3, 1)
    assert -evaluate(board, 2) > evaluate(board, 1)

def test_evaluate_returns_a_plain_int():
    assert isinstance(evaluate(Board(), 1), int)

def test_vectorised_evaluate_matches_a_naive_loop():
    board = Board()
    for col, player in [(3, 1), (3, 2), (2, 1), (4, 2), (2, 1)]:
        board.drop_piece(col, player)

    grid = np.asarray(board.grid).ravel()
    naive = sum(score_window(grid[idx], 1, W) for idx in WINDOW_INDICES)
    centre = [board.grid[r][Board.COLS // 2] for r in range(Board.ROWS)]
    naive += W.center * (centre.count(1) - centre.count(2))

    assert evaluate(board, 1, W) == naive

def test_weights_change_the_evaluation():
    board = Board()
    board.drop_piece(0, 1)
    board.drop_piece(1, 1)
    assert evaluate(board, 1, W) != evaluate(board, 1, Weights(two=50))

#Order moves tests:


def test_order_moves_starts_from_the_centre():
    assert order_moves([0, 1, 2, 3, 4, 5, 6], 7)[0] == 3

def test_order_moves_keeps_every_move():
    moves = [0, 2, 5, 6]
    assert sorted(order_moves(moves, 7)) == moves

#Search tests:

def test_takes_an_immediate_win():
    board = Board()
    for col in (0, 1, 2):
        board.drop_piece(col, 1)
    for col in (0, 1, 2):
        board.drop_piece(col, 2)

    result = choose_move(board, 1, depth=4)
    assert result.column == 3
    assert result.score >= WIN_SCORE

def test_blocks_an_immediate_loss():
    board = Board()
    for col in (0, 1, 2):
        board.drop_piece(col, 2)
    for col in (4, 5):
        board.drop_piece(col, 1)

    assert choose_move(board, 1, depth=4).column == 3

def test_search_leaves_the_board_untouched():
    board = Board()
    board.drop_piece(3, 1)
    board.drop_piece(3, 2)
    before = [row[:] for row in board.grid]

    choose_move(board, 1, depth=4)

    assert board.grid == before

@pytest.mark.parametrize("depth", [2, 3, 4])
def test_pruning_finds_the_same_score_as_plain_minimax(depth):
    board = Board()
    board.drop_piece(3, 1)
    board.drop_piece(3, 2)
    board.drop_piece(2, 1)

    plain = choose_move(board, 1, depth=depth, use_alpha_beta=False)
    pruned = choose_move(board, 1, depth=depth, use_alpha_beta=True)

    assert plain.score == pruned.score

def test_pruning_explores_far_fewer_nodes():
    board = Board()
    board.drop_piece(3, 1)
    board.drop_piece(3, 2)

    plain = choose_move(board, 1, depth=5, use_alpha_beta=False)
    pruned = choose_move(board, 1, depth=5, use_alpha_beta=True)

    assert pruned.nodes_explored < plain.nodes_explored

def test_prefers_a_faster_win():
    board = Board()
    for col in (0, 1, 2):
        board.drop_piece(col, 1)
    for col in (4, 5, 6):
        board.drop_piece(col, 2)

    assert choose_move(board, 1, depth=5).column == 3

def test_only_returns_legal_moves():
    board = Board()
    for player in (1, 2, 1, 2, 1, 2):
        board.drop_piece(0, player)  

    assert choose_move(board, 1, depth=3).column in board.valid_moves()