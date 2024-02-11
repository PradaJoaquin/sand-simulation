import colors
from enum import Enum
import random


class CellType(Enum):
    BEDROCK = -1  # Cell type representing the border of the grid
    AIR = 0
    SAND = 1
    WATER = 2
    STONE = 3


class Cell:
    def __init__(self, type, color):
        self.type = type
        self.color = color

        # TODO: Add a sleeping attribute to the cell to prevent it from being updated every frame
        self.sleeping = False

    def update(self, grid, x, y):
        """
        This method is called every frame to update the cell's state.
        It looks at the grid and updates the cell's state based on the rules of the simulation.

        It should be implemented by the subclasses.

        Args:
            grid (Grid): The grid containing the cell
            x (int): The x position of the cell
            y (int): The y position of the cell
        """
        raise NotImplementedError


class Bedrock(Cell):
    """
    A cell type that represents the border of the grid.
    """

    def __init__(self):
        super().__init__(CellType.BEDROCK, colors.WHITE)

    def update(self, grid, x, y):
        pass


class Air(Cell):
    def __init__(self):
        super().__init__(CellType.AIR, colors.BLACK)

    def update(self, grid, x, y):
        pass


class Sand(Cell):
    def __init__(self):
        super().__init__(CellType.SAND, colors.SAND)

    def update(self, grid, x, y):
        # Check if the cell below is empty
        if grid.get_cell(x, y + 1).type == CellType.AIR:
            return self.update_fall(x, y)

        # Check if the cell below is also sand
        elif grid.get_cell(x, y + 1).type == CellType.SAND:
            return self.update_spread(grid, x, y)

    def update_fall(self, x, y):
        return (x, y + 1)

    def update_spread(self, grid, x, y):
        is_lower_left_empty = False
        is_lower_right_empty = False

        is_lower_left_empty = (
            grid.get_cell(x - 1, y).type == CellType.AIR
            and grid.get_cell(x - 1, y + 1).type == CellType.AIR
        )

        is_lower_right_empty = (
            grid.get_cell(x + 1, y).type == CellType.AIR
            and grid.get_cell(x + 1, y + 1).type == CellType.AIR
        )

        if is_lower_left_empty and is_lower_right_empty:
            # Randomly choose to spread to the left or right
            move_value = random.choice([1, -1])
        elif is_lower_left_empty:
            move_value = -1
        elif is_lower_right_empty:
            move_value = 1
        else:
            return

        return (x + move_value, y + 1)


class Water(Cell):
    def __init__(self):
        super().__init__(CellType.WATER, colors.WATER)

    def update(self, grid, x, y):
        # Check if the cell below is empty
        if grid.get_cell(x, y + 1).type == CellType.AIR:
            return self.update_fall(x, y)

        # Check if the cell below is also water
        return self.update_spread(grid, x, y)

    def update_fall(self, x, y):
        return (x, y + 1)

    def update_spread(self, grid, x, y):
        is_left_empty = False
        is_right_empty = False

        is_left_empty = grid.get_cell(x - 1, y).type == CellType.AIR
        is_right_empty = grid.get_cell(x + 1, y).type == CellType.AIR

        is_lower_left_empty = False
        is_lower_right_empty = False

        is_lower_left_empty = (
            is_left_empty and grid.get_cell(x - 1, y + 1).type == CellType.AIR
        )
        is_lower_right_empty = (
            is_right_empty and grid.get_cell(x + 1, y + 1).type == CellType.AIR
        )

        if is_lower_left_empty and is_lower_right_empty:
            # Randomly choose to spread to the left or right
            move_value = random.choice([1, -1])
        elif is_lower_left_empty:
            move_value = -1
        elif is_lower_right_empty:
            move_value = 1
        else:
            if is_left_empty and is_right_empty:
                move_value = random.choice([1, -1])
            elif is_left_empty:
                move_value = -1
            elif is_right_empty:
                move_value = 1
            else:
                return
            return (x + move_value, y)

        return (x + move_value, y + 1)


class Stone(Cell):
    def __init__(self):
        super().__init__(CellType.STONE, colors.STONE)

    def update(self, grid, x, y):
        pass
