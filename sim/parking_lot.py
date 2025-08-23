# Parking lot grid and slot logic
class ParkingLot:
    def __init__(self, rows=5, cols=10):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]  # 0=free, 1=occupied

    def is_free(self, row, col):
        return self.grid[row][col] == 0

    def occupy(self, row, col):
        self.grid[row][col] = 1

    def free(self, row, col):
        self.grid[row][col] = 0

    def get_free_slots(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] == 0]

    def occupancy_percent(self):
        total = self.rows * self.cols
        occ = sum(sum(row) for row in self.grid)
        return occ / total * 100
