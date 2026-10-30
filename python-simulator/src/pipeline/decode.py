"""
RISC-16 Instruction Decode Stage (ID)
Instruction decode ve register okuma
"""

from ..utils.constants import Opcode
from ..utils.helpers import decode_instruction, get_instruction_name
from ..core.control_unit import ControlUnit, ControlSignals


class InstructionDecode:
    """
    Instruction Decode (ID) Stage
    
    Görevler:
    - Instruction decode
    - Register file okuma
    - Kontrol sinyalleri üretme
    - Immediate sign extension
    """
    
    def __init__(self, register_file, control_unit):
        """
        ID stage başlat
        
        Args:
            register_file: RegisterFile objesi
            control_unit: ControlUnit objesi
        """
        self.reg_file = register_file
        self.control = control_unit
        self._history = []
    
    def decode(self, instruction: int, pc: int) -> dict:
        """
        Instruction'ı decode et
        
        Args:
            instruction: 16-bit instruction
            pc: Instruction'ın PC değeri (branch hesabı için)
        
        Returns:
            Decoded instruction bilgileri ve kontrol sinyalleri
        """
        # Instruction alanlarını çıkar
        decoded = decode_instruction(instruction)
        
        # Kontrol sinyalleri üret
        signals = self.control.generate_signals(
            decoded['opcode'],
            decoded['func']
        )
        
        # Register değerlerini oku
        rs_value = self.reg_file.read(decoded['rs'])
        rt_value = self.reg_file.read(decoded['rt'])
        
        # Sonuç
        result = {
            # Instruction alanları
            'opcode': decoded['opcode'],
            'rs': decoded['rs'],
            'rt': decoded['rt'],
            'rd': decoded['rd'],
            'func': decoded['func'],
            'shamt': decoded['shamt'],
            'imm': decoded['imm_signed'],  # Sign-extended
            'addr': decoded['addr'],
            'instruction': instruction,
            
            # Register değerleri
            'rs_value': rs_value,
            'rt_value': rt_value,
            
            # PC
            'pc': pc,
            
            # Kontrol sinyalleri
            'signals': signals,
            
            # Debug
            'name': get_instruction_name(decoded['opcode'], decoded['func'])
        }
        
        # Geçmişe kaydet
        self._history.append(result.copy())
        
        return result
    
    def get_read_registers(self, instruction: int) -> tuple:
        """
        Instruction'ın okuduğu register'ları döndür
        
        Args:
            instruction: 16-bit instruction
        
        Returns:
            (rs, rt) tuple - kullanılmayan register için None
        """
        decoded = decode_instruction(instruction)
        opcode = decoded['opcode']
        
        rs = decoded['rs']
        rt = decoded['rt']
        
        # J-Type instructions sadece addr kullanır
        if opcode in [Opcode.J, Opcode.JAL]:
            return (None, None)
        
        # JR sadece rs kullanır
        if opcode == Opcode.JR:
            return (rs, None)
        
        # SW ve Branch: rs ve rt'yi oku
        if opcode in [Opcode.SW, Opcode.BEQ, Opcode.BNE]:
            return (rs, rt)
        
        # LW ve ADDI: sadece rs
        if opcode in [Opcode.LW, Opcode.ADDI]:
            return (rs, None)
        
        # R-Type: rs ve rt
        if opcode == Opcode.R_TYPE:
            return (rs, rt)
        
        return (rs, rt)
    
    def get_write_register(self, instruction: int) -> int:
        """
        Instruction'ın yazdığı register'ı döndür
        
        Args:
            instruction: 16-bit instruction
        
        Returns:
            Write register numarası veya None
        """
        decoded = decode_instruction(instruction)
        opcode = decoded['opcode']
        
        # Register'a yazmayan instruction'lar
        if opcode in [Opcode.SW, Opcode.BEQ, Opcode.BNE, Opcode.J, Opcode.JR]:
            return None
        
        # JAL: R7'ye (ra) yazar
        if opcode == Opcode.JAL:
            return 7
        
        # R-Type: rd'ye yazar
        if opcode == Opcode.R_TYPE:
            return decoded['rd']
        
        # I-Type (ADDI, LW): rt'ye yazar
        return decoded['rt']
    
    def is_branch_instruction(self, instruction: int) -> bool:
        """Branch instruction mı?"""
        decoded = decode_instruction(instruction)
        return decoded['opcode'] in [Opcode.BEQ, Opcode.BNE]
    
    def is_jump_instruction(self, instruction: int) -> bool:
        """Jump instruction mı?"""
        decoded = decode_instruction(instruction)
        return decoded['opcode'] in [Opcode.J, Opcode.JAL, Opcode.JR]
    
    def is_load_instruction(self, instruction: int) -> bool:
        """Load instruction mı?"""
        decoded = decode_instruction(instruction)
        return decoded['opcode'] == Opcode.LW
    
    def is_store_instruction(self, instruction: int) -> bool:
        """Store instruction mı?"""
        decoded = decode_instruction(instruction)
        return decoded['opcode'] == Opcode.SW
    
    def reset(self):
        """ID stage'i sıfırla"""
        self._history.clear()
    
    def get_history(self) -> list:
        """Decode geçmişini döndür"""
        return self._history.copy()
    
    def clear_history(self):
        """Geçmişi temizle"""
        self._history.clear()
    
    def __str__(self) -> str:
        if self._history:
            last = self._history[-1]
            return f"ID Stage: {last['name']} rs=R{last['rs']} rt=R{last['rt']} rd=R{last['rd']}"
        return "ID Stage: Empty"
