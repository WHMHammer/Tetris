# author: WHMHammer @ GitHub
# email: whmhammer@gmail.com

from tkinter import Event, Frame, Label, N, Tk
from typing import List

from model import Tetrimino
from view_base import TetrisViewBase
from view_model import NEXT_TETRIMINO_N, TetrisViewModel, TETRIS_COL_N, TETRIS_ROW_N

COLOR_SCHEME = {
    "": "#bfbfbf",  # background
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


class SquareFrame(Frame):
    def __init__(self, master: Frame, size: int = 32, shape: str = ""):
        super().__init__(
            master,
            bg=COLOR_SCHEME[shape],
            highlightbackground=COLOR_SCHEME["border"],
            highlightthickness=1,
            height=size,
            width=size
        )


class TetriminoFrame(Frame):
    def __init__(self, master, shape):
        super().__init__(master)
        if shape == "I":
            SquareFrame(self, size=16, shape="I").grid(row=0, column=0)
            SquareFrame(self, size=16, shape="I").grid(row=0, column=1)
            SquareFrame(self, size=16, shape="I").grid(row=0, column=2)
            SquareFrame(self, size=16, shape="I").grid(row=0, column=3)
        elif shape == "J":
            SquareFrame(self, size=16, shape="J").grid(row=0, column=1)
            SquareFrame(self, size=16, shape="J").grid(row=1, column=1)
            SquareFrame(self, size=16, shape="J").grid(row=2, column=0)
            SquareFrame(self, size=16, shape="J").grid(row=2, column=1)
        elif shape == "L":
            SquareFrame(self, size=16, shape="L").grid(row=0, column=0)
            SquareFrame(self, size=16, shape="L").grid(row=1, column=0)
            SquareFrame(self, size=16, shape="L").grid(row=2, column=0)
            SquareFrame(self, size=16, shape="L").grid(row=2, column=1)
        elif shape == "O":
            SquareFrame(self, size=16, shape="O").grid(row=0, column=0)
            SquareFrame(self, size=16, shape="O").grid(row=0, column=1)
            SquareFrame(self, size=16, shape="O").grid(row=1, column=0)
            SquareFrame(self, size=16, shape="O").grid(row=1, column=1)
        elif shape == "S":
            SquareFrame(self, size=16, shape="S").grid(row=0, column=1)
            SquareFrame(self, size=16, shape="S").grid(row=0, column=2)
            SquareFrame(self, size=16, shape="S").grid(row=1, column=0)
            SquareFrame(self, size=16, shape="S").grid(row=1, column=1)
        elif shape == "T":
            SquareFrame(self, size=16, shape="T").grid(row=0, column=0)
            SquareFrame(self, size=16, shape="T").grid(row=0, column=1)
            SquareFrame(self, size=16, shape="T").grid(row=0, column=2)
            SquareFrame(self, size=16, shape="T").grid(row=1, column=1)
        elif shape == "Z":
            SquareFrame(self, size=16, shape="Z").grid(row=0, column=0)
            SquareFrame(self, size=16, shape="Z").grid(row=0, column=1)
            SquareFrame(self, size=16, shape="Z").grid(row=1, column=1)
            SquareFrame(self, size=16, shape="Z").grid(row=1, column=2)


class TetrisViewTk(Tk, TetrisViewBase):
    def __init__(self):
        # visuals
        super().__init__()
        self.title("Tetris")
        self.resizable(0, 0)

        # left frame
        self.left_frame: Frame = Frame(self)
        self.left_frame.grid(row=0, column=0, sticky=N)

        # score labels
        Label(self.left_frame, text="Score:", width=8).grid(row=0, column=0)
        self.score_label: Label = Label(self.left_frame, text="0", width=8)
        self.score_label.grid(row=1, column=0)

        # spacer
        Frame(self.left_frame, height=16).grid(row=2, column=0)

        # held label
        Label(self.left_frame, text="Hold:", width=8).grid(row=3, column=0)

        # held frame
        self.held_frame: TetriminoFrame = TetriminoFrame(self.left_frame, "")
        self.held_frame.grid(row=4, column=0)

        # spacer between the left frame and the centre frame
        Frame(self, width=16).grid(row=0, column=1)

        # centre frame
        centre_frame = Frame(
            self,
            bg=COLOR_SCHEME[""],
            highlightbackground=COLOR_SCHEME["border"],
            highlightthickness=1,
        )
        centre_frame.grid(row=0, column=2, sticky=N)

        # square frames
        self.square_frames: List[List[Frame]] = []
        for i in range(TETRIS_ROW_N):
            self.square_frames.append([])
            for j in range(TETRIS_COL_N):
                self.square_frames[i].append(SquareFrame(centre_frame))
                self.square_frames[i][j].grid(row=i, column=j)

        # spacer between the centre frame and the right frame
        Frame(self, width=16).grid(row=0, column=3)

        # right frame
        self.right_frame: Frame = Frame(self)
        self.right_frame.grid(row=0, column=4, sticky=N)

        # next label
        Label(self.right_frame, text="Next:", width=8).grid(row=0, column=0)

        # next frames
        self.next_frames: List[TetriminoFrame] = []
        for i in range(NEXT_TETRIMINO_N):
            self.next_frames.append(
                TetriminoFrame(self.right_frame, "")
            )
            self.next_frames[i].grid(row=2*i+1, column=0)
            # spacer
            Frame(self.right_frame, height=16).grid(row=2*i+2, column=0)

        # internal variables
        self.current_squares: List[List[int]] = tuple()
        self.shadow_squares: List[List[int]] = tuple()
        self.view_model: TetrisViewModel = TetrisViewModel(self)

        # start
        self.bind("<Key>", self.on_key_press)
        self.focus_set()
        self.mainloop()

    def on_key_press(self, event: Event):
        if event.keysym == "w":
            self.view_model.drop()
        elif event.keysym == "a":
            self.view_model.move_left()
        elif event.keysym == "s":
            self.view_model.move_down()
        elif event.keysym == "d":
            self.view_model.move_right()
        elif event.keysym == "space":
            self.view_model.rotate_clockwise()
        elif event.keysym == "Shift_L":
            self.view_model.rotate_counterclockwise()
        elif event.keysym == "h":
            self.view_model.hold()
        elif event.keysym == "p":
            self.view_model.toggle_pause()

    def refresh_board(self, board: List[List[str]]):
        for x in range(TETRIS_ROW_N):
            for y in range(TETRIS_COL_N):
                self.square_frames[x][y].config(bg=COLOR_SCHEME[board[x][y]])

    def refresh_current(self, tetrimino: Tetrimino, shadow: List[int], board: List[List[int]]):
        if board is None:
            for x, y in self.current_squares:
                self.square_frames[x][y].config(bg=COLOR_SCHEME[""])
        if shadow is not None:
            if board is None:
                for (i, j) in self.shadow_squares:
                    self.square_frames[i][j].config(bg=COLOR_SCHEME[""])
            self.shadow_squares = []
            for x, y in tetrimino.layout.layout:
                x += shadow[0]
                y += shadow[1]
                self.shadow_squares.append((x, y))
                self.square_frames[x][y].config(bg=COLOR_SCHEME["shadow"])
        self.current_squares = []
        for x, y in tetrimino.layout.layout:
            x += tetrimino.position[0]
            y += tetrimino.position[1]
            self.current_squares.append((x, y))
            self.square_frames[x][y].config(bg=COLOR_SCHEME[tetrimino.shape])

    def refresh_next(self, shapes: List[str]):
        for i in range(NEXT_TETRIMINO_N):
            self.next_frames[i].destroy()
            self.next_frames[i] = TetriminoFrame(self.right_frame, shapes[i])
            self.next_frames[i].grid(row=2*i+1)

    def refresh_held(self, shape: str):
        self.held_frame.destroy()
        self.held_frame = TetriminoFrame(self.left_frame, shape)
        self.held_frame.grid(row=4, column=0)

    def refresh_score(self, score: int):
        self.score_label.config(text=str(score))

    def refresh(
        self,
        board: List[List[str]] = None,
        current: Tetrimino = None,
        shadow: List[int] = None,
        next: List[str] = None,
        held: str = None,
        score: int = None
    ):
        if board is not None:
            self.refresh_board(board)
        if current is not None:
            self.refresh_current(current, shadow, board)
        if next is not None:
            self.refresh_next(next)
        if held is not None:
            self.refresh_held(held)
        if score is not None:
            self.refresh_score(score)
