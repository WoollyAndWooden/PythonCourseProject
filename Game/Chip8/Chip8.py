from functools import wraps
from random import randint

from Game.Chip8.Config import (
    NO_OF_REGISTERS,
    PROGRAM_LOAD_ADDRESS,
    STACK_DEPTH,
    DEFAULT_SPRITE_HEIGHT,
)
from Game.Chip8.Display import Display
from Game.Chip8.Memory import Memory


class Chip8:
    def __init__(self, filepath: str) -> None:
        self.V = [0 for i in range(NO_OF_REGISTERS)]
        self.I = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.program_counter = PROGRAM_LOAD_ADDRESS
        self.stack_pointer = 0
        self.stack = [0 for i in range(STACK_DEPTH)]
        self.Memory = Memory(filepath)
        self.Display = Display()
        self.pop_counter = 0
        self.push_counter = 0

    def check_stack_in_bounds(self):
        if not (self.stack_pointer <= STACK_DEPTH):
            raise Exception(
                f"Stack pointer ({self.stack_pointer}) exceeded Stack depth {STACK_DEPTH}"
            )

    def stack_push(self, val: int) -> None:
        self.stack_pointer += 1
        self.push_counter += 1
        print(
            f"At {hex(self._get_opcode()).upper()} SP: {self.stack_pointer}|{self.push_counter}"
        )
        self.check_stack_in_bounds()
        self.stack[self.stack_pointer] = val

    def stack_pop(self) -> int:
        self.pop_counter += 1
        print(f"At {hex(self._get_opcode()).upper()}|{self.pop_counter}")
        self.check_stack_in_bounds()
        val = self.stack[self.stack_pointer]
        self.stack_pointer -= 1
        return val

    def _get_opcode(self) -> int:
        return (
            self.Memory.Memory[self.program_counter] << 8
            | self.Memory.Memory[self.program_counter + 1]
        )

    # Processor instructions
    def exec(self):
        # Current opcode
        opcode = self._get_opcode()
        self.program_counter += 2

        # lambdas to get certain bits of opcodes
        nnn = lambda opc=opcode: opc & 0x0FFF
        x = lambda opc=opcode: (opc >> 8) & 0x0F
        y = lambda opc=opcode: (opc >> 4) & 0x00F
        kk = lambda opc=opcode: opc & 0x00FF
        last = lambda opc=opcode: opc & 0x000F
        first = lambda opc=opcode: (opc >> 12) & 0xF
        print(
            f"PC: {self.program_counter} opcode: {hex(opcode)}, nnn: {hex(nnn())}, x: {hex(x())}, y: {hex(y())}, kk: {hex(kk())}, last: {hex(last())}, first: {hex(first())}"
        )

        # Comparator mode
        mode = 1

        # Local comparator
        def is_opcode(instruction: int) -> bool:
            if mode == 1:
                return opcode == instruction
            if mode == 2:
                return first() == instruction
            if mode == 3:
                return last() == instruction
            if mode == 4:
                return kk() == instruction

        # Basic instruction set, set mode to 1
        mode = 1
        # CLS
        if is_opcode(0x00E0):
            self.Display.clear_display()
            return
        # RET
        if is_opcode(0x00EE):
            self.program_counter = self.stack_pop()
            return

        # Non basic instructions, set mode to 2
        mode = 2
        # JP
        if is_opcode(0x1):
            self.program_counter = nnn()
            print(f"JP to {self.program_counter} from {self.program_counter}")
            return
        # CAL addr:
        if is_opcode(0x2):
            self.stack_push(self.program_counter)
            self.program_counter = nnn()
            return
        # SE Vc, kk
        if is_opcode(0x3):
            if self.V[x()] == kk():
                self.program_counter += 2
                print(f"SKIPPING AT {self.program_counter}")
            return
        # SNE Vx, kk
        if is_opcode(0x4):
            if self.V[x()] != kk():
                self.program_counter += 2
                print(f"SKIPPING AT {self.program_counter}")
            return
        # SE Vx, Vy
        if is_opcode(0x5):
            if self.V[x()] == self.V[y()]:
                self.program_counter += 2
                print(f"SKIPPING AT {self.program_counter}")
            return
        # LD Vx, Vy
        if is_opcode(0x6):
            self.V[x()] = kk()
            return
        # ADD Vx
        if is_opcode(0x7):
            self.V[x()] = kk(self.V[x()] + kk())
            return
        # Under 0x8 there are several instructions
        if is_opcode(0x8):
            # set comparator mode to 3
            mode = 3
            # LD Vx, Vy
            if is_opcode(0x0):
                self.V[x()] = self.V[y()]
                return
            # Vx OR Vy
            if is_opcode(0x1):
                self.V[x()] |= self.V[y()]
                return
            # Vx AND Vy
            if is_opcode(0x2):
                self.V[x()] &= self.V[y()]
                return
            # Vx XOR Vy
            if is_opcode(0x3):
                self.V[x()] ^= self.V[y()]
                return
            # ADD Vx, Vy. if overflow, set VF to 1, else 0
            if is_opcode(0x4):
                check = True if self.V[x()] + self.V[y()] > 0xFF else False
                self.V[x()] = kk(self.V[x()] + self.V[y()])
                self.V[0xF] = check
                return
            # SUB VX, Vy. If Vx > Vy VF = True, else False
            if is_opcode(0x5):
                check = True if self.V[x()] >= self.V[y()] else False
                self.V[x()] = kk(self.V[x()] - self.V[y()])
                self.V[0xF] = check
                return
            # SHR Vx {, Vy. VF = 1 if least significant bit is 1
            if is_opcode(0x6):
                overflow = True if last(self.V[x()]) & 0b0001 else False
                self.V[x()] //= 2

                self.V[0xF] = overflow
                return
            # SUBN Vx, Vy. If Vy > Vx, VF = 1
            if is_opcode(0x7):
                self.V[x()] = kk(self.V[y()] - self.V[x()])
                self.V[0xF] = True if self.V[y()] >= self.V[x()] else False
                return
            # SHL Vx {, Vy}. If the most significant bit of Vx is 1, then VF = True
            if is_opcode(0xE):
                check = self.V[x()] >> 7
                self.V[x()] = kk(self.V[x()] * 2)
                self.V[0xF] = check
                return
        # switch mode back to 2
        mode = 2
        # SNE Vx, Vy
        if is_opcode(0x9):
            if self.V[x()] != self.V[y()]:
                self.program_counter += 2
                print(f"SKIPPING AT {self.program_counter}")
            return
        # LD I
        if is_opcode(0xA):
            self.I = nnn()
            return
        # JP V0 addr
        if is_opcode(0xB):
            self.program_counter = nnn() + self.V[0]
            return
        # RND Vx, kk
        if is_opcode(0xC):
            self.V[x()] = randint(0, 255) & kk()
            return
        # DRW Vx, Vy. VF = collision
        if is_opcode(0xD):
            self.V[0xF] = self.Display.draw_sprite(
                self.V[x()], self.V[y()], self.Memory.Memory[self.I :], last()
            )
            return
        # Two skips here
        if is_opcode(0xE):
            print(f"NOT IMPLEMENTED {hex(opcode).upper()}")
            return
        # There are several instructions under 0xF000
        if is_opcode(0xF):
            mode = 4
            # LD Vx, DT
            if is_opcode(0x07):
                self.V[x()] = self.delay_timer
                return
            # LD Vx, K: Wait for keypress and store value in Vx
            if is_opcode(0x0A):
                print(f"NOT IMPLEMENTED {hex(opcode).upper()}")
                return
            # LD DT, Vx
            if is_opcode(0x15):
                self.delay_timer = self.V[x()]
                return
            # LD ST, Vx
            if is_opcode(0x18):
                self.sound_timer = self.V[x()]
                return
            # ADD I, Vx
            if is_opcode(0x1E):
                self.I += self.V[x()]
                return
            # LD F, Vx: Location of sprite for Vx
            if is_opcode(0x29):
                self.I = self.V[x()] * DEFAULT_SPRITE_HEIGHT
                return
            # LD B, Vx: Store BCD Representation of Vx in I (hundreds, tens, units)
            if is_opcode(0x33):
                self.Memory.Memory[self.I] = kk(self.V[x()] // 100)
                self.Memory.Memory[self.I + 1] = kk(self.V[x()] // 10 % 10)
                self.Memory.Memory[self.I + 2] = kk(self.V[x()] % 10)
                return
            # LD [I], Vx
            if is_opcode(0x55):
                for i in range(x() + 1):
                    self.Memory.Memory[self.I + i] = self.V[i]
                return
            # LD Vx, I
            if is_opcode(0x65):
                for i in range(x() + 1):
                    self.V[i] = self.Memory.Memory[self.I + i]
                return
            # END OF INSTRUCTIONS
            print(f"INSTRUCTION NOT KNOWN AT {hex(opcode).upper()}")
