import sys

from crossword import *
from collections import deque, namedtuple
import random
Unassigned_Variable = namedtuple('Unassigned_Variable', 'variable, num_choices minus_num_nbhs')


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        values_to_remove = []
        for variable, potential_words in self.domains.items():
            for x in potential_words:
                if variable.length != len(x):
                    values_to_remove.append((variable, x))
        for variable, x in values_to_remove:
            self.domains[variable].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[x, y]:
            x_overlap, y_overlap = self.crossword.overlaps[x, y]
            x_domain_needed_revision = False
            values_to_remove = []
            for test_x in self.domains[x]:
                match_in_y = any([test_x[x_overlap] == test_y[y_overlap] for test_y in self.domains[y]])
                if match_in_y:
                    continue
                values_to_remove.append((x, test_x))
                x_domain_needed_revision = True
            for x, test_x in values_to_remove:
                self.domains[x].remove(test_x)
            return x_domain_needed_revision
        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = ((variable, y) for variable in self.domains for y in self.crossword.neighbors(variable))
        queue = deque(arcs)
        while queue:
            x, y = queue.popleft()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return not any(v == "" for v in assignment.values())

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        unique_var_consistent = len(assignment.values()) == len(set(assignment.values()))
        lengths_consistent = [variable.length == len(input_var) for variable, input_var in assignment.items()]
        length_consistent = all(lengths_consistent)
        return length_consistent and unique_var_consistent

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        constraining_values = []
        valid_nghs = self.crossword.neighbors(var) - set(assignment.keys())
        for word in self.domains[var]:
            ngh_vals_removed = 0
            for ngh in valid_nghs:
                x_overlap, y_overlap = self.crossword.overlaps[var, ngh]
                ngh_vals_removed += sum(1 for ngh_word in self.domains[ngh] if word[x_overlap] != ngh_word[y_overlap])
            constraining_values.append((word, ngh_vals_removed))
        constraining_values.sort(key=lambda x: x[1], reverse=False)
        return constraining_values


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = []
        for unassigned_variable in self.crossword.variables - set(assignment.keys()):
            unassigned_variables.append(
                Unassigned_Variable(
                    unassigned_variable,
                    len(self.domains[unassigned_variable]),
                    -len(self.crossword.neighbors(unassigned_variable))
                )
            )
        unassigned_variables.sort(key=lambda x: (x[1], x[2]), reverse=False)
        return unassigned_variables

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.crossword.variables == set(assignment.keys()):
            return assignment

        unassigned_variables = self.crossword.variables - set(assignment.keys())
        var = random.choice(tuple(unassigned_variables))
        for value in self.domains[var]:
            test_assignment = assignment.copy()
            test_assignment[var] = value
            if self.consistent(test_assignment):
                result = self.backtrack(test_assignment)
                if self.consistent(result):
                    return result
                self.domains[var].remove(value)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
