import chess.svg
from Board import Board, XYPos
from Piece import Queen, Knight, Index, Color, Pawn, Castle, Bishop, King

if __name__ == "__main__":
    # Instantiate board object that I have defined (This will add all the pieces to the board)
    board = Board()
    # This is for visualizing the board using an external chess library, This simply creates a blank chess board.
    image = chess.Board(None)
    # Move white knight to A3 (all moves should be done via the .move_piece method as it checks if the move is valid
    # before updating the board)
    board.move_piece(Knight(Color.White, Index.b), XYPos(Index.a, 3))
    # This loop is to add all the pieces I have in my board to the image
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
        print(f' Piece is {p} coordinate is {c} all the valid moves are {v_m} ')

    s = set()
    # this loop is to add X's at all valid moves for the knight
    for xy_pos in board.get_valid_moves(Knight(Color.White, Index.b)):
        s.add(chess.square(xy_pos.X.value - 1, xy_pos.Y - 1))
    svg = chess.svg.board(board=image, squares=s)
    # Save the generated image
    with open("chess.svg", "w") as file:
        file.write(svg)
