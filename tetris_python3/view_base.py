# author: WHMHammer @ GitHub
# email: whmhammer@gmail.com

from abc import ABC
from typing import List

from model import Tetrimino


class TetrisViewBase(ABC):
    def __init__(self):
        raise NotImplementedError

    def refresh(
        self,
        board: List[List[str]] = None,  # TetrisModel.board
        current: Tetrimino = None,  # TetrisModel.current
        shadow: List[int] = None,  # TetrisModel.calculate_shadow()
        next: List[str] = None,  # TetrisModel.next
        held: str = None,  # TetrisModel.held
        score: int = None  # TetrisModel.score
    ):
        raise NotImplementedError
