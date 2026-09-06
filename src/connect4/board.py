class Board:
    
    """
    Connect Four board: 6 rows x 7 columns.
    Row 0 is the top of the board, 5 is the bottom.
    Pieces fall to the row highest row index available in the column.
    0 is an empty cell, 1 is player 1's piece, and 2 is player 2's piece.
    """

    ROWS = 6
    COLS = 7

    #Initialize the board with an empty grid
    def __init__(self):

        self.grid = [[0] * self.COLS for _ in range(self.ROWS)]

    #Check if a move is valid (column is not full)
    def is_valid_move(self, col):

        return 0 <= col < self.COLS and self.grid[0][col] == 0

    #Get a list of valid moves (columns that are not full)
    def valid_moves(self):

        return [col for col in range(self.COLS) if self.is_valid_move(col)]

    #Drop a piece into col, return row it landed on
    def drop_piece(self, col, player):

        if not self.is_valid_move(col):
            raise ValueError(f"Column {col} is not a valid move")
        
        for row in range(self.ROWS - 1, -1, -1):
            if self.grid[row][col] == 0:
                self.grid[row][col] = player
                return row

    #Remove the last piece dropped in col, return row it was removed from
    def undo_move(self, col):

        for row in range(self.ROWS):
            if self.grid[row][col] != 0:
                self.grid[row][col] = 0
                return row
        raise ValueError(f"Column {col} is empty")

    #Check if a player has won the game
    def check_win(self, player):

        grid = self.grid

        #Horizontal win
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                if all(grid[row][col + i] == player for i in range(4)):
                    return True

        #Vertical win
        for col in range(self.COLS):
            for row in range(self.ROWS - 3):
                if all(grid[row + i][col] == player for i in range(4)):
                    return True

        #Diagonal win (top-left to bottom-right)
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                if all(grid[row + i][col + i] == player for i in range(4)):
                    return True

        #Diagonal win (top-right to bottom-left)
        for row in range(3, self.ROWS):
            for col in range(self.COLS - 3):
                if all(grid[row - i][col + i] == player for i in range(4)):
                    return True

        return False

    #Check if the board is full (no valid moves left)
    def is_full(self):
        return len(self.valid_moves()) == 0

    #Check if the game is a draw (board is full and no player has won)
    def is_draw(self):
        return self.is_full() and not self.check_win(1) and not self.check_win(2)
