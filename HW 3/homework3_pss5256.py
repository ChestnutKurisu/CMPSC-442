############################################################
# CMPSC 442: Homework 3
############################################################

student_name = "Param Somane"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.

import itertools
import math
import random
from queue import PriorityQueue


############################################################
# Section 1: Tile Puzzle
############################################################

def create_tile_puzzle(rows, cols):
    new_board = []
    count = 1
    for i in range(rows):
        new_board.append(list(range(i * cols + 1, (i + 1) * cols + 1)))
    new_board[rows - 1][cols - 1] = 0
    return TilePuzzle(new_board)


class TilePuzzle(object):

    # Required
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])
        # Finding and storing the empty tile
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 0:
                    self.empty_tile = (i, j)
                    break

    def get_board(self):
        return self.board

    def perform_move(self, direction):
        (i, j) = self.empty_tile
        # Checking if movement is valid
        if (direction == 'up' and i == 0) or (direction == 'down' and i == self.rows - 1) or (
                direction == 'left' and j == 0) or (direction == 'right' and j == self.cols - 1):
            return False
        if direction == 'up':
            temp = self.board[i - 1][j]
            self.board[i - 1][j] = self.board[i][j]
            self.board[i][j] = temp
            self.empty_tile = (i - 1, j)
            return True
        elif direction == 'down':
            temp = self.board[i + 1][j]
            self.board[i + 1][j] = self.board[i][j]
            self.board[i][j] = temp
            self.empty_tile = (i + 1, j)
            return True
        elif direction == 'left':
            temp = self.board[i][j - 1]
            self.board[i][j - 1] = self.board[i][j]
            self.board[i][j] = temp
            self.empty_tile = (i, j - 1)
            return True
        elif direction == 'right':
            temp = self.board[i][j + 1]
            self.board[i][j + 1] = self.board[i][j]
            self.board[i][j] = temp
            self.empty_tile = (i, j + 1)
            return True
        # Direction is invalid
        return False

    def scramble(self, num_moves):
        valid_directions = ['up', 'down', 'left', 'right']
        for i in range(num_moves):
            self.perform_move(random.choice(valid_directions))

    def is_solved(self):
        starting_board = create_tile_puzzle(self.rows, self.cols)
        return starting_board.get_board() == self.board

    def copy(self):
        return TilePuzzle([row[:] for row in self.board])

    def successors(self):
        valid_directions = ['up', 'down', 'left', 'right']
        for direction in valid_directions:
            next_move_state = self.copy()
            if next_move_state.perform_move(direction):
                yield direction, next_move_state

    # Required
    def iddfs_helper(self, limit, moves):
        if self.is_solved():
            yield moves
        elif len(moves) < limit:
            for successor in self.successors():
                for solution in successor[1].iddfs_helper(limit, moves + [successor[0]]):
                    yield solution

    def find_solutions_iddfs(self):
        limit = 0
        while True:
            solutions = list(self.iddfs_helper(limit, []))
            if len(solutions) > 0:
                for solution in solutions:
                    yield solution
                break
            limit += 1

    def puzzle_heuristic(self):
        return sum((abs(i - (self.board[i][j] - 1) // self.cols) + abs(
            j - (self.board[i][j] - self.cols * ((self.board[i][j] - 1) // self.cols) - 1))) for (i, j) in
                   itertools.product(list(range(self.rows)), list(range(self.cols)))) + abs(
            self.rows - 1 - self.empty_tile[0]) + abs(self.cols - 1 - self.empty_tile[1]) - abs(
            self.empty_tile[0] - (self.board[self.empty_tile[0]][self.empty_tile[1]] - 1) // self.cols) - abs(
            self.empty_tile[1] - (self.board[self.empty_tile[0]][self.empty_tile[1]] - self.cols * (
                    (self.board[self.empty_tile[0]][self.empty_tile[1]] - 1) // self.cols)))

    # Required
    def find_solution_a_star(self):
        PQ = PriorityQueue()
        PQ.put((self.puzzle_heuristic(), [], self.copy()))
        visited_moves = [self.board]
        while PQ.qsize() != 0:
            estimated_total_cost, solution, puzzle = PQ.get()
            if puzzle.is_solved():
                return solution
            for direction, next_move_state in puzzle.successors():
                if next_move_state.get_board() not in visited_moves:
                    visited_moves.append(puzzle.board)
                    cost_so_far = len(solution)
                    estimated_cost = 1 + next_move_state.puzzle_heuristic()
                    PQ.put((cost_so_far + estimated_cost, solution + [direction], next_move_state))


############################################################
# Section 2: Grid Navigation
############################################################

def get_successors(position, scene):
    x, y = position
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if 0 <= i < len(scene) and 0 <= j < len(scene[0]) and not scene[i][j]:
                yield i, j


# Straight-line Euclidean distance heuristic
def grid_heuristic(start, goal):
    return math.sqrt((start[0] - goal[0]) ** 2 + (start[1] - goal[1]) ** 2)


def find_path(start, goal, scene):
    # Start or goal coincides with an obstacle
    if scene[start[0]][start[1]] or scene[goal[0]][goal[1]]:
        return None
    # A* search
    PQ = PriorityQueue()
    PQ.put((grid_heuristic(start, goal), 0, [start], start))
    visited = set()
    while not PQ.empty():
        estimated_cost, cost_so_far, solution, position = PQ.get()
        if position in visited:
            continue
        else:
            visited.add(position)
        if position == goal:
            return solution
        for new_position in get_successors(position, scene):
            if new_position not in visited:
                PQ.put((cost_so_far + grid_heuristic(position, new_position) + grid_heuristic(new_position, goal),
                        cost_so_far + grid_heuristic(position, new_position),
                        solution + [new_position], new_position))
    return None


############################################################
# Section 3: Linear Disk Movement, Revisited
############################################################


def distinct_successors(grid_state):
    for i in range(len(grid_state)):
        next_state = grid_state[:]
        if grid_state[i] == -1:
            continue
        for j in range(-2, 3):
            if j == 0:
                continue
            if j <= i < len(grid_state) + j and grid_state[i - j] == -1:
                if j == -2 and grid_state[i + 1] == -1:
                    continue
                if j == 2 and grid_state[i - 1] == -1:
                    continue
                next_state[i] = -1
                next_state[i - j] = grid_state[i]
                yield (i, i - j), next_state[:]
                next_state = grid_state[:]


def disk_heuristic(grid):
    return sum(
        0 if grid[position] == -1 else abs(len(grid) - grid[position] - position - 1) for position in range(len(grid)))


def solve_distinct_disks(length, n):
    initial = list(range(n)) + [-1] * (length - n)
    goal = [-1] * (length - n) + list(range(n-1, -1, -1))
    PQ = PriorityQueue()
    PQ.put((disk_heuristic(initial), [], initial))
    visited = [initial]
    while PQ.qsize() != 0:
        heuristic, solution, state = PQ.get()
        if state == goal:
            return solution
        for next_move, grid_state in distinct_successors(state):
            if grid_state not in visited:
                visited.append(grid_state)
                PQ.put((1 + disk_heuristic(grid_state) + len(solution), solution + [next_move], grid_state))


############################################################
# Section 4: Dominoes Game
############################################################

def create_dominoes_game(rows, cols):
    return DominoesGame([[False] * cols for i in range(rows)])


class DominoesGame(object):
    # Required
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])
        self.best_move = None

    def get_board(self):
        return self.board

    def reset(self):
        self.board = [[False] * self.cols] * self.rows

    def is_legal_move(self, row, col, vertical):
        # Dominoes fully within bounds
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        # Dominoes should not cover squares which have already been filled
        if self.board[row][col]:
            return False
        if vertical and (row >= self.rows - 1 or self.board[row + 1][col]):
            return False
        if not vertical and (col >= self.cols - 1 or self.board[row][col + 1]):
            return False
        return True

    def legal_moves(self, vertical):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.is_legal_move(i, j, vertical):
                    yield i, j

    def perform_move(self, row, col, vertical):
        if self.is_legal_move(row, col, vertical):
            self.board[row][col] = True
            if vertical:
                self.board[row + 1][col] = True
            else:
                self.board[row][col + 1] = True

    def game_over(self, vertical):
        return len(list(self.legal_moves(vertical))) == 0

    def copy(self):
        return DominoesGame([row[:] for row in self.board])

    def successors(self, vertical):
        for (i, j) in self.legal_moves(vertical):
            new_game = self.copy()
            new_game.perform_move(i, j, vertical)
            yield (i, j), new_game

    def get_random_move(self, vertical):
        return random.choice(list(self.legal_moves(vertical)))

    # Required
    def get_best_move(self, vertical, limit):
        return self.max_value(vertical, limit, [], float('-inf'), float('inf'))

    def max_value(self, vertical, limit, state, alpha, beta):
        vertical_successors = list(self.successors(vertical))
        horizontal_successors = list(self.successors(not vertical))
        # Return utility value if terminal test successful
        if limit == 0 or self.game_over(vertical):
            return state, len(vertical_successors) - len(horizontal_successors), 1
        v = float('-inf')
        c = 0
        current_move = state
        for pos, succ in vertical_successors:
            move, min_val, previous_count = succ.min_value(not vertical, limit - 1, pos, alpha, beta)
            c += previous_count
            if min_val > v:
                v = min_val
                current_move = pos
            if v >= beta:
                return current_move, v, c
            alpha = max(alpha, v)
        return current_move, v, c

    def min_value(self, vertical, limit, state, alpha, beta):
        vertical_successors = list(self.successors(vertical))
        horizontal_successors = list(self.successors(not vertical))
        # Return utility value if terminal test successful
        if limit == 0 or self.game_over(vertical):
            return state, len(horizontal_successors) - len(vertical_successors), 1
        v = float('inf')
        c = 0
        current_move = state
        for pos, succ in vertical_successors:
            move, max_val, previous_count = succ.max_value(not vertical, limit - 1, pos, alpha, beta)
            c += previous_count
            if max_val < v:
                v = max_val
                current_move = pos
            if v <= alpha:
                return current_move, v, c
            beta = min(beta, v)
        return current_move, v, c
