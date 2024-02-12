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

    def update(self, grid, x, y):
        (new_x, new_y) = self.update_fall(grid, x, y)
        if (new_x, new_y) != (x, y):
            return (new_x, new_y)

        (new_x, new_y) = self.update_fall_spread(grid, x, y)
        if (new_x, new_y) != (x, y):
            return (new_x, new_y)

        return self.update_not_falling(grid, x, y)

    def update_fall(self, grid, x, y):
        furthest_fall_distance = self.furthest_fall_distance(y)
        for i in range(y, furthest_fall_distance):
            if not self.can_traverse(grid.get_cell(x, i + 1)):
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

    def update_fall_spread(self, grid, x, y):
        is_lower_left_empty = False
        is_lower_right_empty = False

        is_lower_left_empty = self.can_traverse(
            grid.get_cell(x - 1, y)
        ) and self.can_traverse(grid.get_cell(x - 1, y + 1))

        is_lower_right_empty = self.can_traverse(
            grid.get_cell(x + 1, y)
        ) and self.can_traverse(grid.get_cell(x + 1, y + 1))

        if is_lower_left_empty and is_lower_right_empty:
            # Randomly choose to spread to the left or right
            move_value = random.choice([1, -1])
        elif is_lower_left_empty:
            move_value = -1
        elif is_lower_right_empty:
            move_value = 1
        else:
            return (x, y)

        return (x + move_value, y + 1)

    def can_traverse(self, cell):
        """
        Check if the cell can traverse the given cell.

        It should be implemented by the subclasses.
        """
        raise NotImplementedError

    def update_not_falling(self, grid, x, y):
        """
        When the cell is not falling, it can still change its state.

        It should be implemented by the subclasses.
        """
        raise NotImplementedError


class Solid(GravityAffected):
    def __init__(self, type, color):
        super().__init__(type, color)


class Liquid(GravityAffected):
    def __init__(self, type, color, flow_speed):
        super().__init__(type, color)
        self.flow_speed = flow_speed

    def can_traverse(self, cell):
        return isinstance(cell, Air)

    def can_flow_through(self, cell):
        """
        Liquid cells can flow through other liquid cells.
        """
        return self.can_traverse(cell) or isinstance(cell, Liquid)


class MovableSolid(Solid):
    def __init__(self, type, color):
        super().__init__(type, color)

    def can_traverse(self, cell):
        return isinstance(cell, Air) or isinstance(cell, Liquid)


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

    def update_not_falling(self, grid, x, y):
        return (x, y)


class Water(Liquid):
    def __init__(self):
        flow_speed = 3
        super().__init__(CellType.WATER, colors.WATER, flow_speed)

    def update_not_falling(self, grid, x, y):
        return self.update_flow(grid, x, y)

    def update_flow(self, grid, x, y):
        # TODO: Change to a better algorithm, it should look for the furthest air cell to flow, passing through other liquids
        is_left_empty = False
        is_right_empty = False

        is_left_empty = self.can_flow_through(grid.get_cell(x - 1, y))
        is_right_empty = self.can_flow_through(grid.get_cell(x + 1, y))

        if is_left_empty and is_right_empty:
            direction = random.choice([1, -1])
        elif is_left_empty:
            direction = -1
        elif is_right_empty:
            direction = 1
        else:
            return (x, y)
        return self.furthest_flow_position(grid, x, y, direction)

    def furthest_flow_position(self, grid, x, y, direction):
        furthest_x = x + (self.flow_speed * direction)
        for i in range(x, furthest_x, direction):
            if not self.can_flow_through(grid.get_cell(i + direction, y)):
                return (i, y)
        return (furthest_x, y)


class Stone(UnmovableSolid):
    def __init__(self):
        super().__init__(CellType.STONE, colors.STONE)

    def update(self, grid, x, y):
        pass
