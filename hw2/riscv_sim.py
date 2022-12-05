from dataclasses import dataclass
from typing import Iterable, Literal, NamedTuple, IO, Iterator
from contextlib import contextmanager
from enum import IntEnum
import sys

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


def sign_extend(x: int, bits: int) -> int:
    assert x < 2**bits, f"{x} is wider than {bits} bits"
    if x & (1 << (bits - 1)):
        # MSB set - negative
        return x - 2**bits
    else:
        return x


def div_towards_zero(a: int, b: int) -> int:
    # NOTE: Python uses different rounding compared with RISC-V expects
    # Source: https://stackoverflow.com/a/61386872
    if (a >= 0) != (b >= 0) and a % b:
        return a // b + 1
    else:
        return a // b


def mod_towards_zero(a: int, b: int) -> int:
    # NOTE: Python uses different rounding compared with RISC-V expects
    # Source: https://stackoverflow.com/a/61346631
    if b < 0:
        b = -b
    return -1 * (-a % b) if a < 0 else a % b



class WBSelector(IntEnum):
    NONE = 0
    ALU = 1
    MEMORY = 2
    PC_PLUS_4 = 3


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


class BranchSelector(IntEnum):
    # NOTE: Values of funct3 of B-instructions
    BEQ = 0b000
    BNE = 0b001
    BLT = 0b100
    BGE = 0b101
    BLTU = 0b110
    BGEU = 0b111


class OP(IntEnum):
    ALU_REG = 0b0110011
    ALU_IMM = 0b0010011
    LOAD = 0b0000011
    STORE = 0b0100011
    BRANCH = 0b1100011
    JAL = 0b1101111
    JALR = 0b1100111
    LUI = 0b0110111
    AUIPC = 0b0010111


@dataclass
class ControlFlags:
    pc_sel: bool = False  # If True, use ALU output instead of PC+4 for next PC
    a_sel: bool = False  # If True, use PC instead of decoded `a` for ALU input
    b_sel: bool = False  # If True, use IMM instead of decoded `b` for ALU input
    br_un: bool = False  # If True, use unsigned comparison instead of signed
    wb_sel: WBSelector = WBSelector.NONE  # Decides which value to store in dest register

    def clear(self) -> None:
        self.pc_sel = False
        self.a_sel = False
        self.b_sel = False
        self.br_un = False
        self.wb_sel = WBSelector.NONE


class DecodedInstruction(NamedTuple):
    op: OP
    funct: int  # (funct7 << 4) | funct3

    rs1_value: int32
    rs2_value: int32
    rd_number: int
    imm: int


