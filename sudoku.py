#!/usr/bin/env python3

import z3

class Sudoku:

    _grid: list[list[z3.Int]] = [[ None for _ in range(9) ] for _ in range(9) ]
    _solver: z3.Solver = None

    _nums = [[ '.' for _ in range(9) ] for _ in range(9) ]

    def __init__(self):
        self._solver = z3.Solver()

        # Create variables
        for row in range(9):
            for col in range(9):
                int_var = z3.Int(f"cell_{row+1}_{col+1}")
                self._grid[row][col] = int_var

        # Add constraints for classic sudoku
        self.add_classic_constraints()

        self.add_math_constraints()

    def add_classic_constraints(self):
        # Digits from 1-9
        for r in range(9):
            for c in range(9):
                v = self._grid[r][c]
                self._solver.add(v >= 1)
                self._solver.add(v <= 9)

        # Distinct digits in row/column
        for i in range(9):
            self._solver.add(z3.Distinct(self._grid[i])) # Row
            self._solver.add(z3.Distinct([self._grid[r][i] for r in range(9)])) # Column

    def add_math_constraints(self):

        # utility function that converts a tuple of 1-indexed coordinates to a tuple of their respective solver variables
        # the below functions accept the positions of the matching cells in this format.
        def coords_to_els(*coord_pairs: tuple[int, int]) -> tuple[z3.ArithRef, ...]:
            return tuple(self._grid[row - 1][col - 1] for row, col in coord_pairs)

        # utility functions to specify various math sudoku conditions.
        # the arguments are (val, *coords), where val is the associated value the result should match,
        # and coords contains coordinate pairs of the cells the operation should be applied to.
        # (each operation has its own function)

        # for example, the constraint:
        # --> "the values of the cells at row 1, column 1; row 2, column 1; row 2, column 2; and row 3, column 1, should multiply together to be 1120"
        # would be specified like:
        # --> times(1120, (1, 1), (2, 1), (2, 2), (3, 1))

        def minus(val, *coords):
            el1, el2 = coords_to_els(*coords)
            self._solver.add(z3.Abs(el1 - el2) == val)

        def divide(val, *coords):
            el1, el2 = coords_to_els(*coords)
            self._solver.add(el1 / el2 == val or el2 / el1 == val)

        def times(val, *coords):
            els = coords_to_els(*coords)
            res = els[0]
            for el in els[1:]:
                res *= el
            self._solver.add(res == val)

        def plus(val, *coords):
            els = coords_to_els(*coords)
            res = els[0]
            for el in els[1:]:
                res += el
            self._solver.add(res == val)

        def equal(val, *coords):
            el = coords_to_els(*coords)[0]
            self._solver.add(el == val)

        # defining the constraints from the specific puzzle I wanted to solve.
        times(1120, (1, 1), (2, 1), (2, 2), (3, 1)) # 1
        minus(8, (1, 2), (1, 3)) # 2
        times(168, (1, 4), (1, 5), (1, 6)) # 3
        times(48, (1, 7), (1, 8), (2, 8)) # 4
        times(18, (1, 9), (2, 9), (3, 9)) # 5
        plus(13, (2, 3), (3, 2), (3, 3), (3, 4)) # 6
        plus(21, (2, 4), (2, 5), (2, 6)) # 7
        plus(24, (2, 7), (3, 6), (3, 7), (3, 8)) # 8
        times(108, (4, 1), (4, 2), (5, 2)) # 9
        plus(9, (4, 3), (4, 4)) # 10
        minus(4, (3, 5), (4, 5)) # 11
        minus(5, (4, 6), (4, 7)) # 12
        plus(22, (4, 8), (4, 9), (5, 8)) # 13
        plus(9, (5, 1), (6, 1), (7, 1)) # 14
        minus(5, (6, 2), (7, 2)) # 15
        divide(3, (5, 3), (5, 4)) # 16
        plus(15, (5, 5), (5, 6), (5, 7)) # 17
        times(42, (6, 3), (6, 4)) # 18
        times(32, (7, 3), (7, 4)) # 19
        divide(3, (6, 5), (7, 5)) # 20
        plus(17, (6, 6), (6, 7)) # 21
        plus(3, (7, 6), (7, 7)) # 22
        times(20, (6, 8), (7, 8)) # 23
        times(120, (5, 9), (6, 9), (7, 9)) # 24
        times(2160, (8, 1), (8, 2), (9, 1), (9, 2)) # 25
        plus(17, (8, 3), (8, 4), (9, 3)) # 26
        plus(3, (8, 5), (8, 6)) # 27
        times(96, (9, 4), (9, 5), (9, 6)) # 28
        times(35, (8, 7), (9, 7)) # 29
        plus(8, (8, 8), (8, 9), (9, 8)) # 30
        equal(7, (9, 9)) # 31

    def solve(self):
        if self._solver.check() == z3.sat:
            m = self._solver.model()
            for r in range(9):
                for c in range(9):
                    self._nums[r][c] = m.evaluate(self._grid[r][c])
            return True
        else:
            return False

    def print(self):
        for r in range(9):
            print('   '
                    .join(["{} {} {}".format(a,b,c) for a,b,c in
                        zip(self._nums[r][::3], self._nums[r][1::3], self._nums[r][2::3])]))
            if r in [2, 5]:
                print()

if __name__ == "__main__":
    s = Sudoku()

    if s.solve():
        print("Solved sudoku:")
        s.print()
    else:
        print("Invalid constraints -- cannot solve")
