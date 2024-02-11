import pygame
import colors
from grid import Grid

PIXEL_SIZE = 5


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

        self.grid = Grid(screen_width // PIXEL_SIZE, screen_height // PIXEL_SIZE)

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
            print(self.clock.get_fps())

        self.cleanup()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_grid()
                if event.key == pygame.K_SPACE:
                    self.spawn_stone()
                if event.key == pygame.K_COMMA:
                    self.change_cursor_size(-2)
                if event.key == pygame.K_PERIOD:
                    self.change_cursor_size(2)

        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            self.spawn_sand()
        if buttons[2]:
            self.spawn_water()

    def spawn_sand(self):
        self.spawn_cell(self.grid.new_sand)

    def spawn_water(self):
        self.spawn_cell(self.grid.new_water)

    def spawn_stone(self):
        self.spawn_cell(self.grid.new_stone)

    def spawn_cell(self, spawn_function):
        """
        Spawns a cell or a group of cells at the mouse position, based on the current cursor size.
        """
        x, y = pygame.mouse.get_pos()
        for i in range(-self.current_cursor_size // 2, self.current_cursor_size // 2):
            for j in range(
                -self.current_cursor_size // 2, self.current_cursor_size // 2
            ):
                spawn_function(x // PIXEL_SIZE + i, y // PIXEL_SIZE + j)

    def reset_grid(self):
        self.grid = Grid(
            self.screen.get_width() // PIXEL_SIZE,
            self.screen.get_height() // PIXEL_SIZE,
        )
        self.screen.fill(colors.BLACK)

    def change_cursor_size(self, change: int):
        if not self.current_cursor_size + change < 1:
            self.current_cursor_size += change

    def render(self):
        self.render_cells()

    def render_cells(self):
        updated_cells = self.grid.get_updated_cells()
        for (x, y), cell in updated_cells.items():
            pygame.draw.rect(
                self.screen,
                cell.color,
                (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE),
            )

    def cleanup(self):
        pygame.quit()


if __name__ == "__main__":
    main_loop = MainLoop()
    main_loop.run()
