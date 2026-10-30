"""
RISC-16 Pipeline Registers
Pipeline aşamaları arasındaki register'lar
"""

from dataclasses import dataclass, field
from typing import Optional
from ..utils.constants import NOP_INSTRUCTION


@dataclass
class IF_ID_Register:
    """
    IF/ID Pipeline Register
    Instruction Fetch → Instruction Decode
    """
    pc: int = 0                    # Program Counter (PC+2)
    instruction: int = NOP_INSTRUCTION  # Fetched instruction
    valid: bool = False            # Geçerli veri var mı?
    
    # Debug bilgileri
    pc_current: int = 0            # Fetch edilen instruction'ın PC'si
    
    def flush(self):
        """Register'ı temizle (NOP ile doldur)"""
        self.pc = 0
        self.instruction = NOP_INSTRUCTION
        self.valid = False
        self.pc_current = 0
    
    def to_dict(self) -> dict:
        return {
            'pc': self.pc,
            'pc_current': self.pc_current,
            'instruction': self.instruction,
            'valid': self.valid
        }


@dataclass
class ID_EX_Register:
    """
    ID/EX Pipeline Register
    Instruction Decode → Execute
    """
    # PC bilgisi
    pc: int = 0                    # PC+2 (branch hesabı için)
    
    # Register değerleri
    rs_value: int = 0              # rs register değeri
    rt_value: int = 0              # rt register değeri
    
    # Instruction alanları
    rs: int = 0                    # rs register numarası
    rt: int = 0                    # rt register numarası
    rd: int = 0                    # rd register numarası
    shamt: int = 0                 # Shift amount
    func: int = 0                  # Function code
    imm: int = 0                   # Sign-extended immediate
    addr: int = 0                  # Jump address
    opcode: int = 0                # Opcode
    
    # Kontrol sinyalleri
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
    alu_op: int = 0
    
    # Meta
    valid: bool = False
    instruction: int = NOP_INSTRUCTION  # Debug için orijinal instruction
    
    def flush(self):
        """Register'ı temizle - kontrol sinyallerini sıfırla"""
        self.reg_write = 0
        self.mem_write = 0
        self.mem_read = 0
        self.branch = 0
        self.jump = 0
        self.valid = False
        self.instruction = NOP_INSTRUCTION
    
    def get_write_register(self) -> int:
        """
        Yazılacak register numarasını döndür
        RegDst sinyaline göre rd veya rt
        JAL için R7 (return address)
        """
        if self.link:
            return 7  # R7 = ra
        elif self.reg_dst:
            return self.rd
        else:
            return self.rt
    
    def to_dict(self) -> dict:
        return {
            'pc': self.pc,
            'rs': self.rs, 'rt': self.rt, 'rd': self.rd,
            'rs_value': self.rs_value, 'rt_value': self.rt_value,
            'imm': self.imm, 'shamt': self.shamt,
            'opcode': self.opcode, 'func': self.func,
            'reg_dst': self.reg_dst, 'alu_src': self.alu_src,
            'mem_to_reg': self.mem_to_reg, 'reg_write': self.reg_write,
            'mem_read': self.mem_read, 'mem_write': self.mem_write,
            'branch': self.branch, 'jump': self.jump,
            'valid': self.valid, 'instruction': self.instruction
        }


@dataclass  
class EX_MEM_Register:
    """
    EX/MEM Pipeline Register
    Execute → Memory Access
    """
    # PC bilgisi
    pc: int = 0                    # Branch target için
    branch_target: int = 0         # Hesaplanan branch adresi
    
    # ALU sonuçları
    alu_result: int = 0            # ALU çıkışı
    zero_flag: bool = False        # ALU zero flag
    
    # Register bilgileri
    rt_value: int = 0              # Store için veri
    write_register: int = 0        # Yazılacak register
    
    # Kontrol sinyalleri (MEM ve WB için)
    mem_to_reg: int = 0
    reg_write: int = 0
    mem_read: int = 0
    mem_write: int = 0
    branch: int = 0
    branch_ne: int = 0
    jump: int = 0
    link: int = 0
    
    # Meta
    valid: bool = False
    instruction: int = NOP_INSTRUCTION
    opcode: int = 0
    
    def flush(self):
        """Register'ı temizle"""
        self.reg_write = 0
        self.mem_write = 0
        self.mem_read = 0
        self.branch = 0
        self.jump = 0
        self.valid = False
        self.instruction = NOP_INSTRUCTION
    
    def should_branch(self) -> bool:
        """Branch alınmalı mı?"""
        if not self.branch:
            return False
        
        # BEQ: zero flag set ise branch
        # BNE: zero flag clear ise branch
        if self.branch_ne:
            return not self.zero_flag
        else:
            return self.zero_flag
    
    def to_dict(self) -> dict:
        return {
            'pc': self.pc, 'branch_target': self.branch_target,
            'alu_result': self.alu_result, 'zero_flag': self.zero_flag,
            'rt_value': self.rt_value, 'write_register': self.write_register,
            'mem_to_reg': self.mem_to_reg, 'reg_write': self.reg_write,
            'mem_read': self.mem_read, 'mem_write': self.mem_write,
            'branch': self.branch, 'jump': self.jump,
            'valid': self.valid, 'instruction': self.instruction
        }


