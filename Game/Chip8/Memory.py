from Emulator.Chip8.Config import MEMORY_SIZE, CHARSET, CHARSET_LOAD_ADDRESS, PROGRAM_LOAD_ADDRESS
from numpy import fromfile, uint8


class Memory:
    def __init__(self, filepath):
        self.Memory = [0x00 for i in range(MEMORY_SIZE)]
        print(len(self.Memory))
        j = 0
        for i in CHARSET:
            self.Memory[CHARSET_LOAD_ADDRESS + j] = i
            j+=1

        with open(filepath, "rb") as ROM:
            arr = fromfile(ROM, dtype=uint8)
            self.Memory[PROGRAM_LOAD_ADDRESS:PROGRAM_LOAD_ADDRESS+len(arr)] = arr
