"""
Tic Tac Toe Player
"""

import math
from collections import defaultdict
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    moves = defaultdict(int)
    for row in board:
        for tile in row:
            moves[tile] += 1
    return X if moves[X] - moves[O] == 0 else O


def actions(board):
    empty_cells = set()
    for x_coord, row in enumerate(board):
        for y_coord, tile in enumerate(row):
            if tile == EMPTY:
                empty_cells.add((x_coord, y_coord))
    return empty_cells


def result(board, action):
    if action not in actions(board):
        raise Exception
    updated_board = copy.deepcopy(board)
    updated_board[action[0]][action[1]] = player(board)
    return updated_board


def winner(board):
    """
    Return winner of the board if there is one, else None
    """
    scores = defaultdict(lambda: defaultdict(int))
    for row_num, row in enumerate(board):
        for col_num, tile in enumerate(row):
            scores[tile][row_num] += 1
            scores[tile][3 + col_num] += 1
            if row_num == col_num:
                scores[tile][6] += 1
            if row_num + col_num == 2:
                scores[tile][7] += 1

    for key, totals_dict in scores.items():
        if 3 in totals_dict.values():
            return key
    return None


def terminal(board):
    return bool(winner(board)) or not(actions(board))


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    p, optimal_action = player(board), None
    v = -math.inf if p == X else math.inf

    for action in actions(board):
        if p == X:
            utility = minimiser(result(board, action))
            if utility > v:
                optimal_action, v = action, utility

        if p == O:
            utility = maximiser(result(board, action))
            if utility < v:
                optimal_action, v = action, utility
    return optimal_action


def minimiser(board):
    if terminal(board):
        return utility(board)

    v = math.inf
    for action in actions(board):
        v = min(v, maximiser(result(board, action)))
    return v


def maximiser(board):
    if terminal(board):
        return utility(board)

    v = -math.inf
    for action in actions(board):
        v = max(v, minimiser(result(board, action)))
    return v
