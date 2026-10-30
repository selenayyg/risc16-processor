# RISC-16 Test Program 3: Branch Operations
# Tests: BEQ, BNE, Labels

# Initialize
addi r1, r0, 5      # r1 = 5
addi r2, r0, 5      # r2 = 5
addi r3, r0, 3      # r3 = 3

# Test BEQ (should branch)
beq r1, r2, equal   # r1 == r2, should jump to 'equal'
addi r4, r0, 1      # This should be skipped
j end

equal:
    addi r4, r0, 10 # r4 = 10 (BEQ worked)

# Test BNE
bne r1, r3, notequal # r1 != r3, should jump
addi r5, r0, 1      # This should be skipped
j end

notequal:
    addi r5, r0, 20 # r5 = 20 (BNE worked)

end:
    addi r6, r0, 30 # r6 = 30 (reached end)
    nop

# Final: r4=10, r5=20, r6=30
