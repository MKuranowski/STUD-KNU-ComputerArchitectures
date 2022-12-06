[x] SLLI (tested in immediates.s)
[x] SRLI (tested in immediates.s)
[x] ADDI (tested in immediates.s)
[x] AUIPC (tested in immediates.s)
[x] XORI (tested in immediates.s)
[x] ANDI (tested in immediates.s)
[x] ORI (tested in immediates.s)
[x] ADD (tested in arithmetic.s)
[x] SUB (tested in arithmetic.s)
[x] SLL (tested in arithmetic.s)
[x] SRL (tested in arithmetic.s)
[x] LUI (tested in arithmetic.s)
[x] XOR (tested in arithmetic.s)
[x] AND (tested in arithmetic.s)
[x] OR (tested in arithmetic.s)
[x] MUL (tested in mul.s)
[x] DIV (tested in mul.s)
[x] REM (tested in mul.s)
[x] LW (tested in memory.s)
[x] SW (tested in memory.s)
[x] BEQ (tested in branches.s)
[x] BNE (tested in branches.s)
[x] BLT (tested in branches.s)
[x] BGE (tested in branches.s)
[x] BLTU (tested in branches.s)
[x] BGEU (tested in branches.s)
[ ] JAL
[ ] JALR

## Halting

As per the assignment, the machine shall halt if `x31 == 0xDEADBEEF`.

To set x31 to 0xDEADBEEF the following sequence is used:

```
lui x31, 912092
addi x31, x31, -273
```

## write_to_zero.s

```
x0 <= 42
```


## immediates.s

```
x30 = 0 + (5800<<12) = 23756800
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

Checks for proper 32-bit wraparound.

```
x20 = 97411312   = ( 23782 << 12) + 240
x21 = 1699649273 = (414953 << 12) + 1785
x22 = 2147483647 = (     1 << 31) - 1

x1 = 97411312 * 97411312 = 2264195328
x2 = 1699649273 * 1699649273 = -758858191
x3 = 2147483647 + 1 = -2147483648
x4 = 1946 << 24 = -1711276032
x5 = 1946 >> 24 = 0
```

NOTE: x20 and x21 are both deliberately chosen so that `X & 0xFFFF_F7FF == X` -
and so that they can be loaded with LUI and ADDI in a straightforward manner,
without sign extension of the latter causing any problems.

## memory.s

NOTE: Assuming little endian

```
x20 = -1
x21 = 42
x25 = 0x54

word[0x54] = -1
word[0x58] = 42
word[0x50] = 42

x1 = word[0x54] = -1
x2 = word[0x58] = 42
x3 = word[0x50] = 42
```

## branches.s

```
x25 = 1
x26 = 42
x27 = -42 = 4294967254

    if (1 == 1) goto A
    x1 = 1   ; should not be set
A:  if (1 == 42) goto B
    x11 = 1  ; should be set
B:  if (1 != 42) goto C
    x2 = 1   ; should not be set
C:  if (42 != 42) goto D
    x12 = 1  ; should be set
D:  if (-42 < 1) goto E
    x3 = 1   ; should not be set
E:  if (1 < -42) goto F
    x13 = 1  ; should be set
F:  if (1 >= 1) goto G
    x4 = 1   ; should not be set
G:  if (42 >= 1) goto H
    x9 = 1   ; should not be set
H:  if (-42 >= 1) goto I
    x14 = 1  ; should be set
I:  if (1 <u 4294967254) goto J
    x5 = 1   ; should not be set
J:  if (42 <u 1) goto K
    x15 = 1  ; should be set
K: if (1 >=u 1) goto L
    x6 = 1   ; should not be set
L: if (4294967254 >=u 42) goto M
    x8 = 1   ; should not be set
M: if (42 >=u 4294967254) goto N
    x16 = 1  ; should be set
N: x21 = 10
loop: x20 += x21
x21 -= 1
if (x21 >= 0) goto loop
```

x1 ~ x9 should all be zeros  
x11 ~ x16 should all be ones  
x20 should be 55  
x21 should be -1

## jump_and_link.s

TODO!
