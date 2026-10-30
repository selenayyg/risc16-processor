"""
RISC-16 Execute Stage (EX)
ALU operasyonları ve adres hesabı
"""

from ..utils.constants import BYTES_PER_WORD, ALUOp, Opcode
from ..utils.helpers import to_unsigned_16
from ..core.alu import ALU, ALUControl


class Execute:
    """
    Execute (EX) Stage
    
    Görevler:
    - ALU operasyonları
    - Branch/Jump adres hesabı
    - Forwarded değerleri kullanma
    """
    
    def __init__(self, alu: ALU):
        """
        EX stage başlat
        
        Args:
            alu: ALU objesi
        """
        self.alu = alu
        self._history = []
    
    def execute(self, 
                rs_value: int, 
                rt_value: int,
                imm: int,
                shamt: int,
                pc: int,
                opcode: int,
                func: int,
                alu_src: int,
                alu_op: int,
                forwarded_rs: int = None,
                forwarded_rt: int = None) -> dict:
        """
        ALU operasyonunu gerçekleştir
        
        Args:
            rs_value: rs register değeri
            rt_value: rt register değeri
            imm: Sign-extended immediate
            shamt: Shift amount
            pc: Program counter (branch hesabı için)
            opcode: Instruction opcode
            func: Function code
            alu_src: ALU source select (0: register, 1: immediate)
            alu_op: ALU operation
            forwarded_rs: Forwarded rs değeri (None ise rs_value kullan)
            forwarded_rt: Forwarded rt değeri (None ise rt_value kullan)
        
        Returns:
            {
                'alu_result': ALU sonucu,
                'zero_flag': Zero flag,
                'branch_target': Branch hedef adresi
            }
        """
        # Forwarding uygula
        a = forwarded_rs if forwarded_rs is not None else rs_value
        b_reg = forwarded_rt if forwarded_rt is not None else rt_value
        
        # ALU B girişi seç
        if alu_src:
            b = imm  # Immediate
        else:
            b = b_reg  # Register
        
        # ALU operasyonunu belirle
        actual_alu_op = ALUControl.get_alu_op(opcode, func, alu_op)
        
        # ALU çalıştır
        if actual_alu_op in [ALUOp.SLL, ALUOp.SRL]:
            # Shift işlemleri için shamt kullan
            result, zero = self.alu.execute(actual_alu_op, a, b, shamt)
        else:
            result, zero = self.alu.execute(actual_alu_op, a, b)
        
        # Branch hedef adresi hesapla
        # Branch target = PC + 2 + (imm * 2)
        branch_target = to_unsigned_16(pc + (imm * BYTES_PER_WORD))
        
        # Sonuç
        exec_result = {
            'alu_result': result,
            'zero_flag': zero,
            'branch_target': branch_target,
            'alu_a': a,
            'alu_b': b,
            'alu_op': actual_alu_op
        }
        
        # Geçmişe kaydet
        self._history.append(exec_result.copy())
        
        return exec_result
    
    def calculate_branch_target(self, pc: int, offset: int) -> int:
        """
        Branch hedef adresini hesapla
        
        Args:
            pc: PC+2 (ID/EX register'daki)
            offset: Sign-extended offset
        
        Returns:
            Branch hedef adresi
        """
        target = pc + (offset * BYTES_PER_WORD)
        return to_unsigned_16(target)
    
    def calculate_jump_target(self, pc: int, addr: int) -> int:
        """
        Jump hedef adresini hesapla
        
        Args:
            pc: Current PC
            addr: 12-bit address
        
        Returns:
            Jump hedef adresi
        """
        # PC'nin üst 3 biti + 12-bit adres + 0 (word aligned)
        pc_upper = pc & 0xE000
        target = pc_upper | ((addr & 0xFFF) << 1)
        return to_unsigned_16(target)
    
    def calculate_jr_target(self, rs_value: int) -> int:
        """
        JR hedef adresini hesapla
        
        Args:
            rs_value: rs register değeri
        
        Returns:
            Jump hedef adresi
        """
        return to_unsigned_16(rs_value)
    
    def calculate_memory_address(self, base: int, offset: int) -> int:
        """
        Load/Store için memory adresini hesapla
        
        Args:
            base: Base register değeri
            offset: Sign-extended offset
        
        Returns:
            Memory adresi
        """
        return to_unsigned_16(base + offset)
    
    def reset(self):
        """EX stage'i sıfırla"""
        self.alu.reset()
        self._history.clear()
    
    def get_history(self) -> list:
        """Execute geçmişini döndür"""
        return self._history.copy()
    
    def clear_history(self):
        """Geçmişi temizle"""
        self._history.clear()
    
    def __str__(self) -> str:
        if self._history:
            last = self._history[-1]
            return f"EX Stage: Result=0x{last['alu_result']:04X}, Zero={last['zero_flag']}"
        return "EX Stage: Empty"
