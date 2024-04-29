import copy

import numpy as np
from enum import Enum
from typing import List, Dict, Type, Set, Union
from dataclasses import dataclass
import chess.svg


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
    XY position on the board bottom left is defined as 1,1 , also used for vector notation to describe movements of the pieces
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
        elif isinstance(other, np.ndarray):
            assert len(other) == 2, "Invalid np vector"
            return XYPos(self.X - other[0], self.Y - int(other[1]))

    def __add__(self, other):
        """
        allows for subtraction between 2 XYPos
        """
        if isinstance(other, XYPos):
            return XYPos(self.X + other.X, self.Y + other.Y)
        elif isinstance(other, np.ndarray):
            assert len(other) == 2, "Invalid np vector"
            return XYPos(self.X + other[0], self.Y + int(other[1]))

    def __mul__(self, other):
        if isinstance(other, int):
            return XYPos(self.X.value * other, self.Y * other)

    def __array__(self) -> np.ndarray:
        """
        This allows XYPos to be converted to a np.array when typecast eg np.array(XYPos)
        :return: np.array conversion of the XYPos
        """
        return np.array([self.X.value, self.Y], dtype=np.int32)

    def __str__(self):
        return f"XYPos object: x={self.X}, y={self.Y}"

    @staticmethod
    def mapper(pos):
        """
        Used for typecasting
        """
        return XYPos(pos[0], pos[1])

    @staticmethod
    def xy_pos_to_chess_poss(xy_pos):
        """
        Convert self-made XYPos class to chess.Pos format for printing
        :param xy_pos:
        """
        return chess.square(xy_pos.X.value - 1, xy_pos.Y - 1)


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

    def movements(self) -> List[np.ndarray]:
        """
        Should return the set of movements in vector notation [dx,dy]
        """
        return [np.array([0, 0])]

    def strong_piece(self) -> bool:
        """
        Strong pieces are defined to be able to move k vectors steps in the boards e.g. like a castle in the [0,1] direction
        """
        return False

    def has_moved(self) -> bool:
        """
        This is a getter for moved , which is important to know for special moves like castling
        """
        return self.moved

    def __str__(self):
        return f"{type(self).__name__} object: Color={self.color.name}, Index={self.index.name}"


