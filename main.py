from enum import Enum
import pygame
import colors
from grid import Grid

DEBUG = True
print("Debug mode is ON") if DEBUG else None


class CurrentMaterial(Enum):
    SAND = 0
    WATER = 1
    STONE = 2
    FIRE = 3
    WOOD = 4


class MainLoop:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sand Simulator")

        screen_width = 800
        screen_height = 600

        # Set up the screen
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill(colors.BLACK)

        self.clock = pygame.time.Clock()
        # Set the desired FPS
        self.fps = 60

        self.pixel_size = 5

        self.grid = Grid(
            screen_width // self.pixel_size, screen_height // self.pixel_size
        )

        self.current_material = CurrentMaterial.SAND
        self.current_cursor_size = 1

        self.running = True

    def run(self):
        while self.running:
            self.handle_input()

            self.render()
            self.grid.update()

            # Update the screen
            pygame.display.flip()

            # Limit the FPS by sleeping for the remainder of the frame time
            self.clock.tick(self.fps)
            if DEBUG:
                pygame.display.set_caption(
                    f"Sand Simulator - FPS: {self.clock.get_fps() :.2f}"
                )

        self.cleanup()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_grid()
                if event.key == pygame.K_1:
                    self.change_current_material(CurrentMaterial.SAND)
                if event.key == pygame.K_2:
                    self.change_current_material(CurrentMaterial.WATER)
                if event.key == pygame.K_3:
                    self.change_current_material(CurrentMaterial.STONE)
                if event.key == pygame.K_4:
                    self.change_current_material(CurrentMaterial.FIRE)
                if event.key == pygame.K_5:
                    self.change_current_material(CurrentMaterial.WOOD)
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.change_cursor_size(1)
                if event.y < 0:
                    self.change_cursor_size(-1)
            # Mouse wheel click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2 and DEBUG:
                    self.debug_cell()

        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            if self.current_material == CurrentMaterial.SAND:
                self.spawn_sand()
            if self.current_material == CurrentMaterial.WATER:
                self.spawn_water()
            if self.current_material == CurrentMaterial.STONE:
                self.spawn_stone()
            if self.current_material == CurrentMaterial.FIRE:
                self.spawn_fire()
            if self.current_material == CurrentMaterial.WOOD:
                self.spawn_wood()
        if buttons[2]:
            self.remove_cells()

    def change_current_material(self, material: CurrentMaterial):
        self.current_material = material
        if DEBUG:
            print(f"Current material: {material.name}")

    def spawn_sand(self):
        self.modify_grid(self.grid.spawn_sand)

    def spawn_water(self):
        self.modify_grid(self.grid.spawn_water)

    def spawn_stone(self):
        self.modify_grid(self.grid.spawn_stone)

    def spawn_fire(self):
        self.modify_grid(self.grid.spawn_fire)

    def spawn_wood(self):
        self.modify_grid(self.grid.spawn_wood)

    def remove_cells(self):
        self.modify_grid(self.grid.remove_cell)

    def modify_grid(self, modify_function):
        """
        Modify the grid based on the current cursor size and mouse position.
        """
        x, y = pygame.mouse.get_pos()
        x_grid = x // self.pixel_size
        y_grid = y // self.pixel_size

        for i in range(
            x_grid - (self.current_cursor_size // 2),
            x_grid + (self.current_cursor_size // 2) + 1,
        ):
            for j in range(
                y_grid - (self.current_cursor_size // 2),
                y_grid + (self.current_cursor_size // 2) + 1,
            ):
                modify_function(i, j)

    def reset_grid(self):
        self.grid = Grid(
            self.screen.get_width() // self.pixel_size,
            self.screen.get_height() // self.pixel_size,
        )
        self.screen.fill(colors.BLACK)

    def change_cursor_size(self, change: int):
        if not self.current_cursor_size + change < 1:
            self.current_cursor_size += change
            if DEBUG:
                print(f"Current cursor size: {self.current_cursor_size}")

    def debug_cell(self):
        x, y = pygame.mouse.get_pos()
        x_grid = x // self.pixel_size
        y_grid = y // self.pixel_size

        cell = self.grid.get_cell(x_grid, y_grid)
        print(
            f"cell: {cell.__class__.__name__}, position: ({x_grid}, {y_grid}), awake: {(x_grid, y_grid) in self.grid.awaken_cells}"
        )

    def render(self):
        self.render_cells()

    def render_cells(self):
        updated_cells = self.grid.get_updated_cells()
        for (x, y), cell in updated_cells.items():
            self.render_cell(x, y, cell)

    def render_cell(self, x, y, cell):
        pygame.draw.rect(
            self.screen,
            cell.color,
            (
                x * self.pixel_size,
                y * self.pixel_size,
                self.pixel_size,
                self.pixel_size,
            ),
        )

    def cleanup(self):
        pygame.quit()


if __name__ == "__main__":
    main_loop = MainLoop()
    main_loop.run()
