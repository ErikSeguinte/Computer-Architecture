"""CPU functionality."""

import sys
from pathlib import Path
from typing import Awaitable

LDI = 0b10000010
MUL = 0b10100010
PRN = 0b01000111
HLT = 0b00000001

ADD = 0b10100000
AND = 0b10101000
CALL = 0b01010000
CMP = 0xA7
DEC = 0x66
DIV = 0xA3
INC = 0x65
INT = 0x52
IRET = 0x13
JEQ = 0x55
JGE = 0x5A
JGT = 0x57
JLE = 0x59
JLT = 0x58
JMP = 0x54
JNE = 0x56
LD = 0x83
MOD = 0xA4
NOP = 0
NOT = 0x69
OR = 0xAA
POP = 0x46
PRA = 0x48
PUSH = 0x45
RET = 0x11
SHL = 0xAC
SHR = 0xAD
ST = 0x84
SUB = 0xA1
XOR = 0xAB


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.set_reg(7, 0xF4D)
        self.pc = 0
        self.sp = 0xF3
        self.im = 5
        self.IS = 6
        self.mar = 0
        self.ir = 0

    @property
    def sp(self):
        return self.reg[7]

    @sp.setter
    def sp(self, value):
        self.reg[7] = value

    @property
    def im(self):
        return self.reg[5]

    @im.setter
    def im(self, value):
        self.reg[5] = value

    @property
    def IS(self):
        return self.reg[6]

    @IS.setter
    def IS(self, value):
        self.reg[6] = value

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
            program = [
                int(line[:8], 2)
                for line in f.read().splitlines()
                if (line and (line[0] == "0" or line[0] == "1"))
            ]

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

    def ram_read(self, pointer=None):
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
        a = self.reg[reg_a]
        b = self.reg[reg_b]

        if op == "ADD":
            self.reg[reg_a] += b
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= b
        elif op == "CMP":
            if a > b:
                self.fl = 0b100
            elif a < b:
                self.fl = 0b010
            else:
                self.fl = 0b001
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
                # self.ir,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def do_mul(self):
        reg_a = self.ram_read()
        reg_b = self.ram_read()
        self.alu("MUL", reg_a, reg_b)

    def do_push(self):
        self.sp -= 1
        reg = self.ram_read()
        self.ram_load(self.sp, self.reg[reg])

    def do_pop(self):
        reg = self.ram_read()
        value = self.ram_read(self.sp)
        self.reg[reg] = value
        # print(self.ram[:0xf3])
        self.sp += 1

    def do_call(self):
        reg = self.ram[self.pc]
        new_loc = self.reg[reg]
        self.sp -= 1
        self.ram[self.sp] = self.pc + 1
        self.pc = new_loc

    def do_ret(self):
        new_loc = self.ram[self.sp]
        self.sp += 1
        self.pc = new_loc

    def do_jmp(self):
        reg = self.ram_read()
        new_loc = self.reg[reg]
        self.pc = new_loc

    def run(self):
        """Run the CPU."""

        self.ir = 0

        while self.ir != 1:
            self.ir = self.ram_read()
            if self.ir == LDI:  # LDI
                reg = self.ram_read()
                value = self.ram_read()
                self.set_reg(reg, value)
            elif self.ir == PRN:  # PRN
                reg = self.ram_read()
                print(f"{self.reg[reg]}")
            elif self.ir == MUL:
                self.do_mul()
            elif self.ir == PUSH:
                self.do_push()
            elif self.ir == POP:
                self.do_pop()
            elif self.ir == CALL:
                self.do_call()
            elif self.ir == RET:
                self.do_ret()
            elif self.ir == ADD:
                self.alu("ADD", self.ram_read(), self.ram_read())
            elif self.ir == CMP:
                self.alu("CMP", self.ram_read(), self.ram_read())
            elif self.ir == JMP:
                reg = self.ram_read()
                self.pc = self.reg[reg]
            elif self.ir == JNE:
                if not (self.fl & 0b001):
                    self.do_jmp()
            elif self.ir == JEQ:
                if (self.fl & 0b001):
                    self.do_jmp()