class Pawn(Piece):

    def __init__(self, _color: Color, _index: Index, _moved_twice=False):
        super().__init__(_color, _index)
        self.moved_twice = _moved_twice

    def movements(self) -> List[np.ndarray]:
        if self.has_moved():
            return list(map(np.array, [(0, 1), (1, 1), (-1, 1)]))
        else:
            # Move Pawn 2 steps forward initially
            return list(map(np.array, [(0, 1), (1, 1), (-1, 1), (0, 2)]))


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
                elif y == 7:
                    self.update_board(Pawn(Color.Black, x), xy_pos)
                else:
                    piece_class = pieces_in_order[x.value - 1]
                    piece = piece_class(Color.Black, x)
                    self.update_board(piece, xy_pos)

    def get_king(self, color: Color) -> XYPos:
        """
        Given Color, you return the kings position on the board
        :param color:
        :return: King position
        """
        return self.piece_to_coordinate[King(color, Index.e)]

    def update_board(self, piece: Piece, coordinate: XYPos):
        """
        Function to update the board according to the piece and coordinate
        :param piece: Piece to update
        :param coordinate: Coordinate of the piece
        """
        self.piece_to_coordinate[piece] = coordinate
        self.coordinate_to_piece[coordinate] = piece

    def is_king_exposed(self, piece: Piece, potential_position: XYPos):
        """
        :param piece:
        :param potential_position:
        """
        original_piece_to_coordinate = self.piece_to_coordinate.copy()
        original_coordinate_to_piece = self.coordinate_to_piece.copy()
        self.update_board(piece, potential_position)
        opponents: List[Piece] = []
        for potential_piece in self.piece_to_coordinate.keys():
            if potential_piece.color != piece.color and potential_piece.color != Color.Blank:
                opponents.append(potential_piece)

        king_position = self.get_king(piece.color)
        for opponent in opponents:
            if king_position in self.get_moves(opponent):
                self.piece_to_coordinate = original_piece_to_coordinate
                self.coordinate_to_piece = original_coordinate_to_piece
                return True
        self.piece_to_coordinate = original_piece_to_coordinate
        self.coordinate_to_piece = original_coordinate_to_piece
        return False

    def check_moves_strong(self, current_position: XYPos, move_direction: np.ndarray, piece: Piece, moves: Set[XYPos]):
        """
        move the strong pieces in their k * vector
        :param current_position: current position of strong piece
        :param move_direction: direction which strong piece can move
        :param piece: piece to move
        :param moves: all the potential moves that can be done
        """
        for k in range(1, 9):
            try:
                potential_position = current_position + move_direction * k
                if self.coordinate_to_piece[potential_position].color == Color.Blank:
                    moves.add(potential_position)
                elif self.coordinate_to_piece[potential_position].color != piece.color:
                    moves.add(potential_position)
                    break
            except ValueError:
                break

    def get_moves(self, piece: Piece) -> Set[XYPos]:
        """
        returns all the potential moves in the form of a Set some of the moves could be invalid as they could expose the king
        :param piece:  to check
        """
        moves: Set[XYPos] = set()
        current_position = self.piece_to_coordinate[piece]
        if not piece.strong_piece():
            for move in piece.movements():
                try:
                    # XYPos out of bound will cause an assertion error
                    # TODO: Distinguish between killing moves and normal moves
                    potential_position = current_position + move
                    piece_at_potential_position = self.coordinate_to_piece[potential_position]
                    if piece is Pawn and move == XYPos(1, 1) or move == XYPos(-1, 1):
                        # Pawn Killing: En-Passant or Normal setting move.Y to 0 to check for En-Passant
                        en_passant = copy.copy(move)
                        en_passant.Y = 0
                        piece_at_en_passant = self.coordinate_to_piece[en_passant]
                        if piece_at_potential_position.color != piece.color and piece_at_potential_position.color != Color.Blank:
                            # Normal Case Pawn Killing
                            moves.add(potential_position)
                        elif piece_at_potential_position.color == Color.Blank and piece_at_en_passant is Pawn and piece_at_en_passant.moved_twice and piece_at_en_passant.color != piece.color:
                            # En-passant case
                            moves.add(potential_position)
                    elif piece is King and move == XYPos(-2, 0) or move == XYPos(2, 0):
                        # Castling
                        if piece.color == Color.Black:
                            row = 8
                        else:
                            row = 1
                        if move[1] == -2:
                            # Far Castle
                            if self.coordinate_to_piece[XYPos(Index.d, row)].color == Color.Blank and \
                                    self.coordinate_to_piece[XYPos(Index.c, row)].color == Color.Blank and \
                                    self.coordinate_to_piece[XYPos(Index.b, row)].color == Color.Blank and \
                                    self.coordinate_to_piece[XYPos(Index.a, row)] is Castle and not \
                                    self.coordinate_to_piece[XYPos(Index.a, row)].has_moved():
                                moves.add(potential_position)
                        else:
                            # Close Castle
                            if self.coordinate_to_piece[XYPos(Index.f, row)].color == Color.Blank and \
                                    self.coordinate_to_piece[XYPos(Index.g, row)].color == Color.Blank and \
                                    self.coordinate_to_piece[XYPos(Index.h, row)] is Castle and not \
                                    self.coordinate_to_piece[XYPos(Index.h, row)].has_moved():
                                moves.add(potential_position)
                    elif self.coordinate_to_piece[potential_position].color != piece.color:
                        moves.add(potential_position)
                except ValueError:
                    continue
        else:
            for move in piece.movements():
                self.check_moves_strong(current_position, move, piece, moves)
                self.check_moves_strong(current_position, move * -1, piece, moves)
        return moves

    def get_valid_moves(self, piece: Piece) -> Set[XYPos]:
        """
        returns all the potential valid moves in the form of a List
        :param piece:  to check
        """
        moves: Set[XYPos] = self.get_moves(piece)
        valid_moves = set()
        for move in moves:
            if not self.is_king_exposed(piece, move):
                valid_moves.add(move)
        return valid_moves

    def move_piece(self, piece: Piece, final_coordinate: XYPos):
        """
        This function is used to move chess pieces , it checks if the move is legal in accordance to the piece and does not cause the king to be exposed
        :param piece: Piece to move
        :param final_coordinate: Final coordinate to be moved to
        """
        valid_moves = self.get_valid_moves(piece)
        if final_coordinate in valid_moves:
            self.update_board(piece, final_coordinate)
        else:
            raise ValueError("Illegal move")


if __name__ == "__main__":
    board = Board()
    for c, p in board.coordinate_to_piece.items():
        print(f' Piece is {p} coordinate is {c} all the valid moves are {board.get_valid_moves(p)}')
