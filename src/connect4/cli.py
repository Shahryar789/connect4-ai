"""
Playable human-vs-AI Connect Four game in the terminal, built on typer.
"""

import sys
import time

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from connect4.ai import choose_move
from connect4.board import Board

PIECES = {0: "[dim]·[/]", 1: "[bold red]●[/]", 2: "[bold yellow]○[/]"}

if sys.platform == "win32":
    # Legacy Windows consoles default to cp1252, which can't encode the circle glyphs below.
    sys.stdout.reconfigure(encoding="utf-8")

app = typer.Typer()
console = Console()

def render_board(board):
    """
    Build a bordered grid of circular pieces on a blue background, with column numbers underneath.
    """

    table = Table(box=box.SQUARE, show_header=False, style="on blue", padding=(0, 1))
    for _ in range(board.COLS):
        table.add_column(justify="center")

    for row in board.grid:
        table.add_row(*(PIECES[cell] for cell in row))

    table.add_row(*(f"[bold]{col + 1}[/]" for col in range(board.COLS)))

    return table

def prompt_human_move(board):
    """
    Ask for a column, reprompting on anything that isn't a valid move.
    """

    while True:
        raw = input("Your move (1-7): ")
        try:
            col = int(raw) - 1
        except ValueError:
            print("Please enter a number.")
            continue

        if not board.is_valid_move(col):
            print("That column is full or doesn't exist, try again.")
            continue

        return col

def announce_result(board, human, ai):
    """
    Print the outcome and return True if the game has ended.
    """

    if board.check_win(human):
        print("You win!")
        return True
    if board.check_win(ai):
        print("The AI wins!")
        return True
    if board.is_draw():
        print("It's a draw.")
        return True
    return False

def play(depth, human_first, alpha_beta):
    """
    Run one full game between the human and the AI.
    """

    board = Board()
    human, ai = 1, 2
    turn = human if human_first else ai

    console.print(render_board(board))

    while True:
        status = []

        if turn == human:
            col = prompt_human_move(board)
            board.drop_piece(col, human)
            status.append(f"You played column {col + 1}")

            if board.check_win(human) or board.is_draw():
                print(" · ".join(status))
                console.print(render_board(board))
                announce_result(board, human, ai)
                break

        start = time.perf_counter()
        result = choose_move(board, ai, depth=depth, use_alpha_beta=alpha_beta)
        elapsed = time.perf_counter() - start
        board.drop_piece(result.column, ai)
        status.append(
            f"AI played column {result.column + 1} — "
            f"{result.nodes_explored:,} nodes in {elapsed:.2f}s"
        )

        print(" · ".join(status))
        console.print(render_board(board))

        if announce_result(board, human, ai):
            break

        turn = human

@app.command()
def main(depth: int = 5, first: bool = True, alpha_beta: bool = True):
    """
    Play a game of Connect Four against the AI.
    """

    try:
        play(depth, first, alpha_beta)
    except KeyboardInterrupt:
        print("\nGame interrupted.")

if __name__ == "__main__":
    app()

