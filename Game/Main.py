import pygame

from Emulator.Chip8.Chip8 import Chip8
from Emulator.Chip8.Config import DISPLAY_MULTIPLIER, DISPLAY_WIDTH, DISPLAY_HEIGHT, FOREGROUND_COLOUR, BACKGROUND_COLOUR
from Emulator.Chip8.Memory import Memory

pygame.init()
size = lambda x: x * DISPLAY_MULTIPLIER
screen = pygame.display.set_mode((size(DISPLAY_WIDTH), size(DISPLAY_HEIGHT)))
clock = pygame.time.Clock()
running = True
pause = False

dt = 0
logo = "Games/chip8-test-suite/1-chip8-logo.ch8"
ibm = "Games/chip8-test-suite/2=ibm-logo.ch8"
corax = "Games/chip8-test-suite/3-corax+.ch8"
chip8 = Chip8("Games/INVADERS")

screenDebug = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOUR)
    if screenDebug:
        for i in chip8.Display.pixels:
            for j in i:
                print("O", end="") if j else print(" ", end="")
            print("\n", end="")
        print("----------------------------------------------------------------------------------")
    for i in range(DISPLAY_WIDTH):
        for j in range(DISPLAY_HEIGHT):
            try:
                if chip8.Display.is_set(i, j):
                    screen.fill(FOREGROUND_COLOUR, rect=pygame.Rect(i * DISPLAY_MULTIPLIER, j * DISPLAY_MULTIPLIER, DISPLAY_MULTIPLIER, DISPLAY_MULTIPLIER))
            except IndexError as err:
                print(f"Error at: {i}, {j}")
                running = False
    previousScreen = chip8.Display.pixels.copy()
    pygame.display.flip()

    try:
        if not pause:
            chip8.exec()
    except Exception as err:
        pause = True
        print(f"Error ({err}) at PC {chip8.program_counter}")
    chip8.program_counter+=2

    dt = clock.tick(60) / 1000

pygame.quit()