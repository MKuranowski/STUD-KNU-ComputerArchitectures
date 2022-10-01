# x10 - x15 -th fibonacci number
# x11 - x15+1 -th fibonacci number
# x12 - index of target fibonacci number
# x15 - loop accumulator
# x16 - temporary value (for swap)
	mv x10, zero
	li x11, 1
	li x12, 15
	mv x15, zero
loop:
	bge t0, x12, end
	add x16, x10, x11
	mv x10, x11
	mv x11, x16
	addi x15, x15, 1
	blt x15, x12, loop
end:
