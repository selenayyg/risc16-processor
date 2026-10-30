# RISC-16 Test Program 2: Memory Operations
# Tests: LW, SW, Memory addressing

# Initialize base address (r1 = 0x100 = 256)
addi r1, r0, 16     # r1 = 16 (base address in data memory)

# Store values to memory
addi r2, r0, 10     # r2 = 10
sw r2, 0(r1)        # mem[16] = 10

addi r3, r0, 20     # r3 = 20
sw r3, 2(r1)        # mem[18] = 20

addi r4, r0, 30     # r4 = 30
sw r4, 4(r1)        # mem[20] = 30

# Load values from memory
lw r5, 0(r1)        # r5 = mem[16] = 10
lw r6, 2(r1)        # r6 = mem[18] = 20

# Add loaded values
add r7, r5, r6      # r7 = 10 + 20 = 30

# Final: r5=10, r6=20, r7=30
nop
