"""CPU functionality."""

# Instructions
HLT = 0b00000001 # Halt
LDI = 0b10000010 # Set Value of a reg to an int
PRN = 0b01000111 # Print
PUSH = 0b01000101 # Push
POP = 0b01000110 # Pop
SP = 0b00000111 # Stack pointer
# PC Mutators
CALL = 0b01010000 # Call
RET = 0b00010001 # Return
JMP = 0b01010100 # Jump
JEQ = 0b01010101 # Jump Equal
JNE = 0b01010110 # Jump - Not Equal
# ALU
ADD = 0b10100000 # Add
MUL = 0b10100010 # Multiply
CMP = 0b10100111 # Compare
SUB = 0b10100001 # Subtract
OR  = 0b10101010 # Bitwise OR
XOR = 0b10101011 # Bitwise XOR
AND = 0b10101000 # Bitwise AND


import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False # Starts/stops the program with a boolean
        self.pc = 0 # Program counter, address of current instruction
        self.fl = 0b00000000 # Flags register
        self.reg = [0] * 8 # Holds 8 bytes of data aka registers
        self.ram = [0] * 256 # Holds 256 bytes of data
        self.reg[SP] = 0xf4 # Stack pointer, keeps track of the address of the top of the stack
        self.ops = {} # Branch table
        self.ops[LDI] = self.LDI
        self.ops[PRN] = self.PRN
        self.ops[ADD] = self.ADD
        self.ops[MUL] = self.MUL
        self.ops[HLT] = self.HLT
        self.ops[PUSH] = self.PUSH
        self.ops[POP] = self.POP
        self.ops[CALL] = self.CALL
        self.ops[RET] = self.RET
        self.ops[CMP] = self.CMP
        self.ops[JMP] = self.JMP
        self.ops[JEQ] = self.JEQ
        self.ops[JNE] = self.JNE

    # Stores a value in a register
    def LDI(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.ram_write(address, value)
        self.pc += 3

    # Prints the numeric value stored in register
    def PRN(self):
        address = self.ram[self.pc + 1]
        self.ram_read(address)
        self.pc += 2
    
    # Add the values in two registers and store the result in register A
    def ADD(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('ADD', reg_a, reg_b)
        self.pc += 3

    # Multiply the values in two registers and store the result in register A
    def MUL(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3

    # Halts the CPU
    def HLT(self):
        self.running = False

    # Pushes a value from the register to the ram
    def PUSH(self):
        address = self.ram[self.pc + 1]
        value = self.reg[address]
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = value
        self.pc += 2

    # Overwrite the register number's value to the popped value
    def POP(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.reg[SP]]
        self.reg[address] = value
        self.reg[SP] += 1
        self.pc += 2

        # Transfers control to the return address on the stack
    def RET(self):
        address = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc = address

    # Calls a subroutine (function) at the address stored in the register
    def CALL(self):
        address = self.ram[self.pc + 1]
        value = self.reg[address]
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2
        self.pc = value

    # Sets the PC to the address stored in the given register
    def JMP(self):
        reg = self.ram[self.pc + 1]
        self.pc = self.reg[reg]

    # Compare the values in two registers
    def CMP(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        if self.reg[reg_a] < self.reg[reg_b]:
            self.fl = 0b00000100
        elif self.reg[reg_a] > self.reg[reg_b]:
            self.fl = 0b00000010
        else:
            self.fl = 0b00000001
        self.pc += 3

    # If equal flag is set (true), jump to the address stored in the given register
    def JEQ(self):
        if self.fl == 0b00000001:
            reg = self.ram[self.pc + 1]
            self.pc = self.reg[reg]
        else:
            self.pc += 2

    # If E flag is clear (false, 0), jump to the address stored in the given register.
    def JNE(self):
        if self.fl != 0b00000001:
            reg = self.ram[self.pc + 1]
            self.pc = self.reg[reg]
        else:
            self.pc += 2

    # This sets the parameter value (MDR) at the parameter address in memory (MAR)
    def ram_write(self, address, value):
        self.reg[address] = value

    # This prints the register at the parameter address
    def ram_read(self, address):
        print(self.reg[address])

    def load(self):
        """Load a program into memory."""
        
        # If there are less than 2 arguments, don't run
        if len(sys.argv) != 2:
            return

        # Grab the file name from argv
        path = sys.argv[1]

        # Opens the file
        with open('./examples/' + path) as f:
            lines = f.readlines()

        program = []

        # Loop through the lines in the file
        for line in lines:
            # Remoce all white space
            line = line.strip()
            if '#' in line:
                # Grabs the index for #
                comment_start = line.index('#')
                # If that index is 0, skip it
                if comment_start == 0:
                    continue
                else:
                    # Grabs the instruction
                    binary = int(line[:comment_start].strip(), 2)
                    # Adds the insruction to the program array
                    program.append(binary)
            # Does the same as above if there are no comments        
            elif line:
                binary = int(line, 2)
                program.append(binary)

        address = 0

        # Loops through the program instructions    
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    # Refer to comments above
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        self.running = True

        while self.running:
            ir = self.ram[self.pc]
            self.ops[ir]()