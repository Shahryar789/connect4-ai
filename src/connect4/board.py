class Board:
    ROWS = 6
    COLS = 7

    def __init__(self):
        self.grid = [[0] * self.COLS for _ in range(self.ROWS)]

    def is_valid_move(self, col):
        return 0 <= col < self.COLS and self.grid[0][col] == 0

    def valid_moves(self):
        return [col for col in range(self.COLS) if self.is_valid_move(col)]

    def drop_piece(self, col, player):
        if not self.is_valid_move(col):
            raise ValueError(f"Column {col} is not a valid move")
        for row in range(self.ROWS - 1, -1, -1):
            if self.grid[row][col] == 0:
                self.grid[row][col] = player
                return row

    def undo_move(self, col):
        for row in range(self.ROWS):
            if self.grid[row][col] != 0:
                self.grid[row][col] = 0
                return row
        raise ValueError(f"Column {col} is empty")

    def check_win(self, player):
        grid = self.grid

        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                if all(grid[row][col + i] == player for i in range(4)):
                    return True

        for col in range(self.COLS):
            for row in range(self.ROWS - 3):
                if all(grid[row + i][col] == player for i in range(4)):
                    return True

        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                if all(grid[row + i][col + i] == player for i in range(4)):
                    return True

        for row in range(3, self.ROWS):
            for col in range(self.COLS - 3):
                if all(grid[row - i][col + i] == player for i in range(4)):
                    return True

        return False

    def is_full(self):
        return len(self.valid_moves()) == 0

    def is_draw(self):
        return self.is_full() and not self.check_win(1) and not self.check_win(2)
