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
    assert moves[O] <= moves[X] <= moves[O] + 1
    return X if moves[X] - moves[O] == 0 else O


def actions(board):
    return {(x, y) for x, y in range(3) if board[x][y] == EMPTY}


def result(board, action):
    if board[action[0]][action[1]] != EMPTY:
        raise Exception("The action is not available on the board")
    updated_board = copy.deepcopy(board)
    updated_board[action[0]][action[1]] = player(board)
    return updated_board


def winner(board):
    """
    Return winner of the board if there is one, else None
    """
    # 0, 1, 2 for rows, 3, 4, 5 for columns, 6 for leading diag, 7 for opposite diag
    Xs = [0 for _ in range(8)]
    Os = [0 for _ in range(8)]
    for i in range(3):
        for j in range(3):
            tile = board[i][j]
            if tile == EMPTY:
                continue
            arr = Xs if tile == X else Os
            arr[i] += 1
            arr[3 + i] += 1
            if i == j:
                arr[6] += 1
            if i + j == 2:
                arr[7] += 1

    if max(Xs) == 3:
        return X
    if max(Os) == 3:
        return O
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

    p, optimal_action, checked_boards = player(board), None, {}
    v = -math.inf if p == X else math.inf

    for action in actions(board):
        if p == X:
            u, checked_boards = minimiser(result(board, action), checked_boards)
            if u > v:
                optimal_action, v = action, u

        if p == O:
            u, checked_boards = maximiser(result(board, action), checked_boards)
            if u < v:
                optimal_action, v = action, u
    return optimal_action


def minimiser(board, checked_boards):
    if terminal(board):
        checked_boards[board] = utility(board)
        return checked_boards[board], checked_boards

    board_tuple = board_to_tuple(board)
    if board_tuple in checked_boards:
        return checked_boards[board_tuple], checked_boards

    v = math.inf
    for action in actions(board):
        new_board = result(board, action)
        u, checked_boards = maximiser(new_board)
        v = min(v, u)
        checked_boards[board_to_tuple(new_board)] = u
    return v, checked_boards


def maximiser(board, checked_boards):
    if terminal(board):
        checked_boards[board] = utility(board)
        return checked_boards[board], checked_boards

    board_tuple = board_to_tuple(board)
    if board_tuple in checked_boards:
        return checked_boards[board_tuple], checked_boards

    v = -math.inf
    for action in actions(board):
        new_board = result(board, action)
        u, checked_boards = minimiser(new_board)
        v = max(v, u)
        checked_boards[board_to_tuple(new_board)] = u
    return v, checked_boards


def board_to_tuple(board):
    result_tuple = ()
    for row in board:
        result_tuple = result_tuple + tuple(row)
    return result_tuple
