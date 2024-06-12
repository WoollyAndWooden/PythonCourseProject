import pygame

from Game.Chip8.Chip8 import Chip8
from sys import argv
from Game.Chip8.Config import (
    DISPLAY_MULTIPLIER,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    FOREGROUND_COLOUR,
    BACKGROUND_COLOUR,
)
pygame.init()
size = lambda x: x * DISPLAY_MULTIPLIER
screen = pygame.display.set_mode((size(DISPLAY_WIDTH), size(DISPLAY_HEIGHT)))
clock = pygame.time.Clock()
running = True
pause = False

dt = 0
if len(argv) != 2:
    raise Exception("Incorrect number of arguements")
chip8 = Chip8(argv[1])

screenDebug = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            print(f"{event.key} pressed")
            if event.key in chip8.Keyboard.keyboard_map.keys():
                print(f"Pressed {event.key}")
                chip8.Keyboard.keyDown(event.key)
                print(chip8.Keyboard.keyState(event.key))
        if event.type == pygame.KEYUP:
            if event.key in chip8.Keyboard.keyboard_map.keys():
                chip8.Keyboard.keyUp(event.key)

    screen.fill(BACKGROUND_COLOUR)
    if screenDebug:
        for i in chip8.Display.pixels:
            for j in i:
                print("O", end="") if j else print(" ", end="")
            print("\n", end="")
        print(
            "----------------------------------------------------------------------------------"
        )
    for i in range(DISPLAY_WIDTH):
        for j in range(DISPLAY_HEIGHT):
            try:
                if chip8.Display.is_set(i, j):
                    screen.fill(
                        FOREGROUND_COLOUR,
                        rect=pygame.Rect(
                            i * DISPLAY_MULTIPLIER,
                            j * DISPLAY_MULTIPLIER,
                            DISPLAY_MULTIPLIER,
                            DISPLAY_MULTIPLIER,
                        ),
                    )
            except IndexError as err:
                print(f"Error at: {i}, {j}")
                running = False
    previousScreen = chip8.Display.pixels.copy()
    pygame.display.flip()

    try:
        if not pause:
            for i in range(0, 12):
                chip8.exec()
    except Exception as err:
        pause = True
        print(f"Error ({err}) at PC {chip8.program_counter}")

    dt = clock.tick(60) / 1000

pygame.quit()
