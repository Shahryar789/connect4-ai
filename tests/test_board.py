import pytest

from connect4.board import Board


def test_new_board_is_empty_and_all_columns_valid():
    board = Board()
    assert board.valid_moves() == list(range(7))
    assert not board.is_full()


def test_drop_piece_lands_on_bottom_row():
    board = Board()
    row = board.drop_piece(3, 1)
    assert row == 5
    assert board.grid[5][3] == 1


def test_drop_piece_stacks_on_top_of_previous_piece():
    board = Board()
    board.drop_piece(2, 1)
    row = board.drop_piece(2, 2)
    assert row == 4
    assert board.grid[4][2] == 2
    assert board.grid[5][2] == 1


def test_drop_piece_raises_on_full_column():
    board = Board()
    for player in [1, 2, 1, 2, 1, 2]:
        board.drop_piece(0, player)
    assert 0 not in board.valid_moves()
    with pytest.raises(ValueError):
        board.drop_piece(0, 1)


def test_drop_piece_raises_on_out_of_range_column():
    board = Board()
    with pytest.raises(ValueError):
        board.drop_piece(7, 1)
    with pytest.raises(ValueError):
        board.drop_piece(-1, 1)


def test_horizontal_win():
    board = Board()
    for col in range(4):
        board.drop_piece(col, 1)
    assert board.check_win(1)
    assert not board.check_win(2)


def test_vertical_win():
    board = Board()
    for _ in range(4):
        board.drop_piece(3, 1)
    assert board.check_win(1)


def test_diagonal_up_right_win():
    board = Board()
    # Build a staircase so column i has i+1 pieces, with player 1 on top each time.
    board.drop_piece(0, 1)

    board.drop_piece(1, 2)
    board.drop_piece(1, 1)

    board.drop_piece(2, 2)
    board.drop_piece(2, 2)
    board.drop_piece(2, 1)

    board.drop_piece(3, 2)
    board.drop_piece(3, 2)
    board.drop_piece(3, 2)
    board.drop_piece(3, 1)

    assert board.check_win(1)


def test_diagonal_down_right_win():
    board = Board()
    # Mirror image of the up-right staircase.
    board.drop_piece(0, 2)
    board.drop_piece(0, 2)
    board.drop_piece(0, 2)
    board.drop_piece(0, 1)

    board.drop_piece(1, 2)
    board.drop_piece(1, 2)
    board.drop_piece(1, 1)

    board.drop_piece(2, 2)
    board.drop_piece(2, 1)

    board.drop_piece(3, 1)

    assert board.check_win(1)


def test_no_win_on_empty_or_scattered_board():
    board = Board()
    assert not board.check_win(1)
    assert not board.check_win(2)

    board.drop_piece(0, 1)
    board.drop_piece(2, 1)
    board.drop_piece(4, 1)
    assert not board.check_win(1)


def test_is_draw_when_board_full_without_a_winner():
    board = Board()
    # A pattern that fills the board with no 4-in-a-row.
    pattern = [
        [1, 1, 2, 2, 1, 1, 2],
        [2, 2, 1, 1, 2, 2, 1],
        [1, 1, 2, 2, 1, 1, 2],
        [2, 2, 1, 1, 2, 2, 1],
        [1, 1, 2, 2, 1, 1, 2],
        [2, 2, 1, 1, 2, 2, 1],
    ]
    for row in reversed(pattern):
        for col, player in enumerate(row):
            board.drop_piece(col, player)

    assert board.is_full()
    assert board.is_draw()
