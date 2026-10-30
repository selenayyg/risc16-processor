# RISC-16 Instruction Set Architecture Design Document

## 1. Overview

This document describes the Instruction Set Architecture (ISA) design for the 16-bit RISC processor implemented as part of the Computer Architecture course project.

## 2. General Specifications

| Parameter | Value |
|-----------|-------|
| Word Size | 16 bits |
| Instruction Width | 16 bits |
| Number of Registers | 8 (R0-R7) |
| Special Register | R0 = 0 (hardwired) |
| Instruction Memory | 512 Bytes |
| Data Memory | 512 Bytes |
| Addressing Mode | Byte-addressable |

## 3. Register Set

| Register | Name | Description |
|----------|------|-------------|
| R0 | zero | Always contains 0 |
| R1 | t0 | Temporary |
| R2 | t1 | Temporary |
| R3 | t2 | Temporary |
| R4 | t3 | Temporary |
| R5 | t4 | Temporary |
| R6 | sp | Stack Pointer |
| R7 | ra | Return Address |

## 4. Instruction Formats

### 4.1 R-Type Format (Register Operations)
```
15  14  13  12 | 11  10  9 | 8  7  6 | 5  4  3 | 2  1  0
   opcode      |    rs     |   rt    |   rd    |  funct
   (4 bits)    | (3 bits)  | (3 bits)| (3 bits)| (3 bits)
```

### 4.2 I-Type Format (Immediate Operations)
```
15  14  13  12 | 11  10  9 | 8  7  6 | 5  4  3  2  1  0
   opcode      |    rs     |   rt    |     immediate
   (4 bits)    | (3 bits)  | (3 bits)|     (6 bits)
```

### 4.3 J-Type Format (Jump Operations)
```
15  14  13  12 | 11  10  9  8  7  6  5  4  3  2  1  0
   opcode      |              address
   (4 bits)    |             (12 bits)
```

## 5. Opcode Assignment

| Opcode (Binary) | Opcode (Hex) | Instruction Type |
|-----------------|--------------|------------------|
| 0000 | 0x0 | R-Type |
| 0001 | 0x1 | ADDI |
| 0010 | 0x2 | LW |
| 0011 | 0x3 | SW |
| 0100 | 0x4 | BEQ |
| 0101 | 0x5 | BNE |
| 0110 | 0x6 | J |
| 0111 | 0x7 | JAL |
| 1000 | 0x8 | JR |
| 1111 | 0xF | HALT |

## 6. R-Type Function Codes

| Funct (Binary) | Funct (Dec) | Operation |
|----------------|-------------|-----------|
| 000 | 0 | ADD |
| 001 | 1 | SUB |
| 010 | 2 | AND |
| 011 | 3 | OR |
| 100 | 4 | SLT |
| 101 | 5 | SLL |
| 110 | 6 | SRL |

## 7. Instruction Descriptions

### 7.1 Arithmetic Instructions

#### ADD - Add
- **Format:** `add rd, rs, rt`
- **Encoding:** `0000_[rs]_[rt]_[rd]_000`
- **Operation:** `R[rd] = R[rs] + R[rt]`

#### SUB - Subtract
- **Format:** `sub rd, rs, rt`
- **Encoding:** `0000_[rs]_[rt]_[rd]_001`
- **Operation:** `R[rd] = R[rs] - R[rt]`

#### ADDI - Add Immediate
- **Format:** `addi rt, rs, imm`
- **Encoding:** `0001_[rs]_[rt]_[imm6]`
- **Operation:** `R[rt] = R[rs] + SignExt(imm6)`

### 7.2 Logical Instructions

#### AND - Bitwise AND
- **Format:** `and rd, rs, rt`
- **Encoding:** `0000_[rs]_[rt]_[rd]_010`
- **Operation:** `R[rd] = R[rs] & R[rt]`

#### OR - Bitwise OR
- **Format:** `or rd, rs, rt`
- **Encoding:** `0000_[rs]_[rt]_[rd]_011`
- **Operation:** `R[rd] = R[rs] | R[rt]`

### 7.3 Comparison Instructions

#### SLT - Set Less Than
- **Format:** `slt rd, rs, rt`
- **Encoding:** `0000_[rs]_[rt]_[rd]_100`
- **Operation:** `R[rd] = (R[rs] < R[rt]) ? 1 : 0`

### 7.4 Shift Instructions

#### SLL - Shift Left Logical
- **Format:** `sll rd, rt, shamt`
- **Encoding:** `0000_[shamt]_[rt]_[rd]_101`
- **Operation:** `R[rd] = R[rt] << shamt`

