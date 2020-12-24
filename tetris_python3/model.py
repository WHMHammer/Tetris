# author: WHMHammer @ GitHub
# email: whmhammer@gmail.com

# this module is thread-unsafe

from random import choice
from typing import List

TETRIS_ROW_N = 20
TETRIS_COL_N = 10
NEXT_TETRIMINO_N = 6


class Layout:
    def __init__(self, layout: List[List[int]], prev=None, next=None):
        self.layout: List[List[int]] = layout
        if prev is None:
            self.prev: Layout = self
        else:
            self.prev: Layout = prev
        if next is None:
            self.next: Layout = self
        else:
            self.next: Layout = next


class Tetrimino:
    ALL_SHAPES = "IJLOSTZ"

    @classmethod
    def random_shape(self) -> str:
        return choice(self.ALL_SHAPES)

    def __init__(self, shape: str = None):
        # shape
        if shape is None:
            shape = self.random_shape()
        self.shape: str = shape

        # position
        self.position: List[int] = [0, 3]

        # layout
        if shape == "I":
            self.layout: Layout = Layout(((1, 0), (1, 1), (1, 2), (1, 3)))
            self.layout.next = Layout(
                ((0, 1), (1, 1), (2, 1), (3, 1)),
                prev=self.layout
            )
            self.layout.next.next = Layout(
                ((1, -1), (1, 0), (1, 1), (1, 2)),
                prev=self.layout.next
            )
            self.layout.next.next.next = Layout(
                ((-1, 1), (0, 1), (1, 1), (2, 1)),
                prev=self.layout.next.next,
                next=self.layout
            )
            self.layout.prev = self.layout.next.next.next
        elif shape == "J":
            self.layout: Layout = Layout(((0, 0), (1, 0), (1, 1), (1, 2)))
            self.layout.next = Layout(
                ((0, 1), (0, 2), (1, 1), (2, 1)),
                prev=self.layout
            )
            self.layout.next.next = Layout(
                ((1, 0), (1, 1), (1, 2), (2, 2)),
                prev=self.layout.next
            )
            self.layout.next.next.next = Layout(
                ((0, 1), (1, 1), (2, 0), (2, 1)),
                prev=self.layout.next.next,
                next=self.layout
            )
            self.layout.prev = self.layout.next.next.next
        elif shape == "L":
            self.layout: Layout = Layout(((0, 2), (1, 0), (1, 1), (1, 2)))
            self.layout.next = Layout(
                ((0, 1), (1, 1), (2, 1), (2, 2)),
                prev=self.layout
            )
            self.layout.next.next = Layout(
                ((1, 0), (1, 1), (1, 2), (2, 0)),
                prev=self.layout.next
            )
            self.layout.next.next.next = Layout(
                ((0, 0), (0, 1), (1, 1), (2, 1)),
                prev=self.layout.next.next,
                next=self.layout
            )
            self.layout.prev = self.layout.next.next.next
        elif shape == "O":
            self.layout: Layout = Layout(((0, 1), (0, 2), (1, 1), (1, 2)))
        elif shape == "S":
            self.layout: Layout = Layout(((0, 1), (0, 2), (1, 0), (1, 1)))
            self.layout.next = Layout(
                ((0, 1), (1, 1), (1, 2), (2, 2)),
                prev=self.layout
            )
            self.layout.next.next = Layout(
                ((1, 1), (1, 2), (2, 0), (2, 1)),
                prev=self.layout.next
            )
            self.layout.next.next.next = Layout(
                ((0, 0), (1, 0), (1, 1), (2, 1)),
                prev=self.layout.next.next,
                next=self.layout
            )
            self.layout.prev = self.layout.next.next.next
        elif shape == "T":
            self.layout: Layout = Layout(((0, 1), (1, 0), (1, 1), (1, 2)))
            self.layout.next = Layout(
                ((0, 1), (1, 1), (1, 2), (2, 1)),
                prev=self.layout
            )
            self.layout.next.next = Layout(
                ((1, 0), (1, 1), (1, 2), (2, 1)),
                prev=self.layout.next
            )
            self.layout.next.next.next = Layout(
                ((0, 1), (1, 0), (1, 1), (2, 1)),
                prev=self.layout.next.next,
                next=self.layout
            )
            self.layout.prev = self.layout.next.next.next
        else:  # shape == "Z"
            self.layout: Layout = Layout(((0, 0), (0, 1), (1, 1), (1, 2)))
            self.layout.next = Layout(
                ((0, 2), (1, 1), (1, 2), (2, 1)),
                prev=self.layout
            )
            self.layout.next.next = Layout(
                ((1, 0), (1, 1), (2, 1), (2, 2)),
                prev=self.layout.next
            )
            self.layout.next.next.next = Layout(
                ((0, 1), (1, 0), (1, 1), (2, 0)),
                prev=self.layout.next.next,
                next=self.layout
            )
            self.layout.prev = self.layout.next.next.next


