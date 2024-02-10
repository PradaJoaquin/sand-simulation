import random
from cell import Air, Cell, Sand, Bedrock, Water


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Create a grid of air cells
        self.grid = [[Air() for _ in range(width + 1)] for _ in range(height + 1)]

        self.new_desired_positions = {}
        self.already_updated = {}

    def new_sand(self, x, y):
        # create multiple sand particles in a small area
        for _ in range(10):
            new_x = x + random.randint(-5, 5)
            new_y = y + random.randint(-5, 5)
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                self.grid[new_y][new_x] = Sand()
                self.already_updated[(new_x, new_y)] = self.grid[new_y][new_x]

    def new_water(self, x, y):
        # create multiple water particles in a small area
        for _ in range(10):
            new_x = x + random.randint(-5, 5)
            new_y = y + random.randint(-5, 5)
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                self.grid[new_y][new_x] = Water()
                self.already_updated[(new_x, new_y)] = self.grid[new_y][new_x]

    def update(self):
        self.new_desired_positions = {}
        self.already_updated = {}

        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[y][x]
                new_position = cell.update(self, x, y)
                if new_position:
                    self.new_desired_positions[(x, y)] = new_position

        for (x, y), new_position in self.new_desired_positions.items():
            self.switch_cells(x, y, *new_position)

    def switch_cells(self, x1, y1, x2, y2):
        # We only want to update the same cell once
        if (x1, y1) in self.already_updated or (x2, y2) in self.already_updated:
            return

        self.grid[y1][x1], self.grid[y2][x2] = self.grid[y2][x2], self.grid[y1][x1]
        self.already_updated[(x1, y1)] = self.grid[y1][x1]
        self.already_updated[(x2, y2)] = self.grid[y2][x2]

    def get_cell(self, x, y) -> Cell:
        # Check if the cell is outside the grid
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return Bedrock()

        return self.grid[y][x]

    def get_updated_cells(self):
        return self.already_updated
