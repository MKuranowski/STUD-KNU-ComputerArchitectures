add x10, x0, x0
addi x11, x0, 10
add x12, x0, x0
loop: add x12, x12, x11
addi x10, x10, 1
blt x10, x11, loop
lui x31, 912092
addi x31, x31, -273
