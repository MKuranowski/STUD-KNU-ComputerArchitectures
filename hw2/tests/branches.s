addi x25, x0, 1
addi x26, x0, 42
addi x27, x0, -42
beq x25, x25, A
addi x1, x0, 1
A: beq x25, x26, B
addi x11, x0, 1
B: bne x25, x26, C
addi x2, x0, 1
C: bne x26, x26, D
addi x12, x0, 1
D: blt x27, x25, E
addi x3, x0, 1
E: blt x25, x27, F
addi x13, x0, 1
F: bge x25, x25, G
addi x4, x0, 1
G: bge x26, x25, H
addi x9, x0, 1
H: bge x27, x25, I
addi x14, x0, 1
I: bltu x25, x27, J
addi x5, x0, 1
J: bltu x26, x25, K
addi x15, x0, 1
K: bgeu x25, x25, L
addi x6, x0, 1
L: bgeu x27, x26, M
addi x8, x0, 1
M: bgeu x26, x27, N
addi x16, x0, 1
N: addi x21, x0, 10
loop: add x20, x20, x21
addi x21, x21, -1
bge x21, x0, loop
lui x31, 912092
addi x31, x31, -273
