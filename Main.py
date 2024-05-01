import chess.svg
from Piece_Class import *
from Board_Class import *

if __name__ == "__main__":
    board = Board()
    image = chess.Board()
    board.update_board(Queen(Color.White, Index.e), XYPos(Index.e, 7))
    for c, p in board.coordinate_to_piece.items():
        if isinstance(p, Pawn):
            letter = "p"
        elif isinstance(p, Castle):
            letter = "r"
        elif isinstance(p, Knight):
            letter = 'n'
        elif isinstance(p, Bishop):
            letter = "b"
        elif isinstance(p, Queen):
            letter = "q"
        elif isinstance(p, King):
            letter = "k"
        else:
            continue
        if p.color == Color.White:
            letter = letter.upper()

        image.set_piece_at(chess.square(c.X.value - 1, c.Y - 1), chess.Piece.from_symbol(letter))

        v_m = "{" + ", ".join(str(xy_pos) for xy_pos in board.get_valid_moves(p)) + "}"
        print(f' Piece is {p} coordinate is {c} all the valid moves are {v_m}  type : ')

    s = set()
    for xy_pos in board.get_valid_moves(Queen(Color.White, Index.d)):
        s.add(chess.square(xy_pos.X.value - 1, xy_pos.Y - 1))
    svg = chess.svg.board(board=image, squares=s)
    with open("chess.svg", "w") as file:
        file.write(svg)
