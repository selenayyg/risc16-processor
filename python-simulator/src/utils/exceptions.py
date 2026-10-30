"""
RISC-16 Custom Exceptions
Simülatör için özel hata sınıfları
"""


class RISC16Error(Exception):
    """Tüm RISC-16 hataları için temel sınıf"""
    pass


# ============================================================
# MEMORY ERRORS
# ============================================================

class MemoryError(RISC16Error):
    """Memory ile ilgili hatalar"""
    pass


class MemoryAccessError(MemoryError):
    """Geçersiz memory erişimi"""
    def __init__(self, address: int, memory_type: str = "memory"):
        self.address = address
        self.memory_type = memory_type
        super().__init__(
            f"Invalid {memory_type} access at address 0x{address:04X}"
        )


class MemoryAlignmentError(MemoryError):
    """Hizalanmamış memory erişimi"""
    def __init__(self, address: int):
        self.address = address
        super().__init__(
            f"Unaligned memory access at address 0x{address:04X}. "
            f"Address must be word-aligned (multiple of 2)."
        )


# ============================================================
# REGISTER ERRORS
# ============================================================

class RegisterError(RISC16Error):
    """Register ile ilgili hatalar"""
    pass


class InvalidRegisterError(RegisterError):
    """Geçersiz register numarası"""
    def __init__(self, register: int):
        self.register = register
        super().__init__(
            f"Invalid register number: {register}. "
            f"Valid registers are R0-R7 (0-7)."
        )


# ============================================================
# INSTRUCTION ERRORS
# ============================================================

class InstructionError(RISC16Error):
    """Instruction ile ilgili hatalar"""
    pass


class InvalidOpcodeError(InstructionError):
    """Geçersiz opcode"""
    def __init__(self, opcode: int):
        self.opcode = opcode
        super().__init__(
            f"Invalid opcode: 0b{opcode:04b} ({opcode})"
        )


class InvalidFunctionCodeError(InstructionError):
    """Geçersiz function code"""
    def __init__(self, func: int):
        self.func = func
        super().__init__(
            f"Invalid function code: 0b{func:03b} ({func})"
        )


class InvalidInstructionError(InstructionError):
    """Geçersiz instruction"""
    def __init__(self, instruction: int, reason: str = ""):
        self.instruction = instruction
        self.reason = reason
        msg = f"Invalid instruction: 0x{instruction:04X}"
        if reason:
            msg += f" - {reason}"
        super().__init__(msg)


# ============================================================
# ASSEMBLER ERRORS
# ============================================================

class AssemblerError(RISC16Error):
    """Assembler ile ilgili hatalar"""
    pass


class SyntaxError(AssemblerError):
    """Assembly syntax hatası"""
    def __init__(self, line_num: int, line: str, message: str):
        self.line_num = line_num
        self.line = line
        self.message = message
        super().__init__(
            f"Syntax error at line {line_num}: {message}\n"
            f"  -> {line}"
        )


class UndefinedLabelError(AssemblerError):
    """Tanımlanmamış label"""
    def __init__(self, label: str, line_num: int = None):
        self.label = label
        self.line_num = line_num
        msg = f"Undefined label: '{label}'"
        if line_num:
            msg += f" at line {line_num}"
        super().__init__(msg)


class DuplicateLabelError(AssemblerError):
    """Tekrarlanan label tanımı"""
    def __init__(self, label: str, line_num: int):
        self.label = label
        self.line_num = line_num
        super().__init__(
            f"Duplicate label definition: '{label}' at line {line_num}"
        )


class ImmediateOverflowError(AssemblerError):
    """Immediate değer taşması"""
    def __init__(self, value: int, bits: int, line_num: int = None):
        self.value = value
        self.bits = bits
        self.line_num = line_num
        max_val = (1 << (bits - 1)) - 1
        min_val = -(1 << (bits - 1))
        msg = f"Immediate value {value} out of range [{min_val}, {max_val}] ({bits}-bit signed)"
        if line_num:
            msg = f"Line {line_num}: " + msg
        super().__init__(msg)


class AddressOverflowError(AssemblerError):
    """Address değer taşması"""
    def __init__(self, value: int, bits: int, line_num: int = None):
        self.value = value
        self.bits = bits
        self.line_num = line_num
        max_val = (1 << bits) - 1
        msg = f"Address value {value} out of range [0, {max_val}] ({bits}-bit)"
        if line_num:
            msg = f"Line {line_num}: " + msg
        super().__init__(msg)


# ============================================================
# PIPELINE ERRORS
# ============================================================

class PipelineError(RISC16Error):
    """Pipeline ile ilgili hatalar"""
    pass


class HazardError(PipelineError):
    """Çözülemeyen hazard durumu"""
    def __init__(self, hazard_type: str, details: str = ""):
        self.hazard_type = hazard_type
        self.details = details
        msg = f"Unresolved {hazard_type} hazard"
        if details:
            msg += f": {details}"
        super().__init__(msg)


# ============================================================
# SIMULATION ERRORS
# ============================================================

class SimulationError(RISC16Error):
    """Simülasyon ile ilgili hatalar"""
    pass


class ProgramNotLoadedError(SimulationError):
    """Program yüklenmemiş"""
    def __init__(self):
        super().__init__("No program loaded. Please load a program first.")


class SimulationEndedError(SimulationError):
    """Simülasyon tamamlandı"""
    def __init__(self, reason: str = "Program completed"):
        self.reason = reason
        super().__init__(f"Simulation ended: {reason}")


class InfiniteLoopError(SimulationError):
    """Sonsuz döngü tespit edildi"""
    def __init__(self, max_cycles: int):
        self.max_cycles = max_cycles
        super().__init__(
            f"Possible infinite loop detected after {max_cycles} cycles"
        )
