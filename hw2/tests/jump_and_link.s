addi x10, x0, 20
jalr x1, x10, 0
jal x9, over
setterZ: addi x14, x0, 1
jalr x0, x4, 0
setterA: addi x11, x0, 1
jalr x0, x1, 0
setterB: addi x12, x0, 1
jalr x0, x2, 0
setterC: addi x13, x0, 1
jalr x0, x3, 0
over: jalr x2, x10, 8
jal x3, setterC
jalr x4, x10, -8
lui x31, 912092
addi x31, x31, -273
