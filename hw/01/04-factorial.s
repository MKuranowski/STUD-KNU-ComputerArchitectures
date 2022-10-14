# Student: Mikolaj Kuranowski
# Student ID: 2020427681
# Date: 2022-10-14

_start:
	# Calculate 6!
	li a0, 6
	call factorial

	# Print the result
	mv a0, a1
	li a7, 36
	ecall

	# Exit the program
	li a7, 10
	ecall

# ==========
# Procedure `unsigned factorial(unsigned)`
# ==========
# Arguments:
# - a0: n
# ==========
# Return value:
# - a1: n!
# ==========
factorial:
	# Base recursion case
	li t0, 1
	bgtu a0, t0, .recur
	mv a1, a0
	ret
.recur:
	# Recursive case - store a0 and ra on the stack
	addi sp, sp, -8
	sw ra, 0(sp)
	sw a0, 4(sp)

	# Calculate (n-1)!
	addi a0, a0, -1
	call factorial

	# Calclate n! by n * (n-1!)
	lw t0, 4(sp)
	mul a1, a1, t0

	# Resotre ra and sp
	lw ra, 0(sp)
	addi sp, sp, 8
	ret