class Processor:
    __slots__ = ("clock", "pc", "registers", "flags", "imem", "dmem", "touched_memory")

    clock: int
    pc: int
    registers: list[int32]
    flags: ControlFlags
    imem: bytearray
    dmem: bytearray
    touched_memory: set[int]

    def __init__(self) -> None:
        self.reset_state()

    def instruction_fetch(self, address: int) -> int:
        return int.from_bytes(self.imem[address : address + 4], BYTE_ORDER)

    # NOTE: With irrelevant for this simulator exceptions, all immediate values are
    #       sign extended. See section 2.2 of RISC-V Instruction Set Manual.

    @staticmethod
    def reconstruct_i_imm(i: int) -> int:
        return sign_extend((i >> 20) & 0xFFF, 12)

    @staticmethod
    def reconstruct_u_imm(i: int) -> int:
        return sign_extend(i & 0xFFFF_F000, 32)

    @staticmethod
    def reconstruct_s_imm(i: int) -> int:
        bits_0_4 = (i >> 7) & 0x1F
        bits_5_11 = (i >> 25) & 0x7F
        return sign_extend((bits_5_11 << 5) | bits_0_4, 12)

    @staticmethod
    def reconstruct_b_imm(i: int) -> int:
        bits_1_4 = (i >> 8) & 0xF
        bits_5_10 = (i >> 25) & 0x1F
        bit_11 = (i >> 7) & 0x1
        bit_12 = (i >> 31) & 0x1
        return sign_extend(
            (bits_1_4 << 1) | (bits_5_10 << 5) | (bit_11 << 11) | (bit_12 << 12),
            13,
        )

    @staticmethod
    def reconstruct_j_imm(i: int) -> int:
        bits_1_10 = (i >> 20) & 0x3FF
        bit_11 = (i >> 19) & 0x1
        bits_12_19 = (i >> 12) & 0xFF
        bit_20 = (i >> 31) & 0x1
        return sign_extend(
            (bits_1_10 << 1) | (bit_11 << 11) | (bits_12_19 << 12) | (bit_20 << 20),
            21,
        )

    def instruction_decode(self, instruction: int) -> DecodedInstruction:
        op = OP(instruction & 0b111_1111)
        funct = 0
        rs1_value = int32(0)
        rs2_value = int32(0)
        rd_number = 0
        imm = 0

        match op:
            case OP.ALU_REG:  # R-Type instructions
                funct = (((instruction >> 25) & 0x7F) << 4) | ((instruction >> 12) & 0b111)
                rs1_value = self.registers[(instruction >> 15) & 0b1_1111]
                rs2_value = self.registers[(instruction >> 20) & 0b1_1111]
                rd_number = (instruction >> 7) & 0b1_1111

                self.flags.wb_sel = WBSelector.ALU

            case OP.ALU_IMM | OP.LOAD | OP.JALR:  # I-type instructions
                funct = (instruction >> 12) & 0b111
                rs1_value = self.registers[(instruction >> 15) & 0b1_1111]
                rd_number = (instruction >> 7) & 0b1_1111
                imm = self.reconstruct_i_imm(instruction)

                self.flags.pc_sel = op == op.JALR
                self.flags.b_sel = True
                if op == OP.LOAD:
                    self.flags.wb_sel = WBSelector.MEMORY
                elif op == op.JALR:
                    self.flags.wb_sel = WBSelector.PC_PLUS_4
                else:
                    self.flags.wb_sel = WBSelector.ALU

            case OP.STORE:  # S-type instructions
                funct = (instruction >> 12) & 0b111
                rs1_value = self.registers[(instruction >> 15) & 0b1_1111]
                rs2_value = self.registers[(instruction >> 20) & 0b1_1111]
                imm = self.reconstruct_s_imm(instruction)

                self.flags.b_sel = True

            case OP.BRANCH:  # B-type instructions
                funct = (instruction >> 12) & 0b111
                rs1_value = self.registers[(instruction >> 15) & 0b1_1111]
                rs2_value = self.registers[(instruction >> 20) & 0b1_1111]
                imm = self.reconstruct_b_imm(instruction)

                self.flags.a_sel = True
                self.flags.b_sel = True
                self.flags.br_un = funct & 0b010 != 0

            case OP.JAL:  # J-type instructions
                rd_number = (instruction >> 7) & 0b1_1111
                imm = self.reconstruct_j_imm(instruction)

                self.flags.pc_sel = True
                self.flags.a_sel = True
                self.flags.b_sel = True
                self.flags.wb_sel = WBSelector.PC_PLUS_4

            case OP.LUI | OP.AUIPC:  # U-type instructions
                # NOTE: rs1_value is zero on entry to this function
                rd_number = (instruction >> 7) & 0b1_1111
                imm = self.reconstruct_u_imm(instruction)

                self.flags.a_sel = op == OP.AUIPC
                self.flags.b_sel = True
                self.flags.wb_sel = WBSelector.ALU

        return DecodedInstruction(op, funct, rs1_value, rs2_value, rd_number, imm)

    @staticmethod
    def run_alu(a: int32, b: int32, alu_selector: ALUSelector) -> int:
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
                return a.as_signed() * b.as_signed()
            case ALUSelector.DIV:
                return div_towards_zero(a.as_signed(), b.as_signed())
            case ALUSelector.REM:
                return mod_towards_zero(a.as_signed(), b.as_signed())

    def run_branch_selector(self, i: DecodedInstruction) -> None:
        # Perform the comparison
        eq = i.rs1_value == i.rs2_value
        if self.flags.br_un:
            lt = i.rs1_value.as_unsigned() < i.rs2_value.as_unsigned()
        else:
            lt = i.rs1_value.as_signed() < i.rs2_value.as_signed()

        # Set pc_sel according to the result
        match BranchSelector(i.funct):
            case BranchSelector.BEQ:
                self.flags.pc_sel = eq
            case BranchSelector.BNE:
                self.flags.pc_sel = not eq
            case BranchSelector.BLT | BranchSelector.BLTU:
                self.flags.pc_sel = lt
            case BranchSelector.BGE | BranchSelector.BGEU:
                self.flags.pc_sel = not lt

    def execute(self, i: DecodedInstruction) -> int:
        if i.op == OP.BRANCH:
            self.run_branch_selector(i)

        return self.run_alu(
            int32.from_int(self.pc) if self.flags.a_sel else i.rs1_value,
            int32.from_int(i.imm) if self.flags.b_sel else i.rs2_value,
            ALUSelector(i.funct),
        )

    def memory(self, address: int, data: int, do_write: bool) -> int:
        # NOTE: Always reads/writes words
        if do_write:
            self.dmem[address : address + 4] = int32(data).to_bytes(4, BYTE_ORDER)
            self.touched_memory.union(range(address, address + 4))
        else:
            data = int.from_bytes(
                self.dmem[address : address + 4],
                BYTE_ORDER,
            )
        return data

    def write_back(self, memory: int, alu: int, register: int) -> None:
        # Don't write to x0
        if register == 0:
            return

        match self.flags.wb_sel:
            case WBSelector.NONE:
                pass
            case WBSelector.ALU:
                self.registers[register] = int32.from_int(alu)
            case WBSelector.MEMORY:
                self.registers[register] = int32.from_int(memory)
            case WBSelector.PC_PLUS_4:
                self.registers[register] = int32.from_int(self.pc + 4)

    def control_unit(self, alu_result: int) -> None:
        self.pc = alu_result if self.flags.pc_sel else self.pc + 4

    def main_loop(self) -> None:
        while self.registers[31] != 0xDEADBEEF:
            self.flags.clear()
            instruction = self.instruction_fetch(self.pc)

            # XXX: example programs don't properly halt
            if not instruction:
                # print("\x1B[31mProgram halted without 0xDEADBEEF in x31\x1B[0m", file=sys.stderr)
                return

            decoded = self.instruction_decode(instruction)
            alu_result = self.execute(decoded)
            if decoded.op == OP.STORE or decoded.op == OP.LOAD:
                mem_result = self.memory(
                    alu_result,
                    decoded.rs2_value.as_unsigned(),
                    decoded.op == OP.STORE,
                )
            else:
                mem_result = 0
            self.write_back(mem_result, alu_result, decoded.rd_number)
            self.control_unit(alu_result)

            self.clock += 1

    def reset_state(self) -> None:
        self.clock = 0
        self.pc = 0
        self.registers = [int32.from_int(0) for _ in range(REGISTERS)]
        self.flags = ControlFlags()
        self.imem = bytearray(IMEM_SIZE)
        self.dmem = bytearray(DMEM_SIZE)
        self.touched_memory = set()

    def print_statistics(self) -> None:
        print("Processor's clock cycles:", self.clock)

    def dump_registers(self) -> None:
        print(">>>>>>>>[REGISTER DUMP]<<<<<<<")
        print(f"PC: = {self.pc}")
        for register_number, register_value in enumerate(self.registers):
            print(f"x{register_number:02d} = {register_value.as_signed()}")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    def dump_memory(self) -> None:
        print(">>>>>>>>[MEMORY DUMP]<<<<<<<<<")
        for touched_address in sorted(self.touched_memory):
            print(f"{touched_address:x} : {self.dmem[touched_address]}")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    def load_program(self, program: Iterable[str]) -> None:
        address = 0
        for line in program:
            instruction = int(line.strip(), 2)
            self.imem[address : address + 4] = instruction.to_bytes(4, BYTE_ORDER)
            address += 4

    def run(self, program: Iterable[str]) -> None:
        self.reset_state()
        self.load_program(program)
        self.main_loop()
        self.print_statistics()
        self.dump_registers()
        self.dump_memory()


@contextmanager
def input_or_stdin() -> Iterator[IO[str]]:
    if len(sys.argv) < 2:
        yield sys.stdin
    else:
        with open(sys.argv[1], "r") as f:
            yield f


if __name__ == "__main__":
    with input_or_stdin() as f:
        Processor().run(f)
