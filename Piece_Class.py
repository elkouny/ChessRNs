from enum import Enum
from typing import List
import numpy as np


class Color(Enum):
    """
    Color names.
    """

    Black = 0
    White = 1
    Blank = 2


class Index(Enum):
    """
    used for the X coordinates in chess that are marked by values from a-h
    """
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8

    def __sub__(self, other):
        if isinstance(other, Index):
            assert 1 <= self.value - other.value <= 8
            return Index(self.value - other.value)
        else:
            assert 1 <= self.value - other <= 8
            return Index(self.value - other)

    def __add__(self, other):
        if isinstance(other, Index):
            assert 1 <= self.value + other.value <= 8
            return Index(self.value + other.value)
        else:
            assert 1 <= self.value + other <= 8
            return Index(self.value + other)


class Piece:
    """
    abstract class for chess piece also used to define blank spots on the chess board
    """

    def __init__(self, _color: Color, _index: Index):
        """
        color indicates black or white index is the initial x position of the piece use to distinguish it from the
        other same pieces, for example the leftmost white pawn would have and index of 1/a
        """
        self.color = _color
        self.index = _index
        self.moved = False

    def movements(self) -> List[np.ndarray]:
        """
        Should return the set of movements in vector notation [dx,dy]
        """
        return [np.array([0, 0])]

    def strong_piece(self) -> bool:
        """
        Strong pieces are defined to be able to move k vectors steps in the boards e.g. like a castle in the [0,
        1] direction
        """
        return False

    def has_moved(self) -> bool:
        """
        This is a getter for moved , which is important to know for special moves like castling
        """
        return self.moved

    def __str__(self):
        return f"{type(self).__name__} object: Color={self.color.name}, Index={self.index.name}"

    # def __is__(self, other):
    #     return isinstance(type(self), other)

    def __hash__(self):
        return hash((self.color.value, self.index.value, type(self).__name__))


class Pawn(Piece):

    def __init__(self, _color: Color, _index: Index, _moved_twice=False):
        super().__init__(_color, _index)
        self.moved_twice = _moved_twice

    def movements(self) -> List[np.ndarray]:
        if self.color == Color.White:
            if self.has_moved():
                return list(map(np.array, [(0, 1), (1, 1), (-1, 1)]))
            else:
                # Move Pawn 2 steps forward initially
                return list(map(np.array, [(0, 1), (1, 1), (-1, 1), (0, 2)]))
        else:
            if self.has_moved():
                return list(map(np.array, [(0, -1), (-1, -1), (1, -1)]))
            else:
                # Move Pawn 2 steps forward initially
                return list(map(np.array, [(0, -1), (-1, -1), (1, -1), (0, -2)]))


class Knight(Piece):

    def movements(self) -> List[np.ndarray]:
        return list(
            map(
                np.array,
                [
                    (1, 2),
                    (2, 1),
                    (2, -1),
                    (1, -2),
                    (-1, -2),
                    (-2, -1),
                    (-2, 1),
                    (-1, 2),
                ],
            )
        )


class Castle(Piece):

    def movements(self) -> List[np.ndarray]:
        return list(map(np.array, [(0, 1), (1, 0)]))

    def strong_piece(self) -> bool:
        return True


class Bishop(Piece):

    def movements(self) -> List[np.ndarray]:
        return list(map(np.array, [(1, 1), (-1, 1)]))

    def strong_piece(self) -> bool:
        return True


class Queen(Piece):

    def movements(self) -> List[np.ndarray]:
        return list(map(np.array, [(1, 1), (-1, 1), (0, 1), (1, 0)]))

    def strong_piece(self) -> bool:
        return True


class King(Piece):

    def movements(self) -> List[np.ndarray]:
        if self.has_moved():
            return list(map(np.array, [(1, 1), (-1, 1), (0, 1), (1, 0)]))
        else:
            # Castling moves included
            return list(map(np.array, [(1, 1), (-1, 1), (0, 1), (1, 0), (-2, 0), (2, 0)]))
