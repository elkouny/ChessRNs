from Piece_Class import Piece, Index, Color
from typing import List, Dict, Type, Set, Union
import numpy as np


class XYPos:
    """
    XY position on the board bottom left is defined as 1,1 , also used for vector notation to describe movements of
    the pieces
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

    def __hash__(self):
        return hash((self.X.value, self.Y))

    def __eq__(self, other):
        return isinstance(other, XYPos) and \
            self.X.value == other.X.value and \
            self.Y == other.Y

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
                    if isinstance(piece, King):
                        self.white_king = piece
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
                    if isinstance(piece, King):
                        self.black_king = piece
                    self.update_board(piece, xy_pos)

    def get_king(self, color: Color) -> XYPos:
        """
        Given Color, you return the kings position on the board
        :param color:
        :return: King position
        """
        if color == Color.Black:
            return self.piece_to_coordinate[self.black_king]
        else:
            return self.piece_to_coordinate[self.white_king]

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

        original_coordinate = self.piece_to_coordinate[piece]
        piece_at_potential_position = self.coordinate_to_piece[potential_position]
        self.update_board(piece, potential_position)
        opponents: List[Piece] = []
        for potential_piece in self.piece_to_coordinate.keys():
            if potential_piece.color != piece.color and potential_piece.color != Color.Blank:
                opponents.append(potential_piece)

        king_position = self.get_king(piece.color)
        for opponent in opponents:
            if king_position in self.get_moves(opponent):
                self.update_board(piece_at_potential_position, potential_position)
                self.update_board(piece, original_coordinate)
                return True

        self.update_board(piece_at_potential_position, potential_position)
        self.update_board(piece, original_coordinate)
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
                else:
                    break
            except AssertionError:
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
                    if isinstance(piece, Pawn) and piece.color == Color.White and ((move == np.array([1, 1])).all() or
                                                                                   (move == np.array([-1, 1])).all()):
                        # Pawn Killing: En-Passant or Normal
                        en_passant = XYPos(potential_position.X, potential_position.Y - 1)
                        piece_at_en_passant = self.coordinate_to_piece[en_passant]
                        if piece_at_potential_position.color != piece.color and piece_at_potential_position.color != Color.Blank:
                            # Normal Case Pawn Killing
                            moves.add(potential_position)
                        elif piece_at_potential_position.color == Color.Blank and piece_at_en_passant is Pawn and piece_at_en_passant.moved_twice and piece_at_en_passant.color != piece.color:
                            # En-passant case
                            moves.add(potential_position)
                    elif isinstance(piece, Pawn) and piece.color == Color.Black and (
                            (move == np.array([-1, -1])).all() or
                            (move == np.array([1, -1])).all()):
                        en_passant = XYPos(potential_position.X, potential_position.Y + 1)
                        piece_at_en_passant = self.coordinate_to_piece[en_passant]
                        if piece_at_potential_position.color != piece.color and piece_at_potential_position.color != Color.Blank:
                            # Normal Case Pawn Killing
                            moves.add(potential_position)
                        elif piece_at_potential_position.color == Color.Blank and piece_at_en_passant is Pawn and piece_at_en_passant.moved_twice and piece_at_en_passant.color != piece.color:
                            # En-passant case
                            moves.add(potential_position)
                    elif isinstance(piece, King) and (
                            (move == np.array([-2, 0])).all() or (move == np.array([2, 0])).all()):
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
                                    isinstance(self.coordinate_to_piece[XYPos(Index.a, row)], Castle) and not \
                                    self.coordinate_to_piece[XYPos(Index.a, row)].has_moved():
                                moves.add(potential_position)
                        else:
                            # Close Castle
                            if self.coordinate_to_piece[XYPos(Index.f, row)].color == Color.Blank and \
                                    self.coordinate_to_piece[XYPos(Index.g, row)].color == Color.Blank and \
                                    isinstance(self.coordinate_to_piece[XYPos(Index.h, row)], Castle) and not \
                                    self.coordinate_to_piece[XYPos(Index.h, row)].has_moved():
                                moves.add(potential_position)
                    elif self.coordinate_to_piece[potential_position].color != piece.color:
                        moves.add(potential_position)
                except AssertionError:
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
        This function is used to move chess pieces , it checks if the move is legal in accordance to the piece and
        does not cause the king to be exposed
        :param piece: Piece to move
        :param final_coordinate: Final coordinate
        to be moved to
        """
        valid_moves = self.get_valid_moves(piece)
        initial_position = self.piece_to_coordinate[piece]
        displacement = np.array(final_coordinate) - np.array(initial_position)
        if final_coordinate in valid_moves:
            piece.moved = True
            if isinstance(piece, Pawn) and abs(displacement[0]) == 2:
                piece.moved_twice = True
            self.update_board(piece, final_coordinate)
        else:
            raise ValueError("Illegal move")
