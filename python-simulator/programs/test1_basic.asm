# RISC-16 Test Program 1: Basic Operations
# Tests: ADDI, ADD, SUB, AND, OR

# Initialize registers
addi r1, r0, 5      # r1 = 5
addi r2, r0, 3      # r2 = 3

# Arithmetic operations
add r3, r1, r2      # r3 = r1 + r2 = 8
sub r4, r1, r2      # r4 = r1 - r2 = 2

# Logical operations
and r5, r1, r2      # r5 = r1 & r2 = 1 (0101 & 0011 = 0001)
or  r6, r1, r2      # r6 = r1 | r2 = 7 (0101 | 0011 = 0111)

# Final: r1=5, r2=3, r3=8, r4=2, r5=1, r6=7
nop
