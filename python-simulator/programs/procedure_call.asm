# Procedure Call Test (JAL/JR)
# main calls add_func(5, 3), result in R3

main:   addi r1, r0, 5      # arg1 = 5
        addi r2, r0, 3      # arg2 = 3
        jal  add_func       # call add_func, R7 = return address
        # R3 = 8 (return value)
        halt

add_func:
        add  r3, r1, r2     # R3 = R1 + R2
        jr   r7             # return
