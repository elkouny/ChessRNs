import numpy as np
from enum import Enum
from typing import List, Dict, Type, Set, Union


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
            return Index(self.value - other.value)

    def __add__(self, other):
        if isinstance(other, Index):
            return Index(self.value + other.value)


class XYPos:
    """
    XY position on the board bottom left is defined as 1,1
    """

    def __init__(self, x: Union[int, Index], y: int) -> None:
        if isinstance(x, Index):
            self.X = x
        else:
            self.X = Index(x)

        assert 1 <= self.X.value <= 8, "X out of bounds"
        assert 1 <= y <= 8, "Y out of bounds"
        self.Y = y

    def __sub__(self, other):
        """
        allows for subtraction between 2 XYPos
        """
        if isinstance(other, XYPos):
            return XYPos(self.X - other.X, self.Y - other.Y)

    def __add__(self, other):
        """
        allows for subtraction between 2 XYPos
        """
        if isinstance(other, XYPos):
            return XYPos(self.X + other.X, self.Y + other.Y)

    def __mul__(self, other):
        if isinstance(other, int):
            return XYPos(self.X.value * other, self.Y * other)

    def __array__(self) -> np.ndarray:
        """
        This allows XYPos to be converted to a np.array when typecast eg np.array(XYPos)
        :return: np.array conversion of the XYPos
        """
        return np.array([self.X.value, self.Y], dtype=np.int32)


class Piece:
    """
    abstract class for chess piece also used to define blank spots on the chess board
    """

    def __init__(self, _color: Color, _index: Index):
        """
        color indicates black or white
        index is the initial x position of the piece use to distinguish it from the other same pieces, for example the leftmost white pawn would have and index of 1/a
        """
        self.color = _color
        self.index = _index
        self.moved = False

    def movements(self) -> Set[np.array]:
        """
        Should return the set of movements in vector notation [dx,dy]
        """
        return set(np.array([0, 0]))

    def strong_piece(self) -> bool:
        """
        Strong pieces are defined to be able to move k vectors steps in the boards eg like a castle in the [0,1] direction
        """
        return False

    def has_moved(self) -> bool:
        """
        This is a getter for moved , which is important to know for special moves like castling
        """
        return self.moved


class Pawn(Piece):

    def movements(self) -> Set[np.array]:
        if self.has_moved():
            return map(list(map(np.array, [(0, 1), (1, 1), (-1, 1)])))
        else:
            # Move Pawn 2 steps forward initially
            return map(list(map(np.array, [(0, 1), (1, 1), (-1, 1), (0, 2)])))


class Knight(Piece):

    def movements(self) -> set[np.array]:
        return set(list(
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
        ))


class Castle(Piece):

    def movements(self) -> Set[np.array]:
        return set(list(map(np.array, [(0, 1), (1, 0)])))

    def strong_piece(self) -> bool:
        return True


class Bishop(Piece):

    def movements(self) -> Set[np.array]:
        return set(list(map(np.array, [(1, 1), (-1, 1)])))

    def strong_piece(self) -> bool:
        return True


class Queen(Piece):

    def movements(self) -> Set[np.array]:
        return set(list(map(np.array, [(1, 1), (-1, 1), (0, 1), (1, 0)])))

    def strong_piece(self) -> bool:
        return True


class King(Piece):

    def movements(self) -> Set[np.array]:
        if self.has_moved():
            return set(list(map(np.array, [(1, 1), (-1, 1), (0, 1), (1, 0)])))
        else:
            # Castling moves included
            return set(list(map(np.array, [(1, 1), (-1, 1), (0, 1), (1, 0), (-2, 0), (2, 0)])))

    def strong_piece(self) -> bool:
        if self.has_moved():
            return False
        else:
            return True


class Board:
    """
    Class for defining chess board
    """

    def __init__(self):
        self.piece_to_coordinate: Dict[Piece, XYPos] = {}
        self.coordinate_to_piece: Dict[XYPos, Piece] = {}
        pieces_in_order: List[Type[Piece]] = [
            Castle,
            Knight,
            Bishop,
            Queen,
            King,
            Bishop,
            Knight,
            Castle,
        ]
        for x in map(Index, range(1, 9)):
            for y in range(1, 9):
                xy_pos = XYPos(x, y)
                if y == 1:
                    piece_class = pieces_in_order[x.value - 1]
                    piece = piece_class(Color.White, x)
                    self.update_board(piece, xy_pos)
                elif y == 2:
                    self.update_board(Pawn(Color.White, x), xy_pos)
                elif 3 <= y <= 6:
                    self.update_board(Piece(Color.Blank, x), xy_pos)
                    self.update_board(Pawn(Color.White, x), xy_pos)
                elif y == 7:
                    self.update_board(Pawn(Color.Black, x), xy_pos)
                else:
                    piece_class = pieces_in_order[x.value - 1]
                    piece = piece_class(Color.Black, x)
                    self.update_board(piece, xy_pos)

    def update_board(self, piece: Piece, coordinate: XYPos):
        """
        Function to update the board according to the piece and coordinate
        :param piece: Piece to update
        :param coordinate: Coordinate of the piece
        """
        self.piece_to_coordinate[piece] = coordinate
        self.coordinate_to_piece[coordinate] = piece

    def in_king_exposed(self, piece: Piece, potential_position: XYPos):
        """
        # TODO: This need to be implemented
        :param piece:
        :param potential_position:
        """
        pass

    def get_valid_moves(self, piece: Piece) -> Set[XYPos]:
        """
        returns all the potential valid moves in the form of a List
        :param piece:  to check
        """
        valid_moves: Set[XYPos] = []
        piece_name: str = piece.__name__
        current_position = self.piece_to_coordinate[piece]
        if not piece.strong_piece():
            for move in piece.movements():
                try:
                    # XYPos out of bound will cause an assertion error
                    # TODO: Distinguish between killing moves and normal moves
                    potential_position = current_position + move
                    if self.coordinate_to_piece[potential_position].color != piece.color:
                        valid_moves.add(potential_position)
                except AssertionError:
                    continue
        else:
            for move in piece.movements():
                for k in range(1, 9):
                    try:
                        potential_position = current_position + move * k

                        if self.coordinate_to_piece[potential_position].color == Color.Blank:
                            valid_moves.add(potential_position)
                        elif self.coordinate_to_piece[potential_position].color != piece.color:
                            valid_moves.add(potential_position)
                            break
                    except AssertionError:
                        break
                for k in range(-1, -9, -1):
                    try:
                        potential_position = current_position + move * k
                        if self.coordinate_to_piece[potential_position].color == Color.Blank:
                            valid_moves.add(potential_position)
                        elif self.coordinate_to_piece[potential_position].color != piece.color:
                            valid_moves.add(potential_position)
                            break
                    except AssertionError:
                        break

        return valid_moves

    def move_piece(self, piece: Piece, final_coordinate: XYPos):
        """
        This function is used to move chess pieces , it checks if the move is legal in accordance to the piece and does not cause the king to be exposed
        :param piece: Piece to move
        :param final_coordinate: Final coordinate to be moved to
        """
