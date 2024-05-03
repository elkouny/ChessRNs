import chess.svg
from Board import *

if __name__ == "__main__":
    board = Board()
    image = chess.Board(None)
    board.move_piece(Knight(Color.White, Index.b), XYPos(Index.a, 3))
    q = Queen(Color.Black, Index.e)
    board.add_piece_to_board(q, XYPos(Index.e, 2))
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

        v_m = "{" + ", ".join(str(xy_pos) for xy_pos in board.get_valid_moves(p)) + "}"
        print(f' Piece is {p} coordinate is {c} all the valid moves are {v_m} ')
        image.set_piece_at(chess.square(c.X.value - 1, c.Y - 1), chess.Piece.from_symbol(letter))

    print(board.get_valid_moves(Bishop(Color.White, Index.f)))
    s = set()
    for xy_pos in board.get_valid_moves(q):
        s.add(chess.square(xy_pos.X.value - 1, xy_pos.Y - 1))
    svg = chess.svg.board(board=image)
    with open("chess.svg", "w") as file:
        file.write(svg)
