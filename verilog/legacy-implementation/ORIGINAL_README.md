# RISC-16 Processor - Verilog Implementation

16-bit RISC işlemci Verilog implementasyonu. 5 aşamalı pipeline, hazard detection ve data forwarding destekli.

## 📁 Dosya Yapısı

```
risc16-verilog/
├── src/
│   ├── risc16_cpu.v         # Top module
│   ├── pc.v                 # Program Counter
│   ├── memory.v             # Instruction & Data Memory
│   ├── register_file.v      # Register File (R0-R7)
│   ├── alu.v                # ALU ve ALU Control
│   ├── control_unit.v       # Control Unit
│   ├── pipeline_registers.v # Pipeline Registers (IF/ID, ID/EX, EX/MEM, MEM/WB)
│   ├── hazard_forwarding.v  # Hazard Detection & Forwarding Unit
│   └── utils.v              # Utility modules (MUX, Sign Extend)
├── testbench/
│   └── risc16_tb.v          # Testbench
└── Makefile
```

## 🏗️ Mimari

### Pipeline Stages
1. **IF** - Instruction Fetch
2. **ID** - Instruction Decode
3. **EX** - Execute
4. **MEM** - Memory Access
5. **WB** - Write Back

### Register Set
| Register | Number | Usage |
|----------|--------|-------|
| R0 | 0 | Hardwired Zero |
| R1-R5 | 1-5 | General Purpose |
| R6 | 6 | Stack Pointer (sp) |
| R7 | 7 | Return Address (ra) |

## 📋 Instruction Set

### R-Type (Opcode: 0000)
| Instruction | Funct | Operation |
|-------------|-------|-----------|
| ADD | 000 | rd = rs + rt |
| SUB | 001 | rd = rs - rt |
| AND | 010 | rd = rs & rt |
| OR | 011 | rd = rs \| rt |
| SLT | 100 | rd = (rs < rt) ? 1 : 0 |
| SLL | 101 | rd = rt << shamt |
| SRL | 110 | rd = rt >> shamt |

### I-Type
| Instruction | Opcode | Operation |
|-------------|--------|-----------|
| ADDI | 0001 | rt = rs + imm |
| LW | 0010 | rt = MEM[rs + offset] |
| SW | 0011 | MEM[rs + offset] = rt |
| BEQ | 0100 | if (rs == rt) PC += offset |
| BNE | 0101 | if (rs != rt) PC += offset |

### J-Type
| Instruction | Opcode | Operation |
|-------------|--------|-----------|
| J | 0110 | PC = address |
| JAL | 0111 | R7 = PC+2; PC = address |
| JR | 1000 | PC = rs |

## ⚠️ Hazard Handling

| Hazard Type | Detection | Solution |
|-------------|-----------|----------|
| RAW Data Hazard | EX/MEM.Rd = ID/EX.Rs | Forwarding |
| Load-Use Hazard | LW followed by dependent | 1-cycle Stall |
| Control Hazard | Branch/Jump | Flush |

## 🚀 Kullanım

### Derleme ve Simülasyon (Icarus Verilog)
```bash
make simulate
```

### Waveform Görüntüleme (GTKWave)
```bash
make wave
```

### Temizleme
```bash
make clean
```

## 📊 Test Programı

Varsayılan test programı 1'den 5'e kadar toplam hesaplar:

```assembly
addi r1, r0, 5      # r1 = 5 (counter)
addi r2, r0, 0      # r2 = 0 (sum)
loop:
    add r2, r2, r1  # sum += counter
    addi r1, r1, -1 # counter--
    bne r1, r0, loop
halt
# Sonuç: R2 = 15
```

## 📌 FPGA Synthesis

Vivado veya Quartus ile synthesize edilebilir:

1. Tüm `.v` dosyalarını projeye ekleyin
2. `risc16_cpu` modülünü top module olarak seçin
3. Clock ve reset pinlerini bağlayın
4. Synthesis ve implementation yapın

## 📝 License

Computer Architecture Course Project
