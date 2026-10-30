# Branch Loop Test
# R1'i 5'ten 0'a kadar say (döngü)

        addi r1, r0, 5      # R1 = 5 (counter)
        addi r2, r0, 0      # R2 = 0 (sum)
        
loop:   add  r2, r2, r1     # sum += counter
        addi r1, r1, -1     # counter--
        bne  r1, r0, loop   # if counter != 0, goto loop
        
        # R2 = 5+4+3+2+1 = 15
        halt
