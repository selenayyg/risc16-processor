# RISC-16 Instruction Set Architecture

## Overview
- 16-bit data path
- 8 general-purpose registers (R0-R7)
- 512 bytes instruction memory
- 512 bytes data memory
- 5-stage pipeline (IF → ID → EX → MEM → WB)

## Instruction Formats

### R-Type (Register)
```
[opcode:4][rs:3][rt:3][rd:3][func:3] = 16 bits
```
- **opcode**: 0000 (R-Type identifier)
- **rs**: Source register 1
- **rt**: Source register 2
- **rd**: Destination register
- **func**: Function code (determines operation)

### I-Type (Immediate)
```
[opcode:4][rs:3][rt:3][imm:6] = 16 bits
```
- **opcode**: Operation code
- **rs**: Source register
- **rt**: Target register (destination for loads/addi)
- **imm**: 6-bit signed immediate (-32 to +31)

### J-Type (Jump)
```
[opcode:4][address:12] = 16 bits
```
- **opcode**: Operation code
- **address**: 12-bit jump target (word address)

## Instructions

### R-Type Instructions (opcode = 0000)

| Instruction | Func | Operation | Description |
|-------------|------|-----------|-------------|
| ADD rd, rs, rt | 000 | rd = rs + rt | Addition |
| SUB rd, rs, rt | 001 | rd = rs - rt | Subtraction |
| AND rd, rs, rt | 010 | rd = rs & rt | Bitwise AND |
| OR rd, rs, rt | 011 | rd = rs \| rt | Bitwise OR |
| SLT rd, rs, rt | 100 | rd = (rs < rt) ? 1 : 0 | Set Less Than |
| SLL rd, rt, shamt | 101 | rd = rt << shamt | Shift Left |
| SRL rd, rt, shamt | 110 | rd = rt >> shamt | Shift Right |

### I-Type Instructions

| Instruction | Opcode | Operation | Description |
|-------------|--------|-----------|-------------|
| ADDI rt, rs, imm | 0001 | rt = rs + imm | Add Immediate |
| LW rt, imm(rs) | 0010 | rt = Mem[rs + imm] | Load Word |
| SW rt, imm(rs) | 0011 | Mem[rs + imm] = rt | Store Word |
| BEQ rs, rt, offset | 0100 | if (rs == rt) PC += offset | Branch Equal |
| BNE rs, rt, offset | 0101 | if (rs != rt) PC += offset | Branch Not Equal |

### J-Type Instructions

| Instruction | Opcode | Operation | Description |
|-------------|--------|-----------|-------------|
| J target | 0110 | PC = target | Jump |
| JAL target | 0111 | R7 = PC+2; PC = target | Jump and Link |
| JR rs | 1000 | PC = rs | Jump Register |

## Registers

| Register | Number | Convention |
|----------|--------|------------|
| R0 | 0 | General purpose |
| R1-R6 | 1-6 | General purpose |
| R7 | 7 | Return address (RA) |

## Memory

- **Instruction Memory**: 512 bytes (256 words)
- **Data Memory**: 512 bytes (256 words)
- **Addressing**: Byte-addressed, word-aligned
- **Endianness**: Big Endian

## Pipeline

### Stages
1. **IF** (Instruction Fetch): Fetch instruction from memory
2. **ID** (Instruction Decode): Decode and read registers
3. **EX** (Execute): ALU operations
4. **MEM** (Memory Access): Load/Store operations
5. **WB** (Write Back): Write result to register

### Hazard Handling
- **Data Forwarding**: EX→EX and MEM→EX paths
- **Load-Use Stall**: 1 cycle stall for load-use hazards
- **Branch Flush**: Flush IF and ID on branch taken
