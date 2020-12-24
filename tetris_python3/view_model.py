# author: WHMHammer @ GitHub
# email: whmhammer@gmail.com

# this module is thread-safe

from os.path import abspath, dirname, join
from sqlite3 import connect
from threading import Lock, Thread
from time import sleep

from model import NEXT_TETRIMINO_N, TetrisModel, TETRIS_COL_N, TETRIS_ROW_N
from view_base import TetrisViewBase


class AutoMoveDownThread(Thread):
    def __init__(self, view_model):
        super().__init__()
        self.view_model: TetrisViewModel = view_model
        self.start()

    def run(self):
        while True:
            self.view_model.lock.acquire()
            if self.view_model.model.is_over:
                self.view_model.lock.release()
                return
            if self.view_model.model.score < 100:
                sleep_time = 0.009*(100-self.view_model.model.score)
            else:
                sleep_time = 0.1
            self.view_model.lock.release()

            sleep(sleep_time)

            self.view_model.lock.acquire()
            if self.view_model.is_paused:
                self.view_model.lock.release()
                continue
            self.view_model.lock.release()
            self.view_model.move_down()


class TetrisViewModel:
    def __init__(self, view: TetrisViewBase):
        self.model: TetrisModel = TetrisModel()
        self.view: TetrisViewBase = view
        self.view.refresh(
            current=self.model.current,
            shadow=self.model.calculate_shadow(),
            next=self.model.next
        )
        self.lock: Lock = Lock()
        self.is_paused: bool = False
        self.auto_move_down_thread: AutoMoveDownThread = AutoMoveDownThread(
            self)

    def move_down(self):
        self.lock.acquire()
        if self.is_paused or self.model.is_over:
            self.lock.release()
            return
        if self.model.move_down():
            self.view.refresh(
                board=self.model.board,
                current=self.model.current,
                shadow=self.model.calculate_shadow(),
                next=self.model.next,
                score=self.model.score
            )
            if self.model.is_over:
                self.save_highscores()
        else:
            self.view.refresh(current=self.model.current)
        self.lock.release()

    def drop(self):
        self.lock.acquire()
        if self.is_paused or self.model.is_over:
            self.lock.release()
            return
        self.model.drop()
        self.view.refresh(
            board=self.model.board,
            current=self.model.current,
            shadow=self.model.calculate_shadow(),
            next=self.model.next,
            score=self.model.score
        )
        self.lock.release()

    def move_left(self):
        self.lock.acquire()
        if self.is_paused or self.model.is_over:
            self.lock.release()
            return
        if self.model.move_left():
            self.view.refresh(
                current=self.model.current,
                shadow=self.model.calculate_shadow()
            )
        self.lock.release()

    def move_right(self):
        self.lock.acquire()
        if self.is_paused or self.model.is_over:
            self.lock.release()
            return
        if self.model.move_right():
            self.view.refresh(
                current=self.model.current,
                shadow=self.model.calculate_shadow()
            )
        self.lock.release()

    def rotate_clockwise(self):
        self.lock.acquire()
        if self.is_paused or self.model.is_over:
            self.lock.release()
            return
        if self.model.rotate_clockwise():
            self.view.refresh(
                current=self.model.current,
                shadow=self.model.calculate_shadow()
            )
        self.lock.release()

    def rotate_counterclockwise(self):
        self.lock.acquire()
        if self.is_paused or self.model.is_over:
            self.lock.release()
            return
        if self.model.rotate_counterclockwise():
            self.view.refresh(
                current=self.model.current,
                shadow=self.model.calculate_shadow()
            )
        self.lock.release()

    def hold(self):
        self.lock.acquire()
        if self.is_paused or self.model.is_over:
            self.lock.release()
            return
        if self.model.hold():
            self.view.refresh(
                current=self.model.current,
                shadow=self.model.calculate_shadow(),
                held=self.model.held
            )
        else:
            self.view.refresh(
                current=self.model.current,
                shadow=self.model.calculate_shadow(),
                held=self.model.held,
                next=self.model.next
            )
        self.lock.release()

    def toggle_pause(self):
        self.lock.acquire()
        if self.model.is_over:
            self.lock.release()
            return
        self.is_paused = not self.is_paused
        self.lock.release()

    def save_highscores(self):
        conn = connect(join(dirname(abspath(__file__)), "highscores.db"))
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS highscore(score INT, time INT, name VARCHAR(16));"
        )
        conn.commit()
        conn.close()
