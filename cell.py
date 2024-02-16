from enum import Enum
import colors
import random
from update_action import SpawnCell, RemoveCell, StayStill, SwitchCells


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


class FallDirection(Enum):
    UP = -1
    DOWN = 1
    NONE = 0


class Element(Cell):
    """
    An element is a type of cell that interacts with other cells to change its state.

    The element has the following properties:
    - color (Color): The color of the element
    - fall_direction (FallDirection): The direction the element falls
    - is_affected_by_gravity (bool): Whether the element is affected by gravity
    - flammability_chance (float): The chance the element can catch fire
    """

    def __init__(
        self, color, fall_direction, is_affected_by_gravity, flammability_chance
    ):
        super().__init__(color)
        self.fall_direction = fall_direction
        self.is_affected_by_gravity = is_affected_by_gravity
        self.flammability_chance = flammability_chance

        self.vertical_speed = 1.0

    def update(self, grid, x, y):
        """
        Every element has the same update steps:
        - Try to fall
        - Try to spread
        - If it can't fall or spread, update its state based on the grid.
        """
        actions = self.update_fall(grid, x, y)
        if actions:
            return actions

        actions = self.update_fall_spread(grid, x, y)
        if actions:
            return actions
        return self.update_not_falling(grid, x, y)

    def update_fall(self, grid, x, y):
        fall_direction = self.fall_direction.value
        if fall_direction == 0:
            # The cell can't fall
            return

        vertical_speed = self.update_vertical_speed()

        farthest_fall_distance = y + (vertical_speed * fall_direction)
        for i in range(y, farthest_fall_distance, fall_direction):
            if not self.can_traverse(grid.get_cell(x, i + fall_direction)):
                self.vertical_speed = 1
                if i == y:
                    # The cell can't fall
                    return
                return [SwitchCells(x, y, x, i)]
        return [SwitchCells(x, y, x, farthest_fall_distance)]

    def update_vertical_speed(self):
        if self.is_affected_by_gravity:
            self.vertical_speed *= 1.1  # Gravity acceleration
        return int(self.vertical_speed)

    def update_fall_spread(self, grid, x, y):
        fall_direction = self.fall_direction.value
        if fall_direction == 0:
            # The cell can't fall
            return

        can_spread_left = False
        can_spread_right = False

        can_spread_left = self.can_traverse(
            grid.get_cell(x - 1, y)
        ) and self.can_traverse(grid.get_cell(x - 1, y + fall_direction))

        can_spread_right = self.can_traverse(
            grid.get_cell(x + 1, y)
        ) and self.can_traverse(grid.get_cell(x + 1, y + fall_direction))

        if can_spread_left and can_spread_right:
            # Randomly choose to spread to the left or right
            move_value = random.choice([1, -1])
        elif can_spread_left:
            move_value = -1
        elif can_spread_right:
            move_value = 1
        else:
            # The cell can't spread
            return

        return [SwitchCells(x, y, x + move_value, y + fall_direction)]

    def try_to_ignite(self):
        """
        Try to ignite the cell.
        """
        return random.random() < self.flammability_chance

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


class Fluid(Element):
    """
    A fluid is any material that flows in response to an applied force, therefore liquids and gases are fluids.
    """

    def __init__(
        self,
        color,
        fall_direction,
        is_affected_by_gravity,
        flammability_chance,
        flow_speed,
    ):
        super().__init__(
            color, fall_direction, is_affected_by_gravity, flammability_chance
        )
        self.flow_speed = flow_speed

    def update_not_falling(self, grid, x, y):
        return self.update_flow(grid, x, y)

    def update_flow(self, grid, x, y):
        farthest_right = self.farthest_flow_position(grid, x, y, 1)
        farthest_left = self.farthest_flow_position(grid, x, y, -1)

        if farthest_right == x and farthest_left == x:
            # The fluid can't flow
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

    def can_flow_through(self, cell):
        """
        Fluid elements can flow through other fluid elements.
        """
        return self.can_traverse(cell) or isinstance(cell, Fluid)


