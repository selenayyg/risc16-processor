"""
RISC-16 Processor Constants
16-bit RISC İşlemci için tüm sabitler
"""

# ============================================================
# PROCESSOR SPECIFICATIONS
# ============================================================
WORD_SIZE = 16                    # 16-bit data path
NUM_REGISTERS = 8                 # R0-R7
INSTRUCTION_MEMORY_SIZE = 512     # 512 Byte
DATA_MEMORY_SIZE = 512            # 512 Byte
BYTES_PER_WORD = 2                # 16-bit = 2 byte

# ============================================================
# INSTRUCTION FORMAT BIT FIELDS
# ============================================================
# R-Type: [opcode:4][rs:3][rt:3][rd:3][func:3] = 16 bit
# I-Type: [opcode:4][rs:3][rt:3][imm:6] = 16 bit
# J-Type: [opcode:4][address:12] = 16 bit

OPCODE_BITS = 4
RS_BITS = 3
RT_BITS = 3
RD_BITS = 3
FUNC_BITS = 3
IMM_BITS = 6
ADDR_BITS = 12
SHAMT_BITS = 3  # Shift amount (func alanında)

# Bit pozisyonları (MSB'den itibaren)
OPCODE_POS = 12    # bit 15-12
RS_POS = 9         # bit 11-9
RT_POS = 6         # bit 8-6
RD_POS = 3         # bit 5-3
FUNC_POS = 0       # bit 2-0
IMM_POS = 0        # bit 5-0
ADDR_POS = 0       # bit 11-0

# ============================================================
# OPCODES (4-bit)
# ============================================================
class Opcode:
    # R-Type instructions (opcode = 0000)
    R_TYPE = 0b0000
    
    # I-Type instructions
    ADDI = 0b0001
    LW   = 0b0010
    SW   = 0b0011
    BEQ  = 0b0100
    BNE  = 0b0101
    
    # J-Type instructions
    J    = 0b0110
    JAL  = 0b0111
    
    # Özel: JR için (R-Type formatında ama ayrı opcode)
    JR   = 0b1000
    
    # HALT instruction (special opcode)
    HALT = 0b1111

# ============================================================
# FUNCTION CODES (3-bit, R-Type için)
# ============================================================
class FuncCode:
    ADD = 0b000
    SUB = 0b001
    AND = 0b010
    OR  = 0b011
    SLT = 0b100
    SLL = 0b101
    SRL = 0b110

# ============================================================
# ALU OPERATIONS
# ============================================================
class ALUOp:
    ADD = 0
    SUB = 1
    AND = 2
    OR  = 3
    SLT = 4      # Set Less Than
    SLL = 5      # Shift Left Logical
    SRL = 6      # Shift Right Logical
    PASS_B = 7   # B'yi geçir (LW/SW için)

# ============================================================
# CONTROL SIGNALS
# ============================================================
class ControlSignals:
    """Her instruction için kontrol sinyalleri"""
    
    # Signal indices
    REG_DST = 0      # 0: rt, 1: rd hedef register
    ALU_SRC = 1      # 0: register, 1: immediate
    MEM_TO_REG = 2   # 0: ALU result, 1: memory data
    REG_WRITE = 3    # 1: register'a yaz
    MEM_READ = 4     # 1: memory'den oku
    MEM_WRITE = 5    # 1: memory'ye yaz
    BRANCH = 6       # 1: branch instruction
    JUMP = 7         # 1: jump instruction
    ALU_OP = 8       # ALU operasyonu (2-bit)
    LINK = 9         # 1: JAL için return address kaydet

# ============================================================
# INSTRUCTION NAMES (Debug için)
# ============================================================
INSTRUCTION_NAMES = {
    # R-Type
    (Opcode.R_TYPE, FuncCode.ADD): "ADD",
    (Opcode.R_TYPE, FuncCode.SUB): "SUB",
    (Opcode.R_TYPE, FuncCode.AND): "AND",
    (Opcode.R_TYPE, FuncCode.OR):  "OR",
    (Opcode.R_TYPE, FuncCode.SLT): "SLT",
    (Opcode.R_TYPE, FuncCode.SLL): "SLL",
    (Opcode.R_TYPE, FuncCode.SRL): "SRL",
    
    # I-Type
    (Opcode.ADDI, None): "ADDI",
    (Opcode.LW, None):   "LW",
    (Opcode.SW, None):   "SW",
    (Opcode.BEQ, None):  "BEQ",
    (Opcode.BNE, None):  "BNE",
    
    # J-Type
    (Opcode.J, None):    "J",
    (Opcode.JAL, None):  "JAL",
    (Opcode.JR, None):   "JR",
}

# ============================================================
# REGISTER NAMES
# ============================================================
REGISTER_NAMES = {
    0: "R0",  # Zero register (her zaman 0) - opsiyonel
    1: "R1",
    2: "R2",
    3: "R3",
    4: "R4",
    5: "R5",
    6: "R6",
    7: "R7",  # Return address için kullanılabilir
}

# Assembly'de alternatif isimler
REGISTER_ALIASES = {
    "zero": 0,
    "r0": 0,
    "r1": 1,
    "r2": 2,
    "r3": 3,
    "r4": 4,
    "r5": 5,
    "r6": 6,
    "r7": 7,
    "ra": 7,  # Return address
}

# ============================================================
# PIPELINE STAGES
# ============================================================
class PipelineStage:
    IF = "IF"    # Instruction Fetch
    ID = "ID"    # Instruction Decode
    EX = "EX"    # Execute
    MEM = "MEM"  # Memory Access
    WB = "WB"    # Write Back

PIPELINE_STAGES = [
    PipelineStage.IF,
    PipelineStage.ID,
    PipelineStage.EX,
    PipelineStage.MEM,
    PipelineStage.WB
]

# ============================================================
# HAZARD TYPES
# ============================================================
class HazardType:
    NONE = "NONE"
    RAW = "RAW"           # Read After Write (data hazard)
    LOAD_USE = "LOAD_USE" # Load-use hazard (stall gerektirir)
    CONTROL = "CONTROL"   # Control hazard (branch/jump)

# ============================================================
# FORWARDING SOURCES
# ============================================================
class ForwardingSource:
    NONE = 0      # Register file'dan
    EX_MEM = 1    # EX/MEM pipeline register'dan
    MEM_WB = 2    # MEM/WB pipeline register'dan

# ============================================================
# DEFAULT VALUES
# ============================================================
NOP_INSTRUCTION = 0x0000  # No operation (add r0, r0, r0)
PC_START = 0x0000         # Program counter başlangıç değeri