#### SRL - Shift Right Logical
- **Format:** `srl rd, rt, shamt`
- **Encoding:** `0000_[shamt]_[rt]_[rd]_110`
- **Operation:** `R[rd] = R[rt] >> shamt`

### 7.5 Memory Instructions

#### LW - Load Word
- **Format:** `lw rt, offset(rs)`
- **Encoding:** `0010_[rs]_[rt]_[offset6]`
- **Operation:** `R[rt] = Mem[R[rs] + SignExt(offset6)]`

#### SW - Store Word
- **Format:** `sw rt, offset(rs)`
- **Encoding:** `0011_[rs]_[rt]_[offset6]`
- **Operation:** `Mem[R[rs] + SignExt(offset6)] = R[rt]`

### 7.6 Branch Instructions

#### BEQ - Branch if Equal
- **Format:** `beq rs, rt, offset`
- **Encoding:** `0100_[rs]_[rt]_[offset6]`
- **Operation:** `if (R[rs] == R[rt]) PC = PC + 2 + SignExt(offset6) << 1`

#### BNE - Branch if Not Equal
- **Format:** `bne rs, rt, offset`
- **Encoding:** `0101_[rs]_[rt]_[offset6]`
- **Operation:** `if (R[rs] != R[rt]) PC = PC + 2 + SignExt(offset6) << 1`

### 7.7 Jump Instructions

#### J - Jump
- **Format:** `j target`
- **Encoding:** `0110_[addr12]`
- **Operation:** `PC = {PC[15:13], addr12, 1'b0}`

#### JAL - Jump and Link
- **Format:** `jal target`
- **Encoding:** `0111_[addr12]`
- **Operation:** `R[7] = PC + 2; PC = {PC[15:13], addr12, 1'b0}`

#### JR - Jump Register
- **Format:** `jr rs`
- **Encoding:** `1000_[rs]_000_000_000`
- **Operation:** `PC = R[rs]`

### 7.8 Special Instructions

#### HALT - Halt Execution
- **Format:** `halt`
- **Encoding:** `1111_000_000_000000`
- **Operation:** Stop processor execution

## 8. Pipeline Design

### 8.1 Pipeline Stages

1. **IF (Instruction Fetch):** Fetch instruction from memory
2. **ID (Instruction Decode):** Decode instruction and read registers
3. **EX (Execute):** Perform ALU operation
4. **MEM (Memory Access):** Access data memory
5. **WB (Write Back):** Write result to register file

### 8.2 Pipeline Registers

| Register | Contents |
|----------|----------|
| IF/ID | PC, Instruction |
| ID/EX | PC, Read Data 1&2, Immediate, Rs, Rt, Rd, Control Signals |
| EX/MEM | PC, ALU Result, Write Data, Write Reg, Control Signals |
| MEM/WB | ALU Result, Memory Data, Write Reg, Control Signals |

## 9. Hazard Handling

### 9.1 Data Hazards

**Forwarding Paths:**
- EX/MEM → EX: Forward ALU result to ALU input
- MEM/WB → EX: Forward WB result to ALU input

**Stall Conditions:**
- Load-Use Hazard: 1-cycle stall when LW result needed immediately

### 9.2 Control Hazards

**Branch Resolution:**
- Branch decision made in MEM stage
- On branch taken: Flush IF/ID and ID/EX registers

## 10. Control Signals

| Signal | Description |
|--------|-------------|
| RegWrite | Enable register write |
| MemToReg | Select memory data for WB |
| MemRead | Enable memory read |
| MemWrite | Enable memory write |
| ALUSrc | Select immediate as ALU input B |
| ALUOp | ALU operation selector |
| Branch | BEQ instruction |
| BranchNE | BNE instruction |
| Jump | J instruction |
| JAL | JAL instruction |
| JR | JR instruction |

## 11. Example Encoding

### Example 1: `add r2, r1, r3`
```
opcode = 0000 (R-type)
rs = 001 (R1)
rt = 011 (R3)
rd = 010 (R2)
funct = 000 (ADD)

Binary: 0000_001_011_010_000 = 0x02D0
```

### Example 2: `addi r1, r0, 5`
```
opcode = 0001 (ADDI)
rs = 000 (R0)
rt = 001 (R1)
imm = 000101 (5)

Binary: 0001_000_001_000101 = 0x1045
```

### Example 3: `sw r2, 0(r0)`
```
opcode = 0011 (SW)
rs = 000 (R0)
rt = 010 (R2)
offset = 000000 (0)

Binary: 0011_000_010_000000 = 0x3080
```

### Example 4: `bne r1, r0, -3`
```
opcode = 0101 (BNE)
rs = 001 (R1)
rt = 000 (R0)
offset = 111101 (-3 in 6-bit signed)

Binary: 0101_001_000_111101 = 0x523D
```
