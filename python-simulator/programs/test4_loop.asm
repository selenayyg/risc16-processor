# RISC-16 Test Program 4: Loop (Sum 1 to 5)
# Tests: Loop with BNE, counter

# Calculate sum = 1 + 2 + 3 + 4 + 5 = 15

# Initialize
addi r1, r0, 0      # r1 = sum = 0
addi r2, r0, 1      # r2 = counter = 1
addi r3, r0, 6      # r3 = limit = 6 (loop while counter < 6)

loop:
    add r1, r1, r2  # sum += counter
    addi r2, r2, 1  # counter++
    bne r2, r3, loop # if counter != 6, continue loop

# Done
# Final: r1 = 15 (sum), r2 = 6 (counter)
nop
