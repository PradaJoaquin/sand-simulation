import colors
import random
from update_action import SpawnCell, RemoveCell, SwitchCells


class Cell:
    def __init__(self, color):
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

        Returns:
            List[UpdateAction]: A list of actions to execute on the grid or None if no action is needed
        """
        raise NotImplementedError


class Empty(Cell):
    def __init__(self):
        super().__init__(colors.BLACK)

    def update(self, grid, x, y):
        return


class GravityAffected(Cell):
    def __init__(self, color):
        super().__init__(color)
        self.vertical_speed = 1

    def update(self, grid, x, y):
        actions = self.update_fall(grid, x, y)
        if actions:
            return actions

        actions = self.update_fall_spread(grid, x, y)
        if actions:
            return actions

        return self.update_not_falling(grid, x, y)

    def update_fall(self, grid, x, y):
        farthest_fall_distance = self.farthest_fall_distance(y)
        for i in range(y, farthest_fall_distance):
            if not self.can_traverse(grid.get_cell(x, i + 1)):
                self.stoped_falling()
                if i == y:
                    # The cell can't fall
                    return
                return [SwitchCells(x, y, x, i)]
        return [SwitchCells(x, y, x, farthest_fall_distance)]

    def farthest_fall_distance(self, current_height):
        """
        Calculates the farthest possible fall position of the cell based on the vertical speed.
        """
        farthest_y = current_height + self.vertical_speed
        self.vertical_speed *= 1.1  # Gravity acceleration
        return int(farthest_y)

    def stoped_falling(self):
        self.vertical_speed = 1

    def update_fall_spread(self, grid, x, y):
        can_spread_lower_left = False
        can_spread_lower_right = False

        can_spread_lower_left = self.can_traverse(
            grid.get_cell(x - 1, y)
        ) and self.can_traverse(grid.get_cell(x - 1, y + 1))

        can_spread_lower_right = self.can_traverse(
            grid.get_cell(x + 1, y)
        ) and self.can_traverse(grid.get_cell(x + 1, y + 1))

        if can_spread_lower_left and can_spread_lower_right:
            # Randomly choose to spread to the left or right
            move_value = random.choice([1, -1])
        elif can_spread_lower_left:
            move_value = -1
        elif can_spread_lower_right:
            move_value = 1
        else:
            # The cell can't spread
            return

        return [SwitchCells(x, y, x + move_value, y + 1)]

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
    def __init__(self, color):
        super().__init__(color)


class Liquid(GravityAffected):
    def __init__(self, color, flow_speed):
        super().__init__(color)
        self.flow_speed = flow_speed

    def can_traverse(self, cell):
        return isinstance(cell, Empty)

    def can_flow_through(self, cell):
        """
        Liquid cells can flow through other liquid cells.
        """
        return self.can_traverse(cell) or isinstance(cell, Liquid)

    def update_not_falling(self, grid, x, y):
        return self.update_flow(grid, x, y)

    def update_flow(self, grid, x, y):
        farthest_right = self.farthest_flow_position(grid, x, y, 1)
        farthest_left = self.farthest_flow_position(grid, x, y, -1)

        if farthest_right == x and farthest_left == x:
            # The liquid can't flow
            return

        delta_right = abs(farthest_right - x)
        delta_left = abs(farthest_left - x)

        if delta_right == delta_left:
            new_x = random.choice([farthest_right, farthest_left])
            return [SwitchCells(x, y, new_x, y)]
        elif delta_right > delta_left:
            return [SwitchCells(x, y, farthest_right, y)]
        else:
            return [SwitchCells(x, y, farthest_left, y)]

    def farthest_flow_position(self, grid, x, y, direction):
        """
        Looks for the farthest position the liquid can flow to in the given direction.

        Liquids only flow to an empty cell.
        """
        farthest_x = x + (self.flow_speed * direction)
        farthest_empty = x
        for i in range(x, farthest_x, direction):
            next_cell = grid.get_cell(i + direction, y)
            if not self.can_flow_through(next_cell):
                return farthest_empty
            if isinstance(next_cell, Empty):
                # Look above the empty cell
                above_cell = grid.get_cell(i + direction, y - 1)
                # We prioritize falling rather than flowing to accelerate the water flow
                if not isinstance(above_cell, Liquid):
                    farthest_empty = i + direction
                else:
                    # But we still leave a small chance for the water to flow to the side, to simulate bubbles
                    if random.random() < 0.05:
                        farthest_empty = i + direction

        return farthest_empty


class MovableSolid(Solid):
    def __init__(self, color):
        super().__init__(color)

    def can_traverse(self, cell):
        return isinstance(cell, Empty) or isinstance(cell, Liquid)


class UnmovableSolid(Solid):
    def __init__(self, color):
        super().__init__(color)

    def update(self, grid, x, y):
        """
        Unmovable solids don't fall, so we only need to update their state when they are not falling.
        """
        return self.update_not_falling(grid, x, y)


class Bedrock(UnmovableSolid):
    """
    A cell type that represents the border of the grid.
    """

    def __init__(self):
        super().__init__(colors.WHITE)

    def update(self, grid, x, y):
        pass


class Sand(MovableSolid):
    def __init__(self):
        super().__init__(colors.SAND)

    def update_not_falling(self, grid, x, y):
        return


class Water(Liquid):
    def __init__(self):
        flow_speed = 5
        super().__init__(colors.WATER, flow_speed)


class Stone(UnmovableSolid):
    def __init__(self):
        super().__init__(colors.STONE)

    def update_not_falling(self, grid, x, y):
        return