class Liquid(Fluid):
    def __init__(self, color, flammability_chance, flow_speed):
        is_affected_by_gravity = True
        fall_direction = FallDirection.DOWN
        super().__init__(
            color,
            fall_direction,
            is_affected_by_gravity,
            flammability_chance,
            flow_speed,
        )

    def can_traverse(self, cell):
        return isinstance(cell, Empty) or isinstance(cell, Gas)


class Gas(Fluid):
    def __init__(self, color, flammability_chance, flow_speed):
        fall_direction = FallDirection.UP
        is_affected_by_gravity = False
        super().__init__(
            color,
            fall_direction,
            is_affected_by_gravity,
            flammability_chance,
            flow_speed,
        )

    def can_traverse(self, cell):
        return isinstance(cell, Empty)


class Solid(Element):
    def __init__(self, color, fall_direction, flammability_chance):
        is_affected_by_gravity = True
        super().__init__(
            color, fall_direction, is_affected_by_gravity, flammability_chance
        )

    def can_traverse(self, cell):
        return isinstance(cell, Empty) or isinstance(cell, Fluid)


class MovableSolid(Solid):
    def __init__(self, color, flammability_chance):
        fall_direction = FallDirection.DOWN
        super().__init__(color, fall_direction, flammability_chance)

    def update_not_falling(self, grid, x, y):
        return


class UnmovableSolid(Solid):
    def __init__(self, color, flammability_chance):
        fall_direction = FallDirection.NONE  # Unmovable solids don't fall
        super().__init__(color, fall_direction, flammability_chance)


class Bedrock(UnmovableSolid):
    """
    A cell type that represents the border of the grid.
    """

    def __init__(self):
        color = colors.WHITE
        flammability_chance = 0
        super().__init__(color, flammability_chance)

    def update_not_falling(self, grid, x, y):
        return


class Sand(MovableSolid):
    def __init__(self):
        color = colors.SAND
        flammability_chance = 0
        super().__init__(color, flammability_chance)


class Water(Liquid):
    def __init__(self):
        color = colors.WATER
        flammability_chance = 0
        flow_speed = 5
        super().__init__(color, flammability_chance, flow_speed)


class Stone(UnmovableSolid):
    def __init__(self):
        color = colors.STONE
        flammability_chance = 0
        super().__init__(color, flammability_chance)


class Fire(UnmovableSolid):
    def __init__(self):
        color = colors.FIRE
        flammability_chance = 0
        super().__init__(color, flammability_chance)

        self.chance_to_extinguish = 0.01

    def update_not_falling(self, grid, x, y):
        actions = [StayStill(x, y)]
        actions.extend(self.update_propagation(grid, x, y))
        actions.extend(self.update_extinguish(grid, x, y))
        return actions

    def update_propagation(self, grid, x, y):
        """
        Look if the fire can propagate to the surrounding cells.
        """
        actions = []
        neighbors = grid.get_all_neighbors_positions(x, y)
        for i, j in neighbors:
            neighbor = grid.get_cell(i, j)
            if isinstance(neighbor, Empty):
                continue
            if grid.get_cell(i, j).try_to_ignite():
                actions.append(SpawnCell(i, j, Fire()))
        return actions

    def update_extinguish(self, grid, x, y):
        """
        Look if the fire can extinguish.
        """
        # See if there is water nearby
        neighbors = grid.get_all_neighbors_positions(x, y)
        for i, j in neighbors:
            if isinstance(grid.get_cell(i, j), Water):
                return [RemoveCell(x, y)]

        # Randomly extinguish the fire
        if random.random() < self.chance_to_extinguish:
            return [RemoveCell(x, y)]
        return []


class Wood(UnmovableSolid):
    def __init__(self):
        color = colors.WOOD
        flammability_chance = 0.01
        super().__init__(color, flammability_chance)

    def update_not_falling(self, grid, x, y):
        return
