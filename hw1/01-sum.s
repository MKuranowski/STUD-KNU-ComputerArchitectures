# Student: Mikolaj Kuranowski
# Student ID: 2020427681
# Date: 2022-10-14

	mv x10, zero
	li x11, 2
	li x12, 1000
	# No need to check the condition on first iteration of the loop, as 2 is always <= 1000.
	# This reduces the amount of jumps required.
loop:
	add x10, x10, x11
	addi x11, x11, 2
	ble x11, x12, loop
