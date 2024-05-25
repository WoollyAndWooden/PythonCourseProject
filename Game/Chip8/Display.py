from functools import wraps

from Game.Chip8.Config import DISPLAY_WIDTH, DISPLAY_HEIGHT


def check_bounds(func):
    @wraps(func)
    def wrapper(self, x, y):
        if not (x >= 0 and x < DISPLAY_WIDTH and y >= 0 and y < DISPLAY_HEIGHT):
            print(x, y)
            raise Exception(f"Pixel out of bounds at {x} {y}")
        return func(self, x, y)

    return wrapper


class Display:
    def __init__(self) -> None:
        self.pixels = [
            [False for i in range(DISPLAY_HEIGHT)] for j in range(DISPLAY_WIDTH)
        ]

    # @check_bounds
    def set(self, x: int, y: int) -> None:
        self.pixels[x][y] = True

    # @check_bounds
    def is_set(self, x: int, y: int) -> bool:
        return self.pixels[x][y]

    def draw_sprite(self, x: int, y: int, sprite: list[int], num: int):
        pixel_collision = False

        for ly in range(num):
            c = sprite[ly]
            for lx in range(num):
                if (c & (0b10000000 >> lx)) == 0:
                    continue
                pixel_collision = self.pixels[(lx + x) % DISPLAY_WIDTH][
                    (ly + y) % DISPLAY_HEIGHT
                ]
                self.pixels[(lx + x) % DISPLAY_WIDTH][(ly + y) % DISPLAY_HEIGHT] ^= True

        return pixel_collision

    def clear_display(self):
        self.pixels = [
            [False for i in range(DISPLAY_HEIGHT)] for j in range(DISPLAY_WIDTH)
        ]
