class UpdateAction:
    """
    Cells use this actions to update the grid.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def execute(self, grid):
        """
        Execute the action on the grid.

        It should be implemented by the subclasses.
        """
        raise NotImplementedError

    def get_position(self):
        return self.x, self.y


class SpawnCell(UpdateAction):
    def __init__(self, x, y, cell):
        super().__init__(x, y)
        self.cell = cell

    def execute(self, grid, cell):
        grid.spawn_cell(self.x, self.y, cell)


class RemoveCell(UpdateAction):
    def execute(self, grid):
        grid.remove_cell(self.x, self.y)


class SwitchCells(UpdateAction):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1)
        self.x2 = x2
        self.y2 = y2

    def execute(self, grid):
        grid.switch_cells(self.x, self.y, self.x2, self.y2)
