import unittest
from tictactoe import *


class TestPlayer(unittest.TestCase):

    def test_x_player(self):
        self.assertEqual(X, player([[EMPTY, EMPTY, O], [X, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]))

    def test_o_player(self):
        self.assertEqual(O, player([[X, EMPTY, O], [X, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]))


class TestAction(unittest.TestCase):

    def test_actions(self):
        self.assertEqual({(0, 1), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)}, actions([[X, EMPTY, O], [X, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]))


class TestResult(unittest.TestCase):

    def test_result(self):
        self.assertEqual([[X, O, O], [X, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]], result([[X, EMPTY, O], [X, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]], (0, 1)))


class TestWinner(unittest.TestCase):

    def test_winner_o(self):
        self.assertEqual(winner([[X, O, O], [X, O, X], [O, X, X]]), O)

    def test_winner_draw_1(self):
        self.assertEqual(winner([[X, O, X], [X, X, O], [O, X, O]]), EMPTY)

    def test_winner_draw_2(self):
        self.assertEqual(winner([[X, EMPTY, X], [X, EMPTY, O], [O, EMPTY, O]]), EMPTY)

    def test_winner_x(self):
        self.assertEqual(winner([[X, EMPTY, EMPTY], [X, EMPTY, EMPTY], [X, O, O]]), X)


class TestTerminal(unittest.TestCase):

    def test_terminal_false(self):
        self.assertEqual(terminal([[X, EMPTY, EMPTY], [X, EMPTY, EMPTY], [EMPTY, O, O]]), False)

    def test_terminal_true_1(self):
        self.assertEqual(terminal([[X, EMPTY, EMPTY], [X, EMPTY, EMPTY], [X, O, O]]), True)

    def test_terminal_true_2(self):
        self.assertEqual(terminal([[X, O, X], [X, X, O], [O, X, O]]), True)


class TestUtility(unittest.TestCase):

    def test_utility_x_win(self):
        self.assertEqual(utility([[X, EMPTY, EMPTY], [X, EMPTY, EMPTY], [X, O, O]]), 1)

    def test_utility_draw(self):
        self.assertEqual(utility([[X, O, X], [X, X, O], [O, X, O]]), 0)

    def test_utility_o_win(self):
        self.assertEqual(utility([[X, O, O], [X, O, X], [O, X, X]]), -1)


class TestMinimax(unittest.TestCase):

    def test_minimax_1(self):
        self.assertEqual(minimax([[X, EMPTY, EMPTY], [X, EMPTY, EMPTY], [EMPTY, EMPTY, O]]), (2, 0))

    def test_minimax_2(self):
        self.assertEqual(minimax([[X, EMPTY, EMPTY], [X, EMPTY, EMPTY], [O, X, O]]), (0, 2))


if __name__ == '__main__':
    unittest.main()