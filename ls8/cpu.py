"""CPU functionality."""

import sys
from pathlib import Path

LDI = 0b10000010 
MUL = 0b10100010
PRN = 0b01000111
HLT = 0b00000001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.set_reg(7, 0xF4d)
        self.pc = 0
        
    def set_reg(self, reg, value):
        self.reg[reg] = value

        a, b = self.reg[0], self.reg[1]

        if a > b:
            self.fl = 0b100
        elif a < b:
            self.fl = 0b010
        else:
            self.fl = 0b000

    def load(self):
        """Load a program into memory."""

        address = 0

        filename = sys.argv[1]
        
        path = Path(f"examples/{filename}")
        
        with open(path, "r") as f:
            program = [int(line[:8], 2) for line in f.read().splitlines() if (line and (line[0] =='0' or line[0] =="1"))]
            



        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        for instruction in program:
            self.ram_load(address, instruction)
            address += 1
            
    def ram_load(self, address, instruction):
        self.ram[address] = instruction

    def ram_read(self, pointer = None):
        if pointer is None:
            p = self.pc
        else:
            p = pointer
        i = self.ram[p]
        
        if pointer is None:
            self.pc += 1
        return i

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def run(self):
        """Run the CPU."""

        i = 0

        while i != 1:
            i = self.ram_read()
            if i == LDI:  # LDI
                reg = self.ram_read()
                value = self.ram_read()
                self.reg[reg] = value
            elif i == PRN:  # PRN
                reg = self.ram_read()
                print(f"{self.reg[reg]}")
            elif i == MUL:
                reg_a = self.ram_read()
                reg_b = self.ram_read()
                self.alu('MUL', reg_a, reg_b)
