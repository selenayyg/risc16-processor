"""
RISC-16 Instruction Fetch Stage (IF)
Program Counter yönetimi ve instruction fetch
"""

from ..utils.constants import BYTES_PER_WORD, PC_START, NOP_INSTRUCTION
from ..utils.helpers import to_unsigned_16


class InstructionFetch:
    """
    Instruction Fetch (IF) Stage
    
    Görevler:
    - Program Counter yönetimi
    - Instruction Memory'den instruction fetch
    - Branch/Jump adres hesabı
    """
    
    def __init__(self, instruction_memory):
        """
        IF stage başlat
        
        Args:
            instruction_memory: InstructionMemory objesi
        """
        self.imem = instruction_memory
        self.pc = PC_START
        self._stalled = False
        self._history = []
    
    def fetch(self) -> dict:
        """
        Mevcut PC'den instruction fetch et
        
        Returns:
            {
                'instruction': 16-bit instruction,
                'pc': current PC,
                'pc_next': PC+2
            }
        """
        # Mevcut PC'yi kaydet
        current_pc = self.pc
        
        # Instruction fetch
        try:
            instruction = self.imem.fetch(self.pc)
        except Exception:
            instruction = NOP_INSTRUCTION
        
        # PC+2 hesapla (sonraki instruction)
        pc_next = to_unsigned_16(self.pc + BYTES_PER_WORD)
        
        # Geçmişe kaydet
        self._history.append({
            'pc': current_pc,
            'instruction': instruction,
            'pc_next': pc_next
        })
        
        return {
            'instruction': instruction,
            'pc': current_pc,
            'pc_next': pc_next
        }
    
    def advance_pc(self):
        """PC'yi bir sonraki instruction'a ilerlet"""
        if not self._stalled:
            self.pc = to_unsigned_16(self.pc + BYTES_PER_WORD)
    
    def set_pc(self, new_pc: int):
        """
        PC'yi yeni değere ayarla (branch/jump için)
        
        Args:
            new_pc: Yeni PC değeri
        """
        self.pc = to_unsigned_16(new_pc)
    
    def branch(self, target: int):
        """
        Branch hedefine git
        
        Args:
            target: Branch hedef adresi
        """
        self.set_pc(target)
    
    def jump(self, target: int):
        """
        Jump hedefine git
        
        Args:
            target: Jump hedef adresi
        """
        self.set_pc(target)
    
    def stall(self):
        """PC'yi dondur (hazard durumunda)"""
        self._stalled = True
    
    def unstall(self):
        """Stall durumunu kaldır"""
        self._stalled = False
    
    @property
    def is_stalled(self) -> bool:
        """Stall durumunda mı?"""
        return self._stalled
    
    def calculate_branch_target(self, pc: int, offset: int) -> int:
        """
        Branch hedef adresini hesapla
        
        Branch hedef = PC + 2 + (offset * 2)
        
        Args:
            pc: Branch instruction'ın PC'si
            offset: Sign-extended offset değeri
        
        Returns:
            Branch hedef adresi
        """
        # PC+2 (branch instruction'dan sonraki adres)
        # + offset * 2 (word offset to byte offset)
        target = pc + BYTES_PER_WORD + (offset * BYTES_PER_WORD)
        return to_unsigned_16(target)
    
    def calculate_jump_target(self, pc: int, addr: int) -> int:
        """
        Jump hedef adresini hesapla
        
        Jump hedef = {PC[15:13], addr[11:0], 0}
        (Üst 3 bit PC'den, alt 13 bit instruction'dan, en alt bit 0)
        
        Args:
            pc: Jump instruction'ın PC'si
            addr: 12-bit jump address
        
        Returns:
            Jump hedef adresi
        """
        # Üst 3 bit PC'den
        pc_upper = pc & 0xE000  # bit 15-13
        # 12-bit address'i 1 bit sola kaydır (word alignment)
        target = pc_upper | ((addr & 0xFFF) << 1)
        return to_unsigned_16(target)
    
    def reset(self):
        """IF stage'i sıfırla"""
        self.pc = PC_START
        self._stalled = False
        self._history.clear()
    
    def get_history(self) -> list:
        """Fetch geçmişini döndür"""
        return self._history.copy()
    
    def clear_history(self):
        """Geçmişi temizle"""
        self._history.clear()
    
    def __str__(self) -> str:
        return f"IF Stage: PC=0x{self.pc:04X}, Stalled={self._stalled}"
