# Fibonacci Sequence
# Calculate first N fibonacci numbers
# N = 8, Store results in memory starting at address 0

        addi r1, r0, 8      # N = 8 (count)
        addi r2, r0, 0      # fib(0) = 0
        addi r3, r0, 1      # fib(1) = 1
        addi r4, r0, 0      # memory address
        
        # Store first two
        sw   r2, 0(r4)      # mem[0] = 0
        addi r4, r4, 2
        sw   r3, 0(r4)      # mem[2] = 1
        addi r4, r4, 2
        addi r1, r1, -2     # count -= 2
        
loop:   beq  r1, r0, done   # if count == 0, done
        add  r5, r2, r3     # r5 = fib(n-2) + fib(n-1)
        sw   r5, 0(r4)      # store result
        addi r4, r4, 2      # next address
        add  r2, r0, r3     # shift: fib(n-2) = fib(n-1)
        add  r3, r0, r5     # shift: fib(n-1) = fib(n)
        addi r1, r1, -1     # count--
        j    loop
        
done:   halt

# Expected memory: 0, 1, 1, 2, 3, 5, 8, 13
