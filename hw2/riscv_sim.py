from ctypes import c_int32, c_uint32
from typing import Iterable

REGISTERS = 32
IMEM_SIZE = 32 * 1024
DMEM_SIZE = 32 * 1024


class RegisterValue(int):
    """RegisterValue represents a value stored in a register: a 32-bit integer"""

    @classmethod
    def from_int(cls, x: int) -> "RegisterValue":
        return cls(c_uint32(x).value)

    def as_unsigned(self) -> int:
        return c_uint32(self).value

    def as_signed(self) -> int:
        return c_int32(self).value


class Processor:
    __slots__ = ("clock", "pc", "registers", "imem", "dmem", "touched_memory")

    clock: int
    pc: int
    registers: list[RegisterValue]
    imem: bytearray
    dmem: bytearray
    touched_memory: set[int]

    def __init__(self) -> None:
        self.reset_state()

    def instruction_fetch(self, address: int) -> int:
        raise NotImplementedError

    def instruction_decode(self, address_rs1: int, address_rs2: int) -> int:
        raise NotImplementedError

    def execute(self, a: int, b: int, alu_selector: int) -> int:
        raise NotImplementedError

    def memory(self, address: int, data: int, mem_rw: int) -> int:
        raise NotImplementedError

    def write_back(self, address: int, address_rd: int, reg_wen: int) -> int:
        raise NotImplementedError

    def control_unit(self, instruction: int, br_equal: int, br_less_than: int) -> int:
        raise NotImplementedError

    def reset_state(self) -> None:
        self.clock = 0
        self.pc = 0
        self.registers = [RegisterValue.from_int(0) for _ in range(REGISTERS)]
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
            self.execute(0, 0, 0)
            self.memory(0, 0, 0)
            self.write_back(0, 0, 0)
            self.control_unit(0, 0, 0)

            self.clock += 1

    def load_program(self, program: Iterable[str]) -> None:
        raise NotImplementedError

    def run(self, program: Iterable[str]) -> None:
        self.reset_state()
        self.load_program(program)
        self.main_loop()
        self.print_statistics()
        self.dump_registers()
        self.dump_memory()