@dataclass
class MEM_WB_Register:
    """
    MEM/WB Pipeline Register
    Memory Access → Write Back
    """
    # Memory ve ALU verileri
    mem_data: int = 0              # Memory'den okunan veri
    alu_result: int = 0            # ALU sonucu
    
    # Register bilgileri
    write_register: int = 0        # Yazılacak register
    
    # Kontrol sinyalleri (WB için)
    mem_to_reg: int = 0
    reg_write: int = 0
    
    # Meta
    valid: bool = False
    instruction: int = NOP_INSTRUCTION
    opcode: int = 0
    
    def flush(self):
        """Register'ı temizle"""
        self.reg_write = 0
        self.valid = False
        self.instruction = NOP_INSTRUCTION
    
    def get_write_data(self) -> int:
        """Register'a yazılacak veriyi döndür"""
        if self.mem_to_reg:
            return self.mem_data
        else:
            return self.alu_result
    
    def to_dict(self) -> dict:
        return {
            'mem_data': self.mem_data, 'alu_result': self.alu_result,
            'write_register': self.write_register,
            'mem_to_reg': self.mem_to_reg, 'reg_write': self.reg_write,
            'valid': self.valid, 'instruction': self.instruction
        }


class PipelineRegisters:
    """
    Tüm pipeline register'larını yöneten sınıf
    """
    
    def __init__(self):
        """Pipeline register'larını başlat"""
        self.IF_ID = IF_ID_Register()
        self.ID_EX = ID_EX_Register()
        self.EX_MEM = EX_MEM_Register()
        self.MEM_WB = MEM_WB_Register()
    
    def flush_all(self):
        """Tüm register'ları temizle"""
        self.IF_ID.flush()
        self.ID_EX.flush()
        self.EX_MEM.flush()
        self.MEM_WB.flush()
    
    def flush_if_id(self):
        """IF/ID register'ını temizle (branch/jump flush)"""
        self.IF_ID.flush()
    
    def flush_id_ex(self):
        """ID/EX register'ını temizle (hazard stall)"""
        self.ID_EX.flush()
    
    def reset(self):
        """Tüm register'ları sıfırla"""
        self.__init__()
    
    def get_state(self) -> dict:
        """Tüm register durumlarını döndür"""
        return {
            'IF_ID': self.IF_ID.to_dict(),
            'ID_EX': self.ID_EX.to_dict(),
            'EX_MEM': self.EX_MEM.to_dict(),
            'MEM_WB': self.MEM_WB.to_dict()
        }
    
    def __str__(self) -> str:
        """Pipeline durumunu string olarak döndür"""
        lines = ["Pipeline Registers:"]
        lines.append(f"  IF/ID:  PC=0x{self.IF_ID.pc:04X}, Inst=0x{self.IF_ID.instruction:04X}, Valid={self.IF_ID.valid}")
        lines.append(f"  ID/EX:  rs={self.ID_EX.rs}, rt={self.ID_EX.rt}, rd={self.ID_EX.rd}, Valid={self.ID_EX.valid}")
        lines.append(f"  EX/MEM: ALU=0x{self.EX_MEM.alu_result:04X}, WriteReg={self.EX_MEM.write_register}, Valid={self.EX_MEM.valid}")
        lines.append(f"  MEM/WB: Data=0x{self.MEM_WB.alu_result:04X}, WriteReg={self.MEM_WB.write_register}, Valid={self.MEM_WB.valid}")
        return "\n".join(lines)
