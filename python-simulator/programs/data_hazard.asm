# Data Hazard Test - Forwarding gerektirir
# R1 = 10, R2 = R1 + 5 (RAW hazard)

    addi r1, r0, 10     # R1 = 10
    addi r2, r1, 5      # R2 = R1 + 5 = 15 (R1 henüz yazılmadı - forwarding)
    add  r3, r1, r2     # R3 = R1 + R2 = 25
    halt
