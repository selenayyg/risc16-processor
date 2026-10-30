# RISC-16 Test Program 5: Function Call (JAL/JR)
# Tests: JAL, JR, subroutine call

# Main program
addi r1, r0, 3      # r1 = 3 (argument)
addi r2, r0, 4      # r2 = 4 (argument)

jal multiply        # Call multiply(r1, r2), result in r3
                    # r7 = return address

# After function call, r3 should have result
addi r4, r0, 1      # r4 = 1 (mark: returned from function)
j end

# ==================
# Function: multiply
# Input: r1, r2
# Output: r3 = r1 * r2 (using repeated addition)
# ==================
multiply:
    addi r3, r0, 0  # r3 = result = 0
    addi r5, r0, 0  # r5 = counter = 0
    
mult_loop:
    beq r5, r1, mult_done  # if counter == r1, done
    add r3, r3, r2  # result += r2
    addi r5, r5, 1  # counter++
    j mult_loop
    
mult_done:
    jr r7           # return (jump to address in r7)

end:
    nop

# Final: r3 = 12 (3 * 4), r4 = 1
