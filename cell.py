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


class GravityAffected(Cell):
    def __init__(self, type, color):
        super().__init__(type, color)
        self.vertical_speed = 1

    def update_fall(self, grid, x, y):
        collide_cell_type = self.stop_falling_cell_type()
        furthest_fall_distance = self.furthest_fall_distance(y)
        for i in range(y, furthest_fall_distance):
            if isinstance(grid.get_cell(x, i + 1), collide_cell_type):
                self.stoped_falling()
                return (x, i)
        return (x, furthest_fall_distance)

    def furthest_fall_distance(self, current_height):
        """
        Calculates the furthest possible fall position of the cell based on the vertical speed.
        """
        furthest_y = current_height + self.vertical_speed
        self.vertical_speed *= 1.1  # Gravity acceleration
        return int(furthest_y)

    def stoped_falling(self):
        self.vertical_speed = 1

    def stop_falling_cell_type(self):
        """
        Returns the cell type in which the cell stops falling.

        It should be implemented by the subclasses.
        """
        raise NotImplementedError


class Solid(GravityAffected):
    def __init__(self, type, color):
        super().__init__(type, color)


class Liquid(GravityAffected):
    def __init__(self, type, color):
        super().__init__(type, color)


class MovableSolid(Solid):
    def __init__(self, type, color):
        super().__init__(type, color)


class UnmovableSolid(Solid):
    def __init__(self, type, color):
        super().__init__(type, color)


class Bedrock(UnmovableSolid):
    """
    A cell type that represents the border of the grid.
    """

    def __init__(self):
        super().__init__(CellType.BEDROCK, colors.WHITE)

    def update(self, grid, x, y):
        pass


# TODO: Change to Nothing instead of Air?
class Air(Cell):
    def __init__(self):
        super().__init__(CellType.AIR, colors.BLACK)

    def update(self, grid, x, y):
        pass


class Sand(MovableSolid):
    def __init__(self):
        super().__init__(CellType.SAND, colors.SAND)

    def update(self, grid, x, y):
        # Check if the cell below is solid
        (new_x, new_y) = self.update_fall(grid, x, y)
        if (new_x, new_y) != (x, y):
            return (new_x, new_y)

        # Check if the cell below is also sand
        if grid.get_cell(x, y + 1).type == CellType.SAND:
            return self.update_spread(grid, x, y)

    def stop_falling_cell_type(self):
        return Solid

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


class Water(Liquid):
    def __init__(self):
        super().__init__(CellType.WATER, colors.WATER)

    def update(self, grid, x, y):
        # Check if the cell below is empty
        (new_x, new_y) = self.update_fall(grid, x, y)
        if (new_x, new_y) != (x, y):
            return (new_x, new_y)

        # Check if the cell below is also water
        return self.update_spread(grid, x, y)

    def stop_falling_cell_type(self):
        return Liquid

    def update_fall(self, grid, x, y):
        furthest_fall_distance = self.furthest_fall_distance(y)
        for i in range(y, furthest_fall_distance):
            if isinstance(grid.get_cell(x, i + 1), GravityAffected):
                self.stoped_falling()
                return (x, i)
        return (x, furthest_fall_distance)

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


class Stone(UnmovableSolid):
    def __init__(self):
        super().__init__(CellType.STONE, colors.STONE)

    def update(self, grid, x, y):
        pass
