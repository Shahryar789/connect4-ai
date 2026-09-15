"""
Benchmark alpha-beta pruning against plain minimax.

For each depth in range, runs choose_move on an empty board both with and
without pruning, recording nodes explored and wall-clock time for each.
Prints a results table to stdout and saves a nodes-explored-vs-depth plot
to docs/benchmark.png.
"""

import os
import time
from dataclasses import dataclass

import matplotlib.pyplot as plt

from connect4.ai import choose_move
from connect4.board import Board

MAX_DEPTH = 7

PLOT_PATH = "docs/benchmark.png"

@dataclass
class BenchmarkResult:

    """
    One (depth, mode) measurement: nodes explored and time taken.
    """

    depth: int
    use_alpha_beta: bool
    nodes_explored: int
    seconds: float

def run_trial(depth, use_alpha_beta):
    """
    Run choose_move once from an empty board and time it.
    """

    board = Board()
    start = time.perf_counter()
    result = choose_move(board, player=1, depth=depth, use_alpha_beta=use_alpha_beta)
    elapsed = time.perf_counter() - start

    return BenchmarkResult(depth, use_alpha_beta, result.nodes_explored, elapsed)

def run_benchmark(max_depth):
    """
    Run both search modes at every depth from 1 to max_depth.
    """

    results = []
    for depth in range(1, max_depth + 1):
        for use_alpha_beta in (False, True):
            results.append(run_trial(depth, use_alpha_beta))
    return results

def print_table(results):
    """
    Print a results table to stdout.
    """

    header = f"{'depth':>5} {'mode':>12} {'nodes':>12} {'seconds':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        mode = "alpha-beta" if r.use_alpha_beta else "minimax"
        print(f"{r.depth:>5} {mode:>12} {r.nodes_explored:>12} {r.seconds:>10.4f}")

def plot_results(results, path):
    """
    Plot nodes explored vs depth, log y-axis, one line per mode.
    """

    depths = sorted({r.depth for r in results})

    minimax_nodes = [r.nodes_explored for r in results if not r.use_alpha_beta]
    alpha_beta_nodes = [r.nodes_explored for r in results if r.use_alpha_beta]

    fig, ax = plt.subplots()
    ax.plot(depths, minimax_nodes, marker="o", label="minimax")
    ax.plot(depths, alpha_beta_nodes, marker="o", label="alpha-beta")
    ax.set_yscale("log")
    ax.set_xlabel("depth")
    ax.set_ylabel("nodes explored")
    ax.set_title("Minimax vs alpha-beta pruning")
    ax.legend()

    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path)

def main():
    results = run_benchmark(MAX_DEPTH)
    print_table(results)
    plot_results(results, PLOT_PATH)

if __name__ == "__main__":
    main()

