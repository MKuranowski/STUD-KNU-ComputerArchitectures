addi x20, x0, -1
addi x21, x0, 42
addi x25, x0, 84
sw x25, x20, 0
sw x25, x21, 4
sw x25, x21, -4
lw x1, x25, 0
lw x2, x25, 4
lw x3, x25, -4
lui x31, 912092
addi x31, x31, -273
