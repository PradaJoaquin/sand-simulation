import random
from cell import Air, Cell, Sand, Bedrock, Water, Stone


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Create a grid of air cells
        self.grid = [[Air() for _ in range(width + 1)] for _ in range(height + 1)]

        self.new_desired_positions = {}
        self.already_updated = {}

    def spawn_sand(self, x, y):
        self.spawn_cell(x, y, Sand())

    def spawn_water(self, x, y):
        self.spawn_cell(x, y, Water())

    def spawn_stone(self, x, y):
        self.spawn_cell(x, y, Stone())

    def spawn_cell(self, x, y, cell):
        if self.is_inside_grid(x, y):
            self.grid[y][x] = cell
            self.already_updated[(x, y)] = self.grid[y][x]

    def remove_cell(self, x, y):
        if self.is_inside_grid(x, y):
            self.grid[y][x] = Air()
            self.already_updated[(x, y)] = self.grid[y][x]

    def update(self):
        self.new_desired_positions = {}
        self.already_updated = {}

        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[y][x]
                new_position = cell.update(self, x, y)
                if new_position:
                    self.new_desired_positions[(x, y)] = new_position

        # Shuffle the cells to update to avoid bias
        cells_to_update = list(self.new_desired_positions.items())
        random.shuffle(cells_to_update)

        for (x, y), new_position in cells_to_update:
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
        if not self.is_inside_grid(x, y):
            return Bedrock()

        return self.grid[y][x]

    def get_updated_cells(self):
        return self.already_updated

    def is_inside_grid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
