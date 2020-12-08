"""CPU functionality."""

import sys
from pathlib import Path


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.fl = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        
        path = Path("examples/print8.ls8")
        
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
            if (i & 0b1111) == 0b0010:  # LDI
                reg = self.ram_read()
                value = self.ram_read()
                self.reg[reg] = value
            elif (i & 0b1111) == 0b0111:  # PRN
                reg = self.ram_read()
                print(f"{self.reg[reg]}")
