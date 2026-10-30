"""
RISC-16 Control Unit
Instruction'a göre kontrol sinyalleri üretir
"""

from dataclasses import dataclass
from ..utils.constants import Opcode, FuncCode, ALUOp


@dataclass
class ControlSignals:
    """
    Kontrol sinyalleri veri yapısı
    
    Attributes:
        reg_dst: Write register seçimi (0: rt, 1: rd)
        alu_src: ALU B girişi seçimi (0: register, 1: immediate)
        mem_to_reg: Write data seçimi (0: ALU result, 1: memory data)
        reg_write: Register'a yazma aktif
        mem_read: Memory'den okuma aktif
        mem_write: Memory'ye yazma aktif
        branch: Branch instruction
        branch_ne: BNE için (1: not equal'da branch)
        jump: Jump instruction
        jump_reg: JR instruction (register'dan jump)
        link: JAL için (return address kaydet)
        alu_op: ALU operasyon tipi
    """
    reg_dst: int = 0
    alu_src: int = 0
    mem_to_reg: int = 0
    reg_write: int = 0
    mem_read: int = 0
    mem_write: int = 0
    branch: int = 0
    branch_ne: int = 0
    jump: int = 0
    jump_reg: int = 0
    link: int = 0
    alu_op: int = ALUOp.ADD
    
    def to_dict(self) -> dict:
        """Dictionary olarak döndür"""
        return {
            'reg_dst': self.reg_dst,
            'alu_src': self.alu_src,
            'mem_to_reg': self.mem_to_reg,
            'reg_write': self.reg_write,
            'mem_read': self.mem_read,
            'mem_write': self.mem_write,
            'branch': self.branch,
            'branch_ne': self.branch_ne,
            'jump': self.jump,
            'jump_reg': self.jump_reg,
            'link': self.link,
            'alu_op': self.alu_op
        }
    
    def __str__(self) -> str:
        """String representation"""
        active = []
        if self.reg_dst: active.append("RegDst")
        if self.alu_src: active.append("ALUSrc")
        if self.mem_to_reg: active.append("MemToReg")
        if self.reg_write: active.append("RegWrite")
        if self.mem_read: active.append("MemRead")
        if self.mem_write: active.append("MemWrite")
        if self.branch: active.append("Branch")
        if self.branch_ne: active.append("BranchNE")
        if self.jump: active.append("Jump")
        if self.jump_reg: active.append("JumpReg")
        if self.link: active.append("Link")
        
        return f"Controls: [{', '.join(active) if active else 'None'}]"


