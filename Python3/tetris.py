import sqlite3 as sql
import tkinter as tk

from random import choice
from threading import Thread
from time import sleep

COLOR_SCHEME = {
    "background": "#bfbfbf",
    "border": "#3f3f3f",
    "shadow": "#7f7f7f",
    "I": "#ff0000",
    "J": "#ff6600",
    "L": "#ffee00",
    "O": "#00ff00",
    "S": "#00ffff",
    "T": "#0000ff",
    "Z": "#9900ff"
}

class Tetris(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tetris - WHMHammer")
        self.resizable(0,0)

        self.board_frame = tk.Frame(
            self,
            bg = COLOR_SCHEME["background"],
            highlightbackground = COLOR_SCHEME["border"],
            highlightthickness = 1,
        )
        self.board = []
        for i in range(20):
            self.board.append([])
            for j in range(10):
                self.board[i].append(Square(self.board_frame))
                self.board[i][j].grid(row = i, column = j)
        self.board_frame.grid(row = 0, column = 0)

        tk.Frame(self, width = 32).grid(row = 0, column = 1)

        self.info_frame = tk.Frame(self)
        self.next_tetrimino_squares = []
        for i in range(2):
            self.next_tetrimino_squares.append([])
            for j in range(4):
                self.next_tetrimino_squares[i].append(Square(self.info_frame))
                self.next_tetrimino_squares[i][j].grid(row = i, column = j)
        self.scoreboard = tk.Label(self.info_frame, text="Score: 0")
        self.scoreboard.grid(row = 2, column = 0, columnspan = 4)
        self.info_frame.grid(row = 0, column = 2, sticky = tk.N)

        self.score = 0

        self.current_tetrimino = Tetrimino(choice("IJLOSTZ"))
        self.next_tetrimino = Tetrimino(choice("IJLOSTZ"))
        self.shadow_position = [0,3]
        self.refresh_shadow()

        self.display()
        self.display_next()

        self.bind("<Key>", self.onkeypress)
        self.focus_set()
        Autofall(self)
        self.mainloop()

    def refresh_shadow(self):
        self.shadow_position = list(self.current_tetrimino.position)
        while self.test(position = self.shadow_position):
            self.shadow_position[0] += 1
        self.shadow_position[0] -= 1
        self.display(color = COLOR_SCHEME["shadow"], position = self.shadow_position)

    def display(self, color = None, position = None):
        if color is None:
            color = self.current_tetrimino.color
        if position is None:
            position = self.current_tetrimino.position
        for rel in self.current_tetrimino.squares[self.current_tetrimino.orientation]:
            self.board[position[0]+rel[0]][position[1]+rel[1]].config(bg = color)

    def display_next(self):
        for i in range(2):
            for j in range(4):
                self.next_tetrimino_squares[i][j].config(bg = self.next_tetrimino.color if (i,j) in self.next_tetrimino.squares[0] else COLOR_SCHEME["background"])

    def onkeypress(self, event = None):
        try:
            {
                "w": self.rotate,
                "a": self.move_left,
                "s": self.move_down,
                "d": self.move_right,
                " ": self.drop
            }[event.char]()
        except KeyError:
            pass

    def rotate(self):
        orientation = 0 if self.current_tetrimino.orientation+1 == self.current_tetrimino.orientations else self.current_tetrimino.orientation+1
        if self.test(orientation = orientation):
            self.display(color = COLOR_SCHEME["background"], position = self.shadow_position)
            self.display(COLOR_SCHEME["background"])
            self.current_tetrimino.orientation = orientation
            self.refresh_shadow()
            self.display()

    def move_left(self):
        position = (self.current_tetrimino.position[0], self.current_tetrimino.position[1]-1)
        if self.test(position = position):
            self.display(color = COLOR_SCHEME["background"], position = self.shadow_position)
            self.display(color = COLOR_SCHEME["background"])
            self.current_tetrimino.position = position
            self.refresh_shadow()
            self.display()

    def move_down(self):
        position = (self.current_tetrimino.position[0]+1, self.current_tetrimino.position[1])
        if self.test(position = position):
            self.display(COLOR_SCHEME["background"])
            self.current_tetrimino.position = position
            self.display()
            return
        for position in self.current_tetrimino.squares[self.current_tetrimino.orientation]:
            self.board[self.current_tetrimino.position[0]+position[0]][self.current_tetrimino.position[1]+position[1]].shape = self.current_tetrimino.shape
        line_clear = 0
        i = 19
        while i >= line_clear:
            for j in range(10):
                if self.board[i][j].shape == "background":
                    break
            else:
                line_clear += 1
                for j in range(i,0,-1):
                    for k in range(10):
                        self.board[j][k].shape = self.board[j-1][k].shape
                        self.board[j][k].config(bg = COLOR_SCHEME[self.board[j][k].shape])
                for j in range(10):
                    self.board[0][j].shape = "background"
                continue
            i -= 1
        if line_clear != 0:
            self.score += 2*line_clear-1
        self.scoreboard.config(text = f"Score: {self.score}")
        self.current_tetrimino = self.next_tetrimino
        self.next_tetrimino = Tetrimino(choice("IJLOSTZ"))
        self.refresh_shadow()
        self.display()
        self.display_next()

    def move_right(self):
        position = (self.current_tetrimino.position[0], self.current_tetrimino.position[1]+1)
        if self.test(position = position):
            self.display(color = COLOR_SCHEME["background"], position = self.shadow_position)
            self.display(COLOR_SCHEME["background"])
            self.current_tetrimino.position = position
            self.refresh_shadow()
            self.display()

    def drop(self):
        self.display(color = COLOR_SCHEME["background"])
        self.current_tetrimino.position = tuple(self.shadow_position)
        self.display()

    def test(self, orientation = None, position = None):
        if orientation is None:
            orientation = self.current_tetrimino.orientation
        if position is None:
            position = self.current_tetrimino.position
        for i in range(4):
            square_position = (self.current_tetrimino.squares[orientation][i][0]+position[0],self.current_tetrimino.squares[orientation][i][1]+position[1])
            if (
                square_position[0] < 0 or
                square_position[0] > 19 or
                square_position[1] < 0 or
                square_position[1] > 9 or
                self.board[square_position[0]][square_position[1]].shape != "background"
            ):
                return False
        return True

class Square(tk.Frame):
    def __init__(self, master):
        super().__init__(
            master,
            bg = COLOR_SCHEME["background"],
            highlightbackground = COLOR_SCHEME["border"],
            highlightthickness = 1,
            height = 32,
            width = 32
        )
        self.shape = "background"

class Tetrimino:
    def __init__(self, shape):
        self.shape = shape
        self.position = (0,3)
        self.orientation = 0
        {
            "I": self.init_I,
            "J": self.init_J,
            "L": self.init_L,
            "O": self.init_O,
            "S": self.init_S,
            "T": self.init_T,
            "Z": self.init_Z
        }[shape]()
        self.color = COLOR_SCHEME[shape]

    def init_I(self):
        self.orientations = 2
        self.squares = (
            ((1,0),(1,1),(1,2),(1,3)),
            ((0,1),(1,1),(2,1),(3,1))
        )

    def init_J(self):
        self.orientations = 4
        self.squares = (
            ((0,0),(1,0),(1,1),(1,2)),
            ((0,1),(0,2),(1,1),(2,1)),
            ((1,0),(1,1),(1,2),(2,2)),
            ((0,1),(1,1),(2,0),(2,1))
        )

    def init_L(self):
        self.orientations = 4
        self.squares = (
            ((0,2),(1,0),(1,1),(1,2)),
            ((0,1),(1,1),(2,1),(2,2)),
            ((1,0),(1,1),(1,2),(2,0)),
            ((0,0),(0,1),(1,1),(2,1))
        )

    def init_O(self):
        self.orientations = 1
        self.squares = (
            ((0,1),(0,2),(1,1),(1,2)),
        )

    def init_S(self):
        self.orientations = 2
        self.squares = (
            ((0,1),(0,2),(1,0),(1,1)),
            ((0,1),(1,1),(1,2),(2,2)),
        )

    def init_T(self):
        self.orientations = 4
        self.squares = (
            ((0,1),(1,0),(1,1),(1,2)),
            ((0,1),(1,1),(1,2),(2,1)),
            ((1,0),(1,1),(1,2),(2,1)),
            ((0,1),(1,0),(1,1),(2,1))
        )

    def init_Z(self):
        self.orientations = 2
        self.squares = (
            ((0,0),(0,1),(1,1),(1,2)),
            ((0,2),(1,1),(1,2),(2,1))
        )

class Autofall(Thread):
    def __init__(self, tetris):
        Thread.__init__(self)
        self.tetris = tetris
        self.start()

    def run(self):
        while self.tetris.test():
            sleep(0.009*(100-self.tetris.score)+0.1 if self.tetris.score < 100 else 0.1)
            self.tetris.move_down()
        self.tetris.unbind("<Key>")

if __name__ == "__main__":
    Tetris()
