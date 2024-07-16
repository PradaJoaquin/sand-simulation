import random
from cell import Empty, Cell, Fire, Sand, Bedrock, Water, Stone, Wood


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Create a grid of air cells
        self.grid = [[Empty() for _ in range(width + 1)] for _ in range(height + 1)]

        self.awaken_cells = set()  # Cells to update in the next frame
        self.updated_cells = {}  # Cells that have been updated in the current frame

    def update(self):
        # Reset the current updated cells
        self.updated_cells = {}

        update_actions = []
        for x, y in self.awaken_cells:
            cell = self.grid[y][x]
            actions = cell.update(self, x, y)
            if actions:
                update_actions.extend(actions)

        # Shuffle the cells actions to avoid bias
        random.shuffle(update_actions)

        # Reset the current awaken cells
        self.awaken_cells = set()

        for action in update_actions:
            x, y = action.get_position()
            # We only want to update the same cell once
            if (x, y) in self.updated_cells:
                continue
            # For each action, we also need to keep awaken the cells that are executing the action.
            # This is because if a cell wants to update itself but it can't, it may need to update again in the next frame.
            self.awaken_cells.add((x, y))
            self.awake_neighbor_cells(x, y)

            action.execute(self)

    def spawn_sand(self, x, y):
        self.spawn_cell(x, y, Sand())

    def spawn_water(self, x, y):
        self.spawn_cell(x, y, Water())

    def spawn_stone(self, x, y):
        self.spawn_cell(x, y, Stone())

    def spawn_fire(self, x, y):
        self.spawn_cell(x, y, Fire())

    def spawn_wood(self, x, y):
        self.spawn_cell(x, y, Wood())

    def remove_cell(self, x, y):
        self.spawn_cell(x, y, Empty())

    def spawn_cell(self, x, y, cell):
        if self.is_inside_grid(x, y):
            self.grid[y][x] = cell
            self.updated_cells[(x, y)] = self.grid[y][x]
            self.awaken_cells.add((x, y))
            self.awake_neighbor_cells(x, y)

    def switch_cells(self, x1, y1, x2, y2):
        # We only want to update the same cell once
        if (x2, y2) in self.updated_cells:
            return

        cell_1 = self.get_cell(x1, y1)
        cell_2 = self.get_cell(x2, y2)

        self.spawn_cell(x1, y1, cell_2)
        self.spawn_cell(x2, y2, cell_1)

    def awake_neighbor_cells(self, x, y):
        neighbors = self.get_all_neighbors_positions(x, y)
        for x, y in neighbors:
            self.awaken_cells.add((x, y))

    def get_cell(self, x, y) -> Cell:
        # Check if the cell is outside the grid
        if not self.is_inside_grid(x, y):
            return Bedrock()

        return self.grid[y][x]

    def get_all_neighbors_positions(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if not self.is_inside_grid(new_x, new_y):
                    continue
                neighbors.append((new_x, new_y))
        return neighbors

    def get_updated_cells(self):
        return self.updated_cells

    def is_inside_grid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
