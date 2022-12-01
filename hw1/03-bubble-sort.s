# Student: Mikolaj Kuranowski
# Student ID: 2020427681
# Date: 2022-10-14

_start:
	# Sort the numbers
	la a0, arr
	li a1, 20
	call bubble_sort

	# Print the sorted array
	la s0, arr
	addi s1, s0, 80  # Pointer to the first element past the array ("end iterator")
.loop:
	# Print the number
	lw a0, (s0)
	li a7, 1
	ecall

	# Print a space
	li a0, ' '
	li a7, 11
	ecall

	# Advance the pointer
	addi s0, s0, 4
	blt s0, s1, .loop

	# Exit the program
	li a7, 10
	ecall


# ==========
# Procedure `void bubble_sort(int*, int)`
# ==========
# Arguments:
# - a0: pointer to the first element of the array
# - a1: number of elements in the array
# ==========
# No return value
# ==========
# Local variables:
# - t0: outer loop counter
# - t1: inner loop counter
# - t2: inner loop max value
# - t3: arr + j
# - t4: arr[j]
# - t5: arr[j+1]
# ==========
bubble_sort:
	addi a1, a1, -1  # All loops do comparisons with a number one less than the length of the array
	mv t0, zero
	bge t0, a1, .end
.outer_loop:
	mv t1, zero
	sub t2, a1, t0
	bge t1, t2, .inner_end
.inner_loop:
	slli t3, t1, 2  # multiply j by 4 to get the offset in bytes
	add t3, t3, a0  # add the base pointer of the array
	lw t4, (t3)
	lw t5, 4(t3)
	ble t4, t5, .no_swap
	sw t4, 4(t3)
	sw t5, (t3)
.no_swap:
	addi t1, t1, 1
	blt t1, t2, .inner_loop
.inner_end:
	addi t0, t0, 1
	blt t0, a1, .outer_loop
.end:
	ret

.data
arr: .word 7, 5, 12, 92, 8, 68, 0, 13, 158, 27, 99, 112, 140, 118, 117, 221, 8, 21, 19, 5
