from random import choice
from sqlite3 import connect
from threading import Condition, Semaphore, Thread
from time import sleep
from tkinter import Frame, Label, N, Tk

TETRIS_ROW_N = 20
TETRIS_COL_N = 10
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


class Tetrimino:
    def __init__(self):
        raise NotImplementedError

    def init(self):
        self.color = COLOR_SCHEME[self.shape]
        self.position = [0, 3]
        self.position_prev = (0, 3)
        self.orientation = self.orientation_init
        self.orientation_prev = self.orientation_init

    def move_down(self):
        self.position_prev = tuple(self.position)
        self.orientation_prev = self.orientation
        self.position[0] += 1

    def move_left(self):
        self.position_prev = tuple(self.position)
        self.orientation_prev = self.orientation
        self.position[1] -= 1

    def move_right(self):
        self.position_prev = tuple(self.position)
        self.orientation_prev = self.orientation
        self.position[1] += 1

    def rotate(self):
        self.position_prev = tuple(self.position)
        self.orientation_prev = self.orientation
        self.orientation = self.orientation.next

    def roll_back(self):
        self.position = list(self.position_prev)
        self.orientation = self.orientation_prev


class Orientation:
    def __init__(self, squares):
        self.squares = squares
        self.next = self


class Tetrimino_I(Tetrimino):
    orientation_init = Orientation(((1, 0), (1, 1), (1, 2), (1, 3)))
    orientation_init.next = Orientation(((0, 1), (1, 1), (2, 1), (3, 1)))
    orientation_init.next.next = orientation_init

    def __init__(self):
        self.shape = "I"
        super().init()


class Tetrimino_J(Tetrimino):
    orientation_init = Orientation(((0, 0), (1, 0), (1, 1), (1, 2)))
    orientation_init.next = Orientation(((0, 1), (0, 2), (1, 1), (2, 1)))
    orientation_init.next.next = Orientation(((1, 0), (1, 1), (1, 2), (2, 2)))
    orientation_init.next.next.next = \
        Orientation(((0, 1), (1, 1), (2, 0), (2, 1)))
    orientation_init.next.next.next.next = orientation_init

    def __init__(self):
        self.shape = "J"
        super().init()


class Tetrimino_L(Tetrimino):
    orientation_init = Orientation(((0, 2), (1, 0), (1, 1), (1, 2)))
    orientation_init.next = Orientation(((0, 1), (1, 1), (2, 1), (2, 2)))
    orientation_init.next.next = Orientation(((1, 0), (1, 1), (1, 2), (2, 0)))
    orientation_init.next.next.next = \
        Orientation(((0, 0), (0, 1), (1, 1), (2, 1)))
    orientation_init.next.next.next.next = orientation_init

    def __init__(self):
        self.shape = "L"
        super().init()


class Tetrimino_O(Tetrimino):
    orientation_init = Orientation(((0, 1), (0, 2), (1, 1), (1, 2)))

    def __init__(self):
        self.shape = "O"
        super().init()


class Tetrimino_S(Tetrimino):
    orientation_init = Orientation(((0, 1), (0, 2), (1, 0), (1, 1)))
    orientation_init.next = Orientation(((0, 1), (1, 1), (1, 2), (2, 2)))
    orientation_init.next.next = orientation_init

    def __init__(self):
        self.shape = "S"
        super().init()


class Tetrimino_T(Tetrimino):
    orientation_init = Orientation(((0, 1), (1, 0), (1, 1), (1, 2)))
    orientation_init.next = Orientation(((0, 1), (1, 1), (1, 2), (2, 1)))
    orientation_init.next.next = Orientation(((1, 0), (1, 1), (1, 2), (2, 1)))
    orientation_init.next.next.next = \
        Orientation(((0, 1), (1, 0), (1, 1), (2, 1)))
    orientation_init.next.next.next.next = orientation_init

    def __init__(self):
        self.shape = "T"
        super().init()


