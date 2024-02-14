import random
from cell import Empty, Cell, Sand, Bedrock, Water, Stone


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Create a grid of air cells
        self.grid = [[Empty() for _ in range(width + 1)] for _ in range(height + 1)]

        self.awaken_cells = set()  # Cells that need to be updated

        self.updated_cells = {}

    def update(self):
        # Reset the current updated cells
        self.updated_cells = {}

        update_actions = []
        for x, y in self.awaken_cells:
            cell = self.grid[y][x]
            actions = cell.update(self, x, y)
            if actions:
                update_actions.extend(actions)

        # Reset the current awaken cells
        self.awaken_cells = set()

        # Shuffle the cells to update to avoid bias
        random.shuffle(update_actions)

        for action in update_actions:
            # For each action, we also need to keep awaken the cells that are executing the action.
            # This is because if a cell wants to update itself but it can't, it may need to update again in the next frame.
            x, y = action.get_position()
            self.awaken_cells.add((x, y))
            self.awake_neighbor_cells(x, y)

            action.execute(self)

    def spawn_sand(self, x, y):
        self.spawn_cell(x, y, Sand())

    def spawn_water(self, x, y):
        self.spawn_cell(x, y, Water())

    def spawn_stone(self, x, y):
        self.spawn_cell(x, y, Stone())

    def remove_cell(self, x, y):
        self.spawn_cell(x, y, Empty())

    def spawn_cell(self, x, y, cell):
        # We only want to update the same cell once
        if (x, y) in self.updated_cells:
            return

        if self.is_inside_grid(x, y):
            self.grid[y][x] = cell
            self.updated_cells[(x, y)] = self.grid[y][x]
            self.awaken_cells.add((x, y))
            self.awake_neighbor_cells(x, y)

    def switch_cells(self, x1, y1, x2, y2):
        # We only want to update the same cell once
        if (x1, y1) in self.updated_cells or (x2, y2) in self.updated_cells:
            return

        cell_1 = self.get_cell(x1, y1)
        cell_2 = self.get_cell(x2, y2)

        self.spawn_cell(x1, y1, cell_2)
        self.spawn_cell(x2, y2, cell_1)

    def awake_neighbor_cells(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if not self.is_inside_grid(new_x, new_y):
                    continue
                self.awaken_cells.add((new_x, new_y))

    def get_cell(self, x, y) -> Cell:
        # Check if the cell is outside the grid
        if not self.is_inside_grid(x, y):
            return Bedrock()

        return self.grid[y][x]

    def get_updated_cells(self):
        return self.updated_cells

    def is_inside_grid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
