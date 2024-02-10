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

        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_grid()
            buttons = pygame.mouse.get_pressed()
            if buttons[0]:
                # Handle mouse click
                self.handle_click()

            self.render()
            self.grid.update()

            # Update the screen
            pygame.display.flip()

            # Limit the FPS by sleeping for the remainder of the frame time
            self.clock.tick(self.fps)
            print(self.clock.get_fps())

        self.cleanup()

    def handle_click(self):
        x, y = pygame.mouse.get_pos()
        self.grid.new_sand(x // PIXEL_SIZE, y // PIXEL_SIZE)

    def reset_grid(self):
        self.grid = Grid(
            self.screen.get_width() // PIXEL_SIZE,
            self.screen.get_height() // PIXEL_SIZE,
        )
        self.screen.fill(colors.BLACK)

    def render(self):
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
