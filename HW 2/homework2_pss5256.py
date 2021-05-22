############################################################
# CMPSC 442: Homework 2
############################################################

student_name = "Param S. Somane"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import math
import random
import copy


############################################################
# Section 1: N-Queens
############################################################

def num_placements_all(n):
    return math.factorial(n * n) / (math.factorial(n) * math.factorial(n * n - n))


def num_placements_one_per_row(n):
    return n ** n


def n_queens_valid(board):
    for i in range(len(board)):
        for j in range(i + 1, len(board)):
            if board[i] == board[j] or i - board[i] == j - board[j] or i + board[i] == j + board[j]:
                return False
    return True


def n_queens_solutions(n):
    board = [0] * n
    for optimal_sol in n_queens_helper(0, board):
        yield optimal_sol


def n_queens_helper(row, board):
    if row == len(board):
        yield board[:]
    else:
        for j in range(len(board)):
            board[row] = j
            if n_queens_valid(board[:row + 1]):
                for sol in n_queens_helper(row + 1, board):
                    yield sol


############################################################
# Section 2: Lights Out
############################################################

class LightsOutPuzzle(object):

    def __init__(self, board):
        self.board = board
        self.row = len(board)
        self.col = (0 if self.row == 0 else len(board[0]))

    def get_board(self):
        return self.board

    def perform_move(self, row, col):
        toggle_lights = [(row, col), (row - 1, col), (row, col - 1), (row + 1, col), (row, col + 1)]
        for (i, j) in toggle_lights:
            if 0 <= i < self.row and 0 <= j < self.col:
                self.board[i][j] = not self.board[i][j]

    def scramble(self):
        for i in range(self.row):
            for j in range(self.col):
                if random.random() < 0.5:
                    self.perform_move(i, j)

    def is_solved(self):
        for i in range(self.row):
            for j in range(self.col):
                if self.board[i][j]:
                    return False
        return True

    def copy(self):
        return LightsOutPuzzle(copy.deepcopy(self.board))

    def successors(self):
        for i in range(self.row):
            for j in range(self.col):
                temp_puzzle = self.copy()
                temp_puzzle.perform_move(i, j)
                yield (i, j), temp_puzzle

    def find_solution(self):
        # BFS graph search is implemented via a queue
        queue = [self]
        visited = {}
        optimal_sol = []
        while True:
            if not queue:
                return None
            board_state = queue.pop(0)
            for move, new_puzzle in board_state.successors():
                # using hint to optimize checking of visited board states to near-constant time
                board = tuple(tuple(row) for row in new_puzzle.board)
                if board in visited:
                    continue
                else:
                    visited[board] = [move]
                if new_puzzle.is_solved():  # board is solvable
                    while new_puzzle.board != self.board:
                        temp_board = tuple(tuple(row) for row in new_puzzle.board)
                        optimal_sol = visited[temp_board] + optimal_sol
                        new_puzzle.perform_move(optimal_sol[0][0], optimal_sol[0][1])
                    return optimal_sol
                queue.append(new_puzzle)  # add puzzle to queue if it does not coincide with a visited board state


def create_puzzle(rows, cols):
    return LightsOutPuzzle([[False] * cols for i in range(rows)])


############################################################
# Section 3: Linear Disk Movement
############################################################


def solve_identical_disks(length, n):
    grid = LinearDiskPuzzle(length, n, 0)
    queue = [grid]
    visited = {}
    optimal_sol = []
    if grid.is_identically_solved():
        return optimal_sol
    while True:
        grid_state = queue.pop(0)
        for move, new_grid in grid_state.successors():
            g = tuple(new_grid.linear_grid)
            if g in visited:
                continue
            else:
                visited[g] = [move]
            if new_grid.is_identically_solved():
                while new_grid.linear_grid != grid.linear_grid:
                    temp_grid = tuple(new_grid.linear_grid)
                    optimal_sol = visited[temp_grid] + optimal_sol
                    new_grid.grid_move(optimal_sol[0][1], optimal_sol[0][0] - optimal_sol[0][1])
                return optimal_sol
            queue.append(new_grid)


def solve_distinct_disks(length, n):
    grid = LinearDiskPuzzle(length, n, 0)
    queue = [grid]
    visited = {}
    optimal_sol = []
    if grid.is_distinctly_solved():
        return optimal_sol
    while True:
        if not queue:
            return None
        grid_state = queue.pop(0)
        for move, new_grid in grid_state.successors():
            g = tuple(new_grid.linear_grid)
            if g in visited:
                continue
            else:
                visited[g] = [move]
            if new_grid.is_distinctly_solved():
                while new_grid.linear_grid != grid.linear_grid:
                    temp_grid = tuple(new_grid.linear_grid)
                    optimal_sol = visited[temp_grid] + optimal_sol
                    new_grid.grid_move(optimal_sol[0][1], optimal_sol[0][0] - optimal_sol[0][1])
                return optimal_sol
            queue.append(new_grid)


class LinearDiskPuzzle(object):
    def __init__(self, L, n, linear_grid):
        self.L = L
        self.n = n
        # enumerate the first n positions with the disk 'id's and set the remaining L-n positions with -1
        if not linear_grid:
            self.linear_grid = [m for m in range(n)] + [-1] * (L - n)
        elif len(linear_grid) == L:
            self.linear_grid = linear_grid
        else:
            return

    def grid_move(self, steps, spaces):
        if (spaces + steps) < 0 or (spaces + steps) >= self.L:
            return
        self.linear_grid[spaces + steps] = self.linear_grid[steps]
        self.linear_grid[steps] = -1

    def is_identically_solved(
            self):  # For identical disks case, goal is reached when all disks are in the last n places
        for i in range(self.L - self.n, self.L):
            if self.linear_grid[i] == -1:
                return False
        return True

    def is_distinctly_solved(
            self):  # For distinct case, goal is reached when i th disk is in the L-i th place, for all i
        for i in range(self.L - self.n, self.L):
            if self.linear_grid[i] != self.L - i - 1:
                return False
        return True

    def copy(self):
        return LinearDiskPuzzle(copy.deepcopy(self.L), copy.deepcopy(self.n), copy.deepcopy(self.linear_grid))

    def successors(self):
        for i in range(self.L):
            if (i - 2) >= 0 and self.linear_grid[i] != -1 and self.linear_grid[i - 1] != -1 and self.linear_grid[
                i - 2] == -1:
                temp_grid = self.copy()
                temp_grid.grid_move(i, -2)
                yield (i, i - 2), temp_grid
            if (i - 1) >= 0 and self.linear_grid[i] != -1 and self.linear_grid[i - 1] == -1:
                temp_grid = self.copy()
                temp_grid.grid_move(i, -1)
                yield (i, i - 1), temp_grid
            if (i + 1) < self.L and self.linear_grid[i] != -1 and self.linear_grid[i + 1] == -1:
                temp_grid = self.copy()
                temp_grid.grid_move(i, 1)
                yield (i, i + 1), temp_grid
            if (i + 2) < self.L and self.linear_grid[i] != -1 and self.linear_grid[i + 1] != -1 and self.linear_grid[
                i + 2] == -1:
                temp_grid = self.copy()
                temp_grid.grid_move(i, 2)
                yield (i, i + 2), temp_grid
