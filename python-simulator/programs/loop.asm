# Loop Test - Sum 1 to 5
    addi r1, r0, 5      # counter
    addi r2, r0, 0      # sum
loop:
    add  r2, r2, r1     # sum += counter
    addi r1, r1, -1     # counter--
    bne  r1, r0, loop   # if counter != 0
    halt
