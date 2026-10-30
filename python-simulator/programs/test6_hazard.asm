# RISC-16 Test Program 6: Data Hazards
# Tests: RAW hazards, forwarding

# Test 1: RAW hazard (back-to-back dependency)
addi r1, r0, 5      # r1 = 5
add r2, r1, r1      # r2 = r1 + r1 = 10 (needs r1 from previous)
add r3, r2, r1      # r3 = r2 + r1 = 15 (needs r2 from previous)

# Test 2: Load-use hazard (requires stall)
addi r4, r0, 16     # r4 = 16 (memory address)
addi r5, r0, 25     # r5 = 25
sw r5, 0(r4)        # mem[16] = 25
lw r6, 0(r4)        # r6 = mem[16] = 25
add r7, r6, r1      # r7 = r6 + r1 = 30 (load-use hazard!)

# Final: r1=5, r2=10, r3=15, r6=25, r7=30
nop
