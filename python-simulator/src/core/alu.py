"""
RISC-16 Arithmetic Logic Unit (ALU)
16-bit aritmetik ve lojik işlemler
"""

from ..utils.constants import ALUOp
from ..utils.helpers import to_unsigned_16, to_signed_16


class ALU:
    """
    16-bit Arithmetic Logic Unit
    
    Desteklenen operasyonlar:
    - ADD: Toplama
    - SUB: Çıkarma
    - AND: Lojik AND
    - OR:  Lojik OR
    - SLT: Set if Less Than (signed)
    - SLL: Shift Left Logical
    - SRL: Shift Right Logical
    - PASS_B: B girişini geçir
    """
    
    def __init__(self):
        """ALU başlat"""
        self._last_result = 0
        self._last_zero_flag = False
        self._last_operation = None
        self._operation_history = []
    
    def execute(self, op: int, a: int, b: int, shamt: int = 0) -> tuple:
        """
        ALU operasyonu gerçekleştir
        
        Args:
            op: ALU operasyon kodu (ALUOp enum)
            a: Birinci operand (16-bit)
            b: İkinci operand (16-bit)
            shamt: Shift amount (shift işlemleri için)
        
        Returns:
            (result, zero_flag) tuple
            - result: 16-bit sonuç
            - zero_flag: Sonuç sıfır mı?
        """
        # Operand'ları 16-bit'e mask'le
        a = to_unsigned_16(a)
        b = to_unsigned_16(b)
        
        # Operasyonu gerçekleştir
        if op == ALUOp.ADD:
            result = a + b
        
        elif op == ALUOp.SUB:
            result = a - b
        
        elif op == ALUOp.AND:
            result = a & b
        
        elif op == ALUOp.OR:
            result = a | b
        
        elif op == ALUOp.SLT:
            # Signed karşılaştırma
            signed_a = to_signed_16(a)
            signed_b = to_signed_16(b)
            result = 1 if signed_a < signed_b else 0
        
        elif op == ALUOp.SLL:
            # Shift Left Logical
            result = b << shamt
        
        elif op == ALUOp.SRL:
            # Shift Right Logical
            result = b >> shamt
        
        elif op == ALUOp.PASS_B:
            # B'yi geçir (LW/SW adres hesabı için)
            result = b
        
        else:
            # Bilinmeyen operasyon - varsayılan olarak 0
            result = 0
        
        # 16-bit'e mask'le
        result = to_unsigned_16(result)
        
        # Zero flag
        zero_flag = (result == 0)
        
        # Sonuçları sakla
        self._last_result = result
        self._last_zero_flag = zero_flag
        self._last_operation = op
        
        # Geçmişe ekle
        self._operation_history.append({
            'operation': self._get_op_name(op),
            'a': a,
            'b': b,
            'shamt': shamt,
            'result': result,
            'zero': zero_flag
        })
        
        return result, zero_flag
    
    def add(self, a: int, b: int) -> int:
        """Toplama işlemi"""
        result, _ = self.execute(ALUOp.ADD, a, b)
        return result
    
    def sub(self, a: int, b: int) -> int:
        """Çıkarma işlemi"""
        result, _ = self.execute(ALUOp.SUB, a, b)
        return result
    
    def and_op(self, a: int, b: int) -> int:
        """AND işlemi"""
        result, _ = self.execute(ALUOp.AND, a, b)
        return result
    
    def or_op(self, a: int, b: int) -> int:
        """OR işlemi"""
        result, _ = self.execute(ALUOp.OR, a, b)
        return result
    
    def slt(self, a: int, b: int) -> int:
        """Set if Less Than (signed)"""
        result, _ = self.execute(ALUOp.SLT, a, b)
        return result
    
    def sll(self, b: int, shamt: int) -> int:
        """Shift Left Logical"""
        result, _ = self.execute(ALUOp.SLL, 0, b, shamt)
        return result
    
    def srl(self, b: int, shamt: int) -> int:
        """Shift Right Logical"""
        result, _ = self.execute(ALUOp.SRL, 0, b, shamt)
        return result
    
    def compare_equal(self, a: int, b: int) -> bool:
        """İki değeri karşılaştır (BEQ/BNE için)"""
        _, zero = self.execute(ALUOp.SUB, a, b)
        return zero
    
    def _get_op_name(self, op: int) -> str:
        """Operasyon ismini döndür"""
        op_names = {
            ALUOp.ADD: "ADD",
            ALUOp.SUB: "SUB",
            ALUOp.AND: "AND",
            ALUOp.OR: "OR",
            ALUOp.SLT: "SLT",
            ALUOp.SLL: "SLL",
            ALUOp.SRL: "SRL",
            ALUOp.PASS_B: "PASS_B"
        }
        return op_names.get(op, "UNKNOWN")
    
    @property
    def last_result(self) -> int:
        """Son sonucu döndür"""
        return self._last_result
    
    @property
    def last_zero_flag(self) -> bool:
        """Son zero flag'i döndür"""
        return self._last_zero_flag
    
    def get_operation_history(self) -> list:
        """Operasyon geçmişini döndür"""
        return self._operation_history.copy()
    
    def clear_history(self) -> None:
        """Geçmişi temizle"""
        self._operation_history.clear()
    
    def reset(self) -> None:
        """ALU'yu sıfırla"""
        self._last_result = 0
        self._last_zero_flag = False
        self._last_operation = None
        self._operation_history.clear()
    
    def __str__(self) -> str:
        """ALU durumunu string olarak döndür"""
        return (
            f"ALU State:\n"
            f"  Last Result: 0x{self._last_result:04X} ({self._last_result})\n"
            f"  Zero Flag: {self._last_zero_flag}\n"
            f"  Last Operation: {self._get_op_name(self._last_operation) if self._last_operation is not None else 'None'}"
        )


class ALUControl:
    """
    ALU Control Unit
    Opcode ve function code'dan ALU operasyonunu belirler
    """
    
    @staticmethod
    def get_alu_op(opcode: int, func: int, alu_op_signal: int) -> int:
        """
        Control sinyallerine göre ALU operasyonunu belirle
        
        Args:
            opcode: Instruction opcode
            func: Function code (R-Type için)
            alu_op_signal: Control unit'ten gelen ALUOp sinyali
        
        Returns:
            ALUOp değeri
        """
        from ..utils.constants import Opcode, FuncCode
        
        # R-Type instructions
        if opcode == Opcode.R_TYPE:
            func_to_alu = {
                FuncCode.ADD: ALUOp.ADD,
                FuncCode.SUB: ALUOp.SUB,
                FuncCode.AND: ALUOp.AND,
                FuncCode.OR:  ALUOp.OR,
                FuncCode.SLT: ALUOp.SLT,
                FuncCode.SLL: ALUOp.SLL,
                FuncCode.SRL: ALUOp.SRL,
            }
            return func_to_alu.get(func, ALUOp.ADD)
        
        # I-Type: ADDI, LW, SW -> ADD kullan (adres hesabı için)
        elif opcode in [Opcode.ADDI, Opcode.LW, Opcode.SW]:
            return ALUOp.ADD
        
        # Branch: BEQ, BNE -> SUB kullan (karşılaştırma için)
        elif opcode in [Opcode.BEQ, Opcode.BNE]:
            return ALUOp.SUB
        
        # Varsayılan
        return ALUOp.ADD
