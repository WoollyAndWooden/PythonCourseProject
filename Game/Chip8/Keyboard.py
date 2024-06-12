import pygame


class Keyboard:
    def __init__(self):
        self.keyboard = {
            pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
            pygame.K_q: 4, pygame.K_w: 5, pygame.K_e: 6, pygame.K_r: 7,
            pygame.K_a: 8, pygame.K_s: 9, pygame.K_d: 10, pygame.K_f: 11,
            pygame.K_z: 12, pygame.K_x: 13, pygame.K_c: 14, pygame.K_v: 15,
        }
        self.keyboard_map = {
            pygame.K_1: False, pygame.K_2: False, pygame.K_3: False, pygame.K_4: False,
            pygame.K_q: False, pygame.K_w: False, pygame.K_e: False, pygame.K_r: False,
            pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_f: False,
            pygame.K_z: False, pygame.K_x: False, pygame.K_c: False, pygame.K_v: False
        }

    def keyUp(self, key):
        if key in self.keyboard_map.keys():
            self.keyboard_map[key] = False

    def keyDown(self, key):
        if key in self.keyboard_map.keys():
            self.keyboard_map[key] = True

    def keyState(self, key):
        if key in self.keyboard_map.keys():
            return self.keyboard_map[key]
        return None