class ControlUnit:
    """
    Control Unit
    Opcode'a göre kontrol sinyalleri üretir
    """
    
    def __init__(self):
        """Control unit başlat"""
        self._last_signals = None
        self._signal_history = []
    
    def generate_signals(self, opcode: int, func: int = 0) -> ControlSignals:
        """
        Opcode ve function code'a göre kontrol sinyalleri üret
        
        Args:
            opcode: 4-bit opcode
            func: 3-bit function code (R-Type için)
        
        Returns:
            ControlSignals objesi
        """
        signals = ControlSignals()
        
        # R-Type instructions
        if opcode == Opcode.R_TYPE:
            signals.reg_dst = 1      # rd'ye yaz
            signals.alu_src = 0      # Register'dan
            signals.mem_to_reg = 0   # ALU sonucu
            signals.reg_write = 1    # Register'a yaz
            signals.mem_read = 0
            signals.mem_write = 0
            signals.branch = 0
            signals.jump = 0
            
            # Function code'a göre ALU operasyonu
            alu_ops = {
                FuncCode.ADD: ALUOp.ADD,
                FuncCode.SUB: ALUOp.SUB,
                FuncCode.AND: ALUOp.AND,
                FuncCode.OR:  ALUOp.OR,
                FuncCode.SLT: ALUOp.SLT,
                FuncCode.SLL: ALUOp.SLL,
                FuncCode.SRL: ALUOp.SRL,
            }
            signals.alu_op = alu_ops.get(func, ALUOp.ADD)
        
        # ADDI
        elif opcode == Opcode.ADDI:
            signals.reg_dst = 0      # rt'ye yaz
            signals.alu_src = 1      # Immediate
            signals.mem_to_reg = 0   # ALU sonucu
            signals.reg_write = 1    # Register'a yaz
            signals.alu_op = ALUOp.ADD
        
        # LW (Load Word)
        elif opcode == Opcode.LW:
            signals.reg_dst = 0      # rt'ye yaz
            signals.alu_src = 1      # Immediate (offset)
            signals.mem_to_reg = 1   # Memory'den
            signals.reg_write = 1    # Register'a yaz
            signals.mem_read = 1     # Memory oku
            signals.alu_op = ALUOp.ADD  # Adres hesabı
        
        # SW (Store Word)
        elif opcode == Opcode.SW:
            signals.reg_dst = 0
            signals.alu_src = 1      # Immediate (offset)
            signals.reg_write = 0    # Register'a yazma
            signals.mem_write = 1    # Memory'ye yaz
            signals.alu_op = ALUOp.ADD  # Adres hesabı
        
        # BEQ (Branch if Equal)
        elif opcode == Opcode.BEQ:
            signals.alu_src = 0      # Register'dan
            signals.reg_write = 0    # Register'a yazma
            signals.branch = 1       # Branch aktif
            signals.branch_ne = 0    # Equal'da branch
            signals.alu_op = ALUOp.SUB  # Karşılaştırma için
        
        # BNE (Branch if Not Equal)
        elif opcode == Opcode.BNE:
            signals.alu_src = 0      # Register'dan
            signals.reg_write = 0    # Register'a yazma
            signals.branch = 1       # Branch aktif
            signals.branch_ne = 1    # Not equal'da branch
            signals.alu_op = ALUOp.SUB  # Karşılaştırma için
        
        # J (Jump)
        elif opcode == Opcode.J:
            signals.reg_write = 0
            signals.jump = 1         # Jump aktif
        
        # JAL (Jump and Link)
        elif opcode == Opcode.JAL:
            signals.reg_dst = 0
            signals.reg_write = 1    # R7'ye (ra) yaz
            signals.jump = 1         # Jump aktif
            signals.link = 1         # Return address kaydet
        
        # JR (Jump Register)
        elif opcode == Opcode.JR:
            signals.reg_write = 0
            signals.jump = 1         # Jump aktif
            signals.jump_reg = 1     # Register'dan adres al
        
        # Geçmişe kaydet
        self._last_signals = signals
        self._signal_history.append({
            'opcode': opcode,
            'func': func,
            'signals': signals.to_dict()
        })
        
        return signals
    
    def get_nop_signals(self) -> ControlSignals:
        """
        NOP için kontrol sinyalleri (tüm write'lar kapalı)
        Pipeline stall durumunda kullanılır
        """
        return ControlSignals(
            reg_write=0,
            mem_write=0,
            branch=0,
            jump=0
        )
    
    @property
    def last_signals(self) -> ControlSignals:
        """Son üretilen sinyaller"""
        return self._last_signals
    
    def get_signal_history(self) -> list:
        """Sinyal geçmişini döndür"""
        return self._signal_history.copy()
    
    def clear_history(self) -> None:
        """Geçmişi temizle"""
        self._signal_history.clear()
    
    def reset(self) -> None:
        """Control unit'i sıfırla"""
        self._last_signals = None
        self._signal_history.clear()


# Kontrol sinyallerini gösteren tablo (debug için)
CONTROL_TABLE = """
+-------+--------+---------+------------+----------+----------+-----------+--------+------+------+
| Inst  | RegDst | ALUSrc  | MemToReg   | RegWrite | MemRead  | MemWrite  | Branch | Jump | Link |
+-------+--------+---------+------------+----------+----------+-----------+--------+------+------+
| R-Type|   1    |    0    |     0      |    1     |    0     |     0     |   0    |  0   |  0   |
| ADDI  |   0    |    1    |     0      |    1     |    0     |     0     |   0    |  0   |  0   |
| LW    |   0    |    1    |     1      |    1     |    1     |     0     |   0    |  0   |  0   |
| SW    |   X    |    1    |     X      |    0     |    0     |     1     |   0    |  0   |  0   |
| BEQ   |   X    |    0    |     X      |    0     |    0     |     0     |   1    |  0   |  0   |
| BNE   |   X    |    0    |     X      |    0     |    0     |     0     |   1    |  0   |  0   |
| J     |   X    |    X    |     X      |    0     |    0     |     0     |   0    |  1   |  0   |
| JAL   |   X    |    X    |     X      |    1     |    0     |     0     |   0    |  1   |  1   |
| JR    |   X    |    X    |     X      |    0     |    0     |     0     |   0    |  1   |  0   |
+-------+--------+---------+------------+----------+----------+-----------+--------+------+------+
"""
