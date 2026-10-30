# Load-Use Hazard Test - Stall gerektirir
# Memory[0] = 42, R1 = Memory[0], R2 = R1 + 1

    addi r1, r0, 42     # R1 = 42
    sw   r1, 0(r0)      # Memory[0] = 42
    lw   r2, 0(r0)      # R2 = Memory[0] = 42
    addi r3, r2, 1      # R3 = R2 + 1 = 43 (load-use hazard - stall)
    halt
