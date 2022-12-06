'''
Simple RISC-V Assembler

Usage: python ./assembler.py ./path-to-RISC-V-Assembler-code/your-asm-code.S ./name-of-executable-file

'name-of-executable-file' will be the input of your riscv_sim
'''

import sys
import re

def twos_com(n):
    s = bin(n & int("1"* 32, 2))[2:]
    return ("{0:0>%s}" % (32)).format(s)

riscv_asm = sys.argv[1] if len(sys.argv) >= 2 else None
machine_code = sys.argv[2] if len(sys.argv) >= 3 else None

_fp_read = open(riscv_asm, "r") if riscv_asm else sys.stdin
_fp_write = open(machine_code, "w") if machine_code else sys.stdout

r_format = ['add', 'sub', 'mul', 'div', 'rem', 'or', 'xor', 'and', 'sll', 'srl']
i_format = ['lw', 'addi', 'slli', 'srli', 'xori', 'ori', 'andi', 'jalr']
u_format = ['lui', 'auipc']
s_format = ['sw']
b_format = ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']

r_inst = ['0000000000', '0100000000', '0000001000', '0000001100', '0000001110', '0000000110', '0000000100', '0000000111', '0000000001', '0000000101']
i_inst = ['0100000011', '0000010011', '0010010011', '1010010011', '1000010011', '1100010011', '1110010011', '0001100111']
u_inst = ['0110111', '0010111']
b_inst = ['000', '001', '100', '101', '110', '111']

line_cnt = 0
labels = {}

for line in _fp_read:
    line_cnt += 1
    if ":" in line:
        labels[line.split(':')[0]] = line_cnt

_fp_read.seek(0)

line_cnt = 0
for line in _fp_read:
    line_cnt += 1
    if '(' in line:
        # jalr x12, 128(x1)
        line = line.split(',')[0] + ', ' + line.split(',')[1].split('(')[1].split(')')[0] + ', ' + line.split(',')[1].lstrip().split('(')[0]
    if ':' in line:
        temp = re.split(r', | |\n', line[line.index(':')+1:])
        del temp[0]
    else:
        temp = re.split(r', | |\n', line)
    mnemonic = temp[0]
    if mnemonic in r_format:
        rs1 = format(bin(int(temp[2][1:]))[2:], '0>5')
        rs2 = format(bin(int(temp[3][1:]))[2:], '0>5')
        rd = format(bin(int(temp[1][1:]))[2:], '0>5')
        i = r_format.index(mnemonic)
        _fp_write.write(r_inst[i][:7] + rs2 + rs1 + r_inst[i][7:] + rd + '0110011')
    elif mnemonic in i_format:
        rd1 = format(bin(int(temp[1][1:]))[2:], '0>5')
        rs1 = format(bin(int(temp[2][1:]))[2:], '0>5')
        imm = twos_com(int(temp[3]))
        i = i_format.index(mnemonic)
        _fp_write.write(imm[-12:] + rs1 + i_inst[i][:3] + rd1 + i_inst[i][3:])
    elif mnemonic in u_format:
        rd = format(bin(int(temp[1][1:]))[2:], '0>5')
        imm = twos_com(int(temp[2]))
        i = u_format.index(mnemonic)
        _fp_write.write(imm[-20:] + rd + u_inst[i])
    elif mnemonic in b_format:
        rs1 = format(bin(int(temp[1][1:]))[2:], '0>5')
        rs2 = format(bin(int(temp[2][1:]))[2:], '0>5')
        imm = twos_com((labels[temp[3]] - line_cnt) * 4)
        i = b_format.index(mnemonic)
        _fp_write.write(imm[-13] + imm[-11:-5] + rs2 + rs1 + b_inst[i] + imm[-5:-1] + imm[-12] + '1100011')
    elif mnemonic in s_format:
        rs1 = format(bin(int(temp[1][1:]))[2:], '0>5')
        rs2 = format(bin(int(temp[2][1:]))[2:], '0>5')
        imm = twos_com(int(temp[3]))
        i = s_format.index(mnemonic)
        _fp_write.write(imm[-12:-5] + rs2 + rs1 + '010' + imm[-5:] + '0100011')
    elif mnemonic == 'jal':
        rd1 = format(bin(int(temp[1][1:]))[2:], '0>5')
        imm = twos_com((labels[temp[2]] - line_cnt) * 4)
        _fp_write.write(imm[-21] + imm[-11:-1] + imm[-12] + imm[-20:-12] + rd1 + '1101111')

    _fp_write.write('\n')


_fp_read.close()
_fp_write.close()

# List of instructions
'''
- Memory operations:
LW, SW

- Arithmetic and logical operations:
SLL, SLLI, SRL, SRLI, ADD, ADDI, SUB, LUI, AUIPC, OR, XOR, AND, XORI, ORI, ANDI
MUL, DIV, REM

- Branch:
BEQ, BNE, BLT, BGE, BLTU, BGEU

- Jump:
JAL, JALR
'''

'''
LW      : imm(12) | rs1(5) | 010 | rd(5) | 0000011
SW      : imm[11:5] | rs2 | rs1 | 010 | imm[4:0] | 0100011
'''


'''
ADD     : 0000000 | rs2 | rs1 | 000 | rd | 0110011
SUB     : 0010100 | rs2 | rs1 | 000 | rd | 0110011
MUL     : 0000001 | rs2 | rs1 | 000 | rd | 0110011
DIV     : 0000001 | rs2 | rs1 | 100 | rd | 0110011
REM     : 0000001 | rs2 | rs1 | 110 | rd | 0110011
OR      : 0000000 | rs2 | rs1 | 110 | rd | 0110011
XOR     : 0000000 | rs2 | rs1 | 100 | rd | 0110011
AND     : 0000000 | rs2 | rs1 | 111 | rd | 0110011

SLL     : 0000000 | rs2 | rs1 | 001 | rd | 0110011
SRL     : 0000000 | rs2 | rs1 | 101 | rd | 0110011
'''


'''
ADDI    : imm[11:0] | rs1 | 000 | rd | 0010011
SLLI    : 00000xxxxxxx | rs1 | 001 | rd | 0010011
SRLI    : 00000xxxxxxx | rs1 | 101 | rd | 0010011
XORI    : imm[11:0] | rs1 | 100 | rd | 0010011
ORI     : imm[11:0] | rs1 | 110 | rd | 0010011
ANDI    : imm[11:0] | rs1 | 111 | rd | 0010011

LUI     : imm[31:12] | rd | 0110111
AUIPC   : imm[31:12] | rd | 0010111

BEQ     : imm[12|10:5] | rs2 | rs1 | 000 | imm[4:1|11] | 1100011
BNE     : imm[12|10:5] | rs2 | rs1 | 001 | imm[4:1|11] | 1100011
BLT     : imm[12|10:5] | rs2 | rs1 | 100 | imm[4:1|11] | 1100011
BGE     : imm[12|10:5] | rs2 | rs1 | 101 | imm[4:1|11] | 1100011
BLTU    : imm[12|10:5] | rs2 | rs1 | 110 | imm[4:1|11] | 1100011
BGEU    : imm[12|10:5] | rs2 | rs1 | 111 | imm[4:1|11] | 1100011

JAL     : imm[20|10:1|11|19:12] | rd | 1101111
JALR    : imm[11:0] | rs1 | 000 | rd | 1100111

'''
