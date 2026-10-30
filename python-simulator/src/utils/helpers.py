"""
RISC-16 Helper Functions
Bit manipülasyonu ve yardımcı fonksiyonlar
"""

from .constants import *


def get_bits(value: int, start: int, length: int) -> int:
    """
    Bir değerden belirli bitleri çıkarır
    
    Args:
        value: Kaynak değer
        start: Başlangıç bit pozisyonu (LSB'den)
        length: Çıkarılacak bit sayısı
    
    Returns:
        Çıkarılan bitler (sağa kaydırılmış)
    
    Example:
        get_bits(0b11010110, 2, 3) -> 0b101 (bit 4-2)
    """
    mask = (1 << length) - 1
    return (value >> start) & mask


def set_bits(value: int, data: int, start: int, length: int) -> int:
    """
    Bir değerin belirli bitlerini ayarlar
    
    Args:
        value: Hedef değer
        data: Yazılacak veri
        start: Başlangıç bit pozisyonu
        length: Bit sayısı
    
    Returns:
        Güncellenmiş değer
    """
    mask = ((1 << length) - 1) << start
    return (value & ~mask) | ((data << start) & mask)


def sign_extend(value: int, bits: int) -> int:
    """
    Signed değeri genişletir (sign extension)
    
    Args:
        value: Genişletilecek değer
        bits: Orijinal bit sayısı
    
    Returns:
        16-bit'e sign-extended değer
    
    Example:
        sign_extend(0b111010, 6) -> 0xFFFA (negatif değer)
    """
    sign_bit = 1 << (bits - 1)
    if value & sign_bit:
        # Negatif sayı - üst bitleri 1 yap
        return value | (~((1 << bits) - 1) & 0xFFFF)
    return value & 0xFFFF


def to_signed_16(value: int) -> int:
    """
    16-bit unsigned değeri signed'a çevirir
    
    Args:
        value: Unsigned 16-bit değer
    
    Returns:
        Signed değer (-32768 ile 32767 arası)
    """
    if value & 0x8000:
        return value - 0x10000
    return value


def to_unsigned_16(value: int) -> int:
    """
    Signed değeri 16-bit unsigned'a çevirir
    
    Args:
        value: Signed değer
    
    Returns:
        Unsigned 16-bit değer (0 ile 65535 arası)
    """
    return value & 0xFFFF


def decode_instruction(instruction: int) -> dict:
    """
    16-bit instruction'ı decode eder
    
    Args:
        instruction: 16-bit machine code
    
    Returns:
        Dictionary with decoded fields
    """
    opcode = get_bits(instruction, OPCODE_POS, OPCODE_BITS)
    rs = get_bits(instruction, RS_POS, RS_BITS)
    rt = get_bits(instruction, RT_POS, RT_BITS)
    rd = get_bits(instruction, RD_POS, RD_BITS)
    func = get_bits(instruction, FUNC_POS, FUNC_BITS)
    imm = get_bits(instruction, IMM_POS, IMM_BITS)
    addr = get_bits(instruction, ADDR_POS, ADDR_BITS)
    
    # Immediate sign extension
    imm_signed = sign_extend(imm, IMM_BITS)
    
    return {
        'opcode': opcode,
        'rs': rs,
        'rt': rt,
        'rd': rd,
        'func': func,
        'shamt': rd,  # Shift için rd alanı shamt olarak kullanılır
        'imm': imm,
        'imm_signed': to_signed_16(imm_signed),
        'addr': addr,
        'raw': instruction
    }


def encode_r_type(opcode: int, rs: int, rt: int, rd: int, func: int) -> int:
    """
    R-Type instruction encode eder
    
    Format: [opcode:4][rs:3][rt:3][rd:3][func:3]
    
    Returns:
        16-bit machine code
    """
    instruction = 0
    instruction = set_bits(instruction, opcode, OPCODE_POS, OPCODE_BITS)
    instruction = set_bits(instruction, rs, RS_POS, RS_BITS)
    instruction = set_bits(instruction, rt, RT_POS, RT_BITS)
    instruction = set_bits(instruction, rd, RD_POS, RD_BITS)
    instruction = set_bits(instruction, func, FUNC_POS, FUNC_BITS)
    return instruction


def encode_i_type(opcode: int, rs: int, rt: int, imm: int) -> int:
    """
    I-Type instruction encode eder
    
    Format: [opcode:4][rs:3][rt:3][imm:6]
    
    Returns:
        16-bit machine code
    """
    instruction = 0
    instruction = set_bits(instruction, opcode, OPCODE_POS, OPCODE_BITS)
    instruction = set_bits(instruction, rs, RS_POS, RS_BITS)
    instruction = set_bits(instruction, rt, RT_POS, RT_BITS)
    instruction = set_bits(instruction, imm & 0x3F, IMM_POS, IMM_BITS)
    return instruction


