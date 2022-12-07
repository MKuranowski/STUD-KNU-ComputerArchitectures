- [ ] deadbeef.s and test.s - halting condition not satisfied
- [ ] deadbeef.s - invalid immediate, as they are sign extended
    should be `lui x31, 0xDEADC; addi x31, x31, 0xEEF`; aka:
    `lui x31, 912092; addi x31, x31, -273`
- [ ] assembler.py - wrong binary for `sub` instructions (should be `"0100000" "000"`)
- [ ] assembler.py - error when assembling `sw`
- [ ] riscv_sim.c - integer sizes
- [ ] riscv_sim.py - mul/div/rem and rounding
- [ ] riscv_sim.py - conversion between signed and unsigned not easy
