from typing import Iterable, Literal
from enum import IntEnum

REGISTERS = 32
IMEM_SIZE = 32 * 1024
DMEM_SIZE = 32 * 1024
BYTE_ORDER: Literal["big", "little"] = "big"


class int32(int):
    """int32 represents a value stored in a register: a 32-bit integer"""

    @classmethod
    def from_int(cls, x: int) -> "int32":
        return cls(x % 2**32)

    def as_unsigned(self) -> int:
        return self

    def as_signed(self) -> int:
        if self & 0x8000_0000:
            return self - 2**32  # negative
        else:
            return self  # non-negative


class WBSelector(IntEnum):
    MEMORY = 0
    ALU = 1


class ALUSelector(IntEnum):
    # NOTE: Values the following format `(funct7 << 4) | funct3` (of R-instructions)
    ADD = 0x0
    SUB = 0x200
    XOR = 0x4
    OR = 0x6
    AND = 0x7
    SLL = 0x1
    SRL = 0x5
    MUL = 0x10
    DIV = 0x14
    REM = 0x16


class Processor:
    __slots__ = ("clock", "pc", "registers", "imem", "dmem", "touched_memory")

    clock: int
    pc: int
    registers: list[int32]
    imem: bytearray
    dmem: bytearray
    touched_memory: set[int]

    def __init__(self) -> None:
        self.reset_state()

    def instruction_fetch(self, address: int) -> int:
        raise NotImplementedError

    def instruction_decode(self, address_rs1: int, address_rs2: int) -> int:
        raise NotImplementedError

    def execute(self, a: int, b: int, alu_selector: ALUSelector) -> int:
        match alu_selector:
            case ALUSelector.ADD:
                return a + b
            case ALUSelector.SUB:
                return a - b
            case ALUSelector.XOR:
                return a ^ b
            case ALUSelector.OR:
                return a | b
            case ALUSelector.AND:
                return a & b
            case ALUSelector.SLL:
                return a << b
            case ALUSelector.SRL:
                return a >> b
            case ALUSelector.MUL:
                return a * b
            case ALUSelector.DIV:
                return a // b
            case ALUSelector.REM:
                return a % b

    def memory(self, address: int, data: int, do_write: bool) -> int:
        # NOTE: Always reads/writes words
        if do_write:
            self.dmem[address:address+4] = int32(data).to_bytes(4, BYTE_ORDER)
            self.touched_memory.union(range(address, address+4))
        else:
            data = int.from_bytes(self.dmem[address:address+4], BYTE_ORDER)
        return data

    def write_back(self, memory: int, alu: int, register: int, selector: WBSelector) -> None:
        match selector:
            case WBSelector.MEMORY:
                self.registers[register] = int32.from_int(memory)
            case WBSelector.ALU:
                self.registers[register] = int32.from_int(alu)

    def control_unit(self, instruction: int, br_equal: int, br_less_than: int) -> int:
        raise NotImplementedError

    def reset_state(self) -> None:
        self.clock = 0
        self.pc = 0
        self.registers = [int32.from_int(0) for _ in range(REGISTERS)]
        self.imem = bytearray(IMEM_SIZE)
        self.dmem = bytearray(DMEM_SIZE)
        self.touched_memory = set()

    def print_statistics(self) -> None:
        print("Processor's clock cycles:", self.clock)

    def dump_registers(self) -> None:
        print(">>>>>>>>[REGISTER DUMP]<<<<<<<");
        print(f"PC: = {self.pc}");
        for register_number, register_value in enumerate(self.registers):
            print(f"x{register_number:02d} = {register_value.as_signed()}")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");

    def dump_memory(self) -> None:
        print(">>>>>>>>[MEMORY DUMP]<<<<<<<<<")
        for touched_address in sorted(self.touched_memory):
            print(f"{touched_address:x} : {self.dmem[touched_address]}")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    def main_loop(self) -> None:
        while self.registers[31] != 0xDEADBEEF:
            self.instruction_fetch(self.pc)
            self.instruction_decode(0, 0)
            self.execute(0, 0, ALUSelector.ADD)
            self.memory(0, 0, False)
            self.write_back(0, 0, 0, WBSelector.MEMORY)
            self.control_unit(0, 0, 0)

            self.clock += 1

    def load_program(self, program: Iterable[str]) -> None:
        address = 0
        for line in program:
            instruction = int(line.strip(), 2)
            self.imem[address:address+4] = instruction.to_bytes(4, BYTE_ORDER)
            address += 4

    def run(self, program: Iterable[str]) -> None:
        self.reset_state()
        self.load_program(program)
        self.main_loop()
        self.print_statistics()
        self.dump_registers()
        self.dump_memory()