def encode_j_type(opcode: int, addr: int) -> int:
    """
    J-Type instruction encode eder
    
    Format: [opcode:4][address:12]
    
    Returns:
        16-bit machine code
    """
    instruction = 0
    instruction = set_bits(instruction, opcode, OPCODE_POS, OPCODE_BITS)
    instruction = set_bits(instruction, addr & 0xFFF, ADDR_POS, ADDR_BITS)
    return instruction


def format_binary(value: int, bits: int = 16) -> str:
    """
    Değeri binary string olarak formatlar
    
    Args:
        value: Formatlanacak değer
        bits: Bit sayısı
    
    Returns:
        Binary string (örn: "0000_0001_0010_0011")
    """
    binary = format(value & ((1 << bits) - 1), f'0{bits}b')
    # 4'erli grupla
    return '_'.join([binary[i:i+4] for i in range(0, len(binary), 4)])


def format_hex(value: int, bits: int = 16) -> str:
    """
    Değeri hex string olarak formatlar
    
    Args:
        value: Formatlanacak değer
        bits: Bit sayısı
    
    Returns:
        Hex string (örn: "0x0123")
    """
    hex_digits = bits // 4
    return f"0x{value & ((1 << bits) - 1):0{hex_digits}X}"


def get_instruction_type(opcode: int) -> str:
    """
    Opcode'a göre instruction tipini döndürür
    
    Returns:
        "R", "I", veya "J"
    """
    if opcode == Opcode.R_TYPE:
        return "R"
    elif opcode in [Opcode.J, Opcode.JAL]:
        return "J"
    else:
        return "I"


def get_instruction_name(opcode: int, func: int = None) -> str:
    """
    Instruction ismini döndürür
    
    Args:
        opcode: Opcode değeri
        func: Function code (R-Type için)
    
    Returns:
        Instruction ismi (örn: "ADD", "LW")
    """
    if opcode == Opcode.R_TYPE:
        return INSTRUCTION_NAMES.get((opcode, func), "UNKNOWN")
    else:
        return INSTRUCTION_NAMES.get((opcode, None), "UNKNOWN")


def disassemble(instruction: int) -> str:
    """
    Machine code'u assembly string'e çevirir
    
    Args:
        instruction: 16-bit machine code
    
    Returns:
        Assembly string (örn: "ADD R1, R2, R3")
    """
    if instruction == 0:
        return "NOP"
    
    decoded = decode_instruction(instruction)
    opcode = decoded['opcode']
    
    if opcode == Opcode.R_TYPE:
        name = get_instruction_name(opcode, decoded['func'])
        if decoded['func'] in [FuncCode.SLL, FuncCode.SRL]:
            # Shift instructions
            return f"{name} R{decoded['rd']}, R{decoded['rt']}, {decoded['shamt']}"
        else:
            return f"{name} R{decoded['rd']}, R{decoded['rs']}, R{decoded['rt']}"
    
    elif opcode == Opcode.JR:
        return f"JR R{decoded['rs']}"
    
    elif opcode in [Opcode.J, Opcode.JAL]:
        name = get_instruction_name(opcode)
        return f"{name} {format_hex(decoded['addr'], 12)}"
    
    elif opcode in [Opcode.LW, Opcode.SW]:
        name = get_instruction_name(opcode)
        return f"{name} R{decoded['rt']}, {decoded['imm_signed']}(R{decoded['rs']})"
    
    elif opcode in [Opcode.BEQ, Opcode.BNE]:
        name = get_instruction_name(opcode)
        return f"{name} R{decoded['rs']}, R{decoded['rt']}, {decoded['imm_signed']}"
    
    elif opcode == Opcode.ADDI:
        return f"ADDI R{decoded['rt']}, R{decoded['rs']}, {decoded['imm_signed']}"
    
    else:
        return f"UNKNOWN ({format_hex(instruction)})"


def parse_register(reg_str: str) -> int:
    """
    Register string'ini numaraya çevirir
    
    Args:
        reg_str: Register string (örn: "R1", "r2", "ra")
    
    Returns:
        Register numarası (0-7)
    
    Raises:
        ValueError: Geçersiz register
    """
    reg_str = reg_str.lower().strip()
    
    if reg_str in REGISTER_ALIASES:
        return REGISTER_ALIASES[reg_str]
    
    raise ValueError(f"Invalid register: {reg_str}")
