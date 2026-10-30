# RISC-16 Verilog Implementation

16-bit RISC Processor with 5-Stage Pipeline - Computer Architecture Course 2024-2025

## Specifications

- **Instruction Width:** 16-bit
- **Registers:** 8 general-purpose (R0-R7), R0 hardwired to zero
- **Pipeline Stages:** IF → ID → EX → MEM → WB
- **Instruction Memory:** 512 Bytes (256 words)
- **Data Memory:** 512 Bytes (256 words)
- **Data Hazard Resolution:** Forwarding + Stall
- **Control Hazard Resolution:** Flush on branch taken

## Instruction Set

### R-Type Instructions
| Instruction | Format | Operation |
|-------------|--------|-----------|
| ADD | `add rd, rs, rt` | rd = rs + rt |
| SUB | `sub rd, rs, rt` | rd = rs - rt |
| AND | `and rd, rs, rt` | rd = rs & rt |
| OR | `or rd, rs, rt` | rd = rs \| rt |
| SLT | `slt rd, rs, rt` | rd = (rs < rt) ? 1 : 0 |
| SLL | `sll rd, rt, shamt` | rd = rt << shamt |
| SRL | `srl rd, rt, shamt` | rd = rt >> shamt |

### I-Type Instructions
| Instruction | Format | Operation |
|-------------|--------|-----------|
| ADDI | `addi rt, rs, imm` | rt = rs + imm |
| LW | `lw rt, offset(rs)` | rt = Mem[rs + offset] |
| SW | `sw rt, offset(rs)` | Mem[rs + offset] = rt |
| BEQ | `beq rs, rt, label` | if (rs == rt) PC = label |
| BNE | `bne rs, rt, label` | if (rs != rt) PC = label |

### J-Type Instructions
| Instruction | Format | Operation |
|-------------|--------|-----------|
| J | `j target` | PC = target |
| JAL | `jal target` | R7 = PC+2; PC = target |
| JR | `jr rs` | PC = rs |

### Special
| Instruction | Format | Operation |
|-------------|--------|-----------|
| HALT | `halt` | Stop execution |

## Instruction Encoding

```
R-Type: [opcode:4][rs:3][rt:3][rd:3][shamt/funct:3]
I-Type: [opcode:4][rs:3][rt:3][imm:6]
J-Type: [opcode:4][address:12]
```

### Opcode Table
| Opcode | Instruction |
|--------|-------------|
| 0000 | R-Type |
| 0001 | ADDI |
| 0010 | LW |
| 0011 | SW |
| 0100 | BEQ |
| 0101 | BNE |
| 0110 | J |
| 0111 | JAL |
| 1000 | JR |
| 1111 | HALT |

### R-Type Function Codes
| Funct | Operation |
|-------|-----------|
| 000 | ADD |
| 001 | SUB |
| 010 | AND |
| 011 | OR |
| 100 | SLT |
| 101 | SLL |
| 110 | SRL |

## File Structure

```
risc16-verilog/
├── risc16_cpu.v         # Top-level CPU module
├── program_counter.v    # Program Counter
├── instruction_memory.v # Instruction Memory (ROM)
├── data_memory.v        # Data Memory (RAM)
├── register_file.v      # Register File (8x16-bit)
├── alu.v                # Arithmetic Logic Unit
├── control_unit.v       # Control Signal Generator
├── pipeline_regs.v      # Pipeline Registers (IF/ID, ID/EX, EX/MEM, MEM/WB)
├── hazard_unit.v        # Hazard Detection + Forwarding Unit
├── risc16_tb.v          # Testbench
├── Makefile             # Build automation
└── README.md            # This file
```

## Simulation

### Using Icarus Verilog (Free, Open Source)

```bash
# Install (macOS)
brew install icarus-verilog

# Install (Ubuntu)
sudo apt install iverilog

# Compile and run
make

# Or manually:
iverilog -o risc16_sim risc16_tb.v risc16_cpu.v program_counter.v \
         instruction_memory.v data_memory.v register_file.v \
         alu.v control_unit.v pipeline_regs.v hazard_unit.v
vvp risc16_sim

# View waveforms (requires GTKWave)
make wave
```

### Using Vivado (Xilinx)

1. Create new project
2. Add all .v files as sources
3. Add risc16_tb.v as simulation source
4. Run behavioral simulation

## Test Program

The default test program calculates sum of 1 to 5:

```assembly
# Sum 1+2+3+4+5 = 15
    addi r1, r0, 5      # r1 = 5 (counter)
    addi r2, r0, 0      # r2 = 0 (sum)
loop:
    add  r2, r2, r1     # sum += counter
    addi r1, r1, -1     # counter--
    bne  r1, r0, loop   # if counter != 0, loop
    sw   r2, 0(r0)      # Mem[0] = sum
    halt
```

Expected result:
- R1 = 0
- R2 = 15
- Mem[0] = 15

## Pipeline Diagram

```
          ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
Instr 1:  │ IF  │──▶│ ID  │──▶│ EX  │──▶│ MEM │──▶│ WB  │
          └─────┘   └─────┘   └─────┘   └─────┘   └─────┘
                    ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
Instr 2:           │ IF  │──▶│ ID  │──▶│ EX  │──▶│ MEM │──▶...
                    └─────┘   └─────┘   └─────┘   └─────┘
                              ┌─────┐   ┌─────┐   ┌─────┐
Instr 3:                     │ IF  │──▶│ ID  │──▶│ EX  │──▶...
                              └─────┘   └─────┘   └─────┘
```

## Hazard Handling

### Data Hazards
- **Forwarding:** EX-EX and MEM-EX forwarding paths
- **Stall:** Load-use hazard causes 1-cycle stall

### Control Hazards
- **Flush:** On branch taken, IF/ID register is flushed
- **Predict Not Taken:** Default behavior

## Author

Computer Architecture Course - 2024-2025 Fall Semester