class Tetrimino_Z(Tetrimino):
    orientation_init = Orientation(((0, 0), (0, 1), (1, 1), (1, 2)))
    orientation_init.next = Orientation(((0, 2), (1, 1), (1, 2), (2, 1)))
    orientation_init.next.next = orientation_init

    def __init__(self):
        self.shape = "Z"
        super().init()


class Tetris(Tk):
    all_tetrimino_classes = (
        Tetrimino_I,
        Tetrimino_J,
        Tetrimino_L,
        Tetrimino_O,
        Tetrimino_S,
        Tetrimino_T,
        Tetrimino_Z
    )

    def __init__(self):
        super().__init__()
        self.title("Tetris - WHMHammer")
        self.resizable(0, 0)
        self.semaphore = Semaphore()

        self.board_frame = Frame(
            self,
            bg=COLOR_SCHEME[""],
            highlightbackground=COLOR_SCHEME["border"],
            highlightthickness=1,
        )
        self.board = []
        for i in range(TETRIS_ROW_N):
            self.board.append([])
            for j in range(TETRIS_COL_N):
                self.board[i].append(Square(self.board_frame))
                self.board[i][j].grid(row=i, column=j)
        self.board_frame.grid(row=0, column=0)

        Frame(self, width=32).grid(row=0, column=1)

        self.info_frame = Frame(self)
        self.next_tetrimino_squares = []
        for i in range(2):
            self.next_tetrimino_squares.append([])
            for j in range(4):
                self.next_tetrimino_squares[i].append(Square(self.info_frame))
                self.next_tetrimino_squares[i][j].grid(row=i, column=j)
        self.scoreboard = Label(self.info_frame, text="Score: 0")
        self.scoreboard.grid(row=2, column=0, columnspan=4)
        self.info_frame.grid(row=0, column=2, sticky=N)

        self.score = 0
        self.is_over = False
        self.is_paused = False

        self.current_tetrimino = self.new_random_tetrimino()
        self.next_tetrimino = self.new_random_tetrimino()
        self.shadow_position = (0, 3)

        self.refresh_shadow()
        self.refresh_board_display()
        self.refresh_next_tetrimino_display()

        self.bind("<Key>", self.on_key_press)
        self.focus_set()

        th = AutoMoveDownThread(self)

        self.mainloop()

        th.join()

    def new_random_tetrimino(self):
        return choice(self.all_tetrimino_classes)()

    def refresh_shadow(self):
        x0, y0 = self.shadow_position
        for x, y in self.current_tetrimino.orientation_prev.squares:
            self.board[x0+x][y0+y].config(bg=COLOR_SCHEME[""])
        x0, y0 = self.current_tetrimino.position
        while self.check(position=(x0, y0)):
            x0 += 1
        x0 -= 1
        self.shadow_position = (x0, y0)
        for x, y in self.current_tetrimino.orientation.squares:
            self.board[x0+x][y0+y].config(bg=COLOR_SCHEME["shadow"])

    def refresh_board_display(self):
        x0, y0 = self.current_tetrimino.position_prev
        for x, y in self.current_tetrimino.orientation_prev.squares:
            self.board[x0+x][y0+y].config(bg=COLOR_SCHEME[""])

        x0, y0 = self.current_tetrimino.position
        for x, y in self.current_tetrimino.orientation.squares:
            self.board[x0+x][y0+y].config(bg=self.current_tetrimino.color)

    def refresh_next_tetrimino_display(self):
        for x in range(2):
            for y in range(4):
                self.next_tetrimino_squares[x][y].config(bg=COLOR_SCHEME[""])
        for x, y in self.next_tetrimino.orientation_init.squares:
            self.next_tetrimino_squares[x][y].config(
                bg=self.next_tetrimino.color
            )

    def on_key_press(self, event):
        self.semaphore.acquire(timeout=0.1)
        if self.is_over:
            self.semaphore.release()
            return

        if event.char == "w":
            self.current_tetrimino.rotate()
        elif event.char == "a":
            self.current_tetrimino.move_left()
        elif event.char == "s":
            self.current_tetrimino.move_down()
            if not self.check():
                x0, y0 = self.current_tetrimino.position_prev
                for x, y in self.current_tetrimino.orientation.squares:
                    self.board[x0+x][y0+y].shape = \
                        self.current_tetrimino.shape
                offset = 0
                for x in range(TETRIS_ROW_N-1, -1, -1):
                    for y in range(TETRIS_COL_N):
                        if not self.board[x][y].shape:
                            break
                    else:
                        offset += 1
                        continue
                    if offset:
                        for y in range(TETRIS_COL_N):
                            self.board[x + offset][y].shape = \
                                self.board[x][y].shape
                if offset:
                    for x in range(offset):
                        for y in range(TETRIS_COL_N):
                            self.board[x][y].shape = ""
                    for x in range(TETRIS_ROW_N):
                        for y in range(TETRIS_COL_N):
                            self.board[x][y].config(
                                bg=COLOR_SCHEME[self.board[x][y].shape]
                            )
                    self.score += offset
                    self.scoreboard.config(text=f"Score: {self.score}")
                self.current_tetrimino = self.next_tetrimino
                self.shadow_position = (0, 3)
                self.refresh_shadow()
                self.refresh_board_display()
                self.next_tetrimino = self.new_random_tetrimino()
                self.refresh_next_tetrimino_display()
                if not self.check():
                    self.is_over = True
                    # high scores
                self.semaphore.release()
                return
            self.refresh_board_display()
            self.semaphore.release()
            return
        elif event.char == "d":
            self.current_tetrimino.move_right()
        elif event.char == " ":
            self.current_tetrimino.position_prev = self.current_tetrimino.position
            self.current_tetrimino.position = list(self.shadow_position)
            self.refresh_shadow()
            self.refresh_board_display()
            self.semaphore.release()
            self.on_key_press(FakeSKeyOnPress)
            return
        elif event.char == "p":
            self.is_paused = not self.is_paused
            self.semaphore.release()
            return
        else:
            self.semaphore.release()
            return

        if self.check():
            self.refresh_shadow()
            self.refresh_board_display()
        else:
            self.current_tetrimino.roll_back()
        self.semaphore.release()

    def check(self, position=None):
        if not position:
            x0, y0 = self.current_tetrimino.position
        else:
            x0, y0 = position
        for x, y in self.current_tetrimino.orientation.squares:
            x += x0
            y += y0
            if x < 0 or x >= TETRIS_ROW_N or y < 0 or y >= TETRIS_COL_N or self.board[x][y].shape:
                return False
        return True


class Square(Frame):
    def __init__(self, master):
        super().__init__(
            master,
            bg=COLOR_SCHEME[""],
            highlightbackground=COLOR_SCHEME["border"],
            highlightthickness=1,
            height=32,
            width=32
        )
        self.shape = ""


class AutoMoveDownThread(Thread):
    def __init__(self, tetris):
        Thread.__init__(self)
        self.tetris = tetris
        self.start()

    def run(self):
        while True:
            self.tetris.semaphore.acquire(timeout=0.1)
            if self.tetris.is_over:
                break
            if self.tetris.score < 100:
                sleep_time = 0.009*(100-self.tetris.score)
            else:
                sleep_time = 0.1
            self.tetris.semaphore.release()
            sleep(sleep_time)

            self.tetris.semaphore.acquire(timeout=0.1)
            if self.tetris.is_paused:
                self.tetris.semaphore.release()
                continue
            self.tetris.semaphore.release()
            self.tetris.on_key_press(FakeSKeyOnPress)


class FakeSKeyOnPress:
    char = "s"


if __name__ == "__main__":
    Tetris()
