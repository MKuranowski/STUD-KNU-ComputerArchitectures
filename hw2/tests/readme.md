[x] SLLI (tested in immediates.s)
[x] SRLI (tested in immediates.s)
[x] ADDI (tested in immediates.s)
[x] AUIPC (tested in immediates.s)
[x] XORI (tested in immediates.s)
[x] ANDI (tested in immediates.s)
[x] ORI (tested in immediates.s)
[x] ADD (tested in arithmetic.s )
[x] SUB (tested in arithmetic.s)
[x] SLL (tested in arithmetic.s)
[x] SRL (tested in arithmetic.s)
[x] LUI (tested in arithmetic.s)
[x] XOR (tested in arithmetic.s)
[x] AND (tested in arithmetic.s)
[x] OR (tested in arithmetic.s)
[ ] MUL
[ ] DIV
[ ] REM
[ ] LW
[ ] SW
[ ] BEQ
[ ] BNE
[ ] BLT
[ ] BGE
[ ] BLTU
[ ] BGEU
[ ] JAL
[ ] JALR

## immideates.s

```
x31 = 0 + (5800<<12) = 23756800
x1 = 10 + 20 - 1 = 29
x2 = 2 << 6 = 128
x3 = 45 >> 2 = 11
x4 = 819 ^ 341 = 614
x5 = 819 & 341 = 273
x6 = 819 | 341 = 887
```

## arithmetic.s

```
x20 = 819
x21 = 341
x22 = -42
x23 = 45
x24 = 2
x25 = 6

x1 = 819 + 341 - 42 = 1118
x2 = 341 - 819 + 42 = -436
x3 = 45 << 6 = 2880
x4 = 45 >> 2 = 11
x5 = 819 ^ 341 = 614
x6 = 819 & 341 = 273
x7 = 819 | 341 = 887
```

## mul.s

```
x20 = 1961
x21 = 83
x22 = -13
x23 = -27
x1 = 1961 // 83 = 23
x2 = 1961 % 83 = 52
x3 = 1961 * 83 = 162763
x4 = 1961 // -13 = -150
x5 = 1961 % -13 = 11
x6 = 1961 * -13 = -25493
x7 = -27 // -13 = 2
x8 = -27 % -13 = -1
x9 = -27 * -13 = 351
x10 = -13 // 83 = 0
x11 = -13 % 83 = -13
x12 = -13 * 83 = -1079
```

NOTE: Python uses different rounding compared to what RISC-V expects.


## overflow.s

TODO!

## memory.s

TODO!

## branches.s

TODO!

## jump_and_link.s

TODO!