class TetrisModel:
    def __init__(self):
        # board
        self.board: List[List[str]] = []
        for i in range(TETRIS_ROW_N):
            self.board.append([])
            for j in range(TETRIS_COL_N):
                self.board[i].append("")

        # current
        self.current: Tetrimino = Tetrimino()

        # next
        self.next: List[str] = []
        for i in range(NEXT_TETRIMINO_N):
            self.next.append(Tetrimino.random_shape())

        # held
        self.held: str = None
        self.has_held: bool = False

        # score
        self.score: int = 0

        # misc
        self.is_over: bool = False

    def check(self, position: List[int]) -> bool:
        # check whether the given position (of the current tetrimino) is legal
        if self.is_over:
            return

        for x, y in self.current.layout.layout:
            x += position[0]
            y += position[1]
            if x < 0 or x >= TETRIS_ROW_N or y < 0 or y >= TETRIS_COL_N or self.board[x][y]:
                return False
        return True

    def calculate_shadow(self) -> List[List[int]]:
        # calculate the position of the shadow
        if self.is_over:
            return
        x = self.current.position[0]
        while self.check((x, self.current.position[1])):
            x += 1
        return x-1, self.current.position[1]

    def move_down(self) -> bool:
        # move the current tetrimino down by 1 row
        # return True if the board is updated
        # return False otherwise
        if self.is_over:
            return

        self.current.position[0] += 1
        if self.check(self.current.position):
            # the board is not updated
            return False

        # the board is updated
        # board
        for x, y in self.current.layout.layout:
            self.board[
                x+self.current.position[0]-1
            ][
                y + self.current.position[1]
            ] = self.current.shape

        # current
        self.current = Tetrimino(self.next[0])

        # next
        for i in range(NEXT_TETRIMINO_N-1):
            self.next[i] = self.next[i+1]
        self.next[-1] = Tetrimino.random_shape()

        # held
        self.has_held = False

        # score
        offset = 0
        for x in range(TETRIS_ROW_N-1, -1, -1):
            for y in range(TETRIS_COL_N):
                if not self.board[x][y]:  # self.board == ""
                    break
            else:
                offset += 1
                continue
            if offset:  # offset != 0
                for y in range(TETRIS_COL_N):
                    self.board[x + offset][y] = self.board[x][y]
        if offset:  # offset != 0
            for x in range(offset):
                for y in range(TETRIS_COL_N):
                    self.board[x][y] = ""
            self.score += offset

        # misc
        self.is_over = not self.check(self.current.position)

        return True

    def drop(self) -> None:
        # drop the current tetrimino to the bottom of the board
        if self.is_over:
            return

        self.current.position = list(self.calculate_shadow())
        self.move_down()

    def move_left(self) -> bool:
        # move the current tetrimino left by 1 column
        # return True if the movement is legal
        # return False otherwise
        if self.is_over:
            return

        self.current.position[1] -= 1
        if self.check(self.current.position):
            # the movement is legal
            return True

        # the movement is illegal
        self.current.position[1] += 1
        return False

    def move_right(self) -> bool:
        # move the current tetrimino right  by 1 column
        # return True if the movement is legal
        # return False otherwise
        if self.is_over:
            return

        self.current.position[1] += 1
        if self.check(self.current.position):
            # the movement is legal
            return True

        # the movement is illegal
        self.current.position[1] -= 1
        return False

    def rotate_clockwise(self) -> bool:
        # rotate the current tetrimino clockwise by 90 degrees
        # return True if the rotation is legal
        # return False otherwise
        if self.is_over:
            return

        self.current.layout = self.current.layout.next
        if self.check(self.current.position):
            # the rotation is legal
            return True

        # the rotation is illegal
        self.current.layout = self.current.layout.prev
        return False

    def rotate_counterclockwise(self) -> bool:
        # rotate the current tetrimino counterclockwise by 90 degrees
        # return True if the rotation is legal
        # return False otherwise
        if self.is_over:
            return

        self.current.layout = self.current.layout.prev
        if self.check(self.current.position):
            # the rotation is legal
            return True

        # the rotation is illegal
        self.current.layout = self.current.layout.next
        return False

    def hold(self) -> bool:
        # hold the current tetrimino
        # change the current tetrimino to the previously-held one, and return True
        # move on to the next tetrimino if there is none held, and return False
        if self.is_over or self.has_held:
            return
        self.has_held = True

        if self.held is None:
            self.held = self.current.shape
            self.current = Tetrimino(self.next[0])
            for i in range(NEXT_TETRIMINO_N-1):
                self.next[i] = self.next[i+1]
                self.next[-1] = Tetrimino.random_shape()
            return False

        shape = self.held
        self.held = self.current.shape
        self.current = Tetrimino(shape)
        return True
