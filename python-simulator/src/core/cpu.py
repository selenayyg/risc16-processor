"""
RISC-16 CPU
Ana işlemci sınıfı - 5 aşamalı pipeline kontrolü
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict

from ..utils.constants import (
    Opcode, NOP_INSTRUCTION, BYTES_PER_WORD,
    PipelineStage, PIPELINE_STAGES, ForwardingSource
)
from ..utils.helpers import decode_instruction, disassemble, format_hex
from ..core.registers import RegisterFile
from ..core.memory import InstructionMemory, DataMemory
from ..core.alu import ALU
from ..core.control_unit import ControlUnit
from ..pipeline.pipeline_registers import PipelineRegisters
from ..pipeline.fetch import InstructionFetch
from ..pipeline.decode import InstructionDecode
from ..pipeline.execute import Execute
from ..pipeline.memory_access import MemoryAccess
from ..pipeline.writeback import WriteBack
from ..hazard.hazard_detection import HazardDetectionUnit
from ..hazard.forwarding_unit import ForwardingUnit
from ..hazard.stall_controller import StallController


@dataclass
class CycleInfo:
    """Her cycle için detaylı bilgi"""
    cycle: int = 0
    pc: int = 0
    
    # Her stage'deki instruction
    if_instruction: int = NOP_INSTRUCTION
    id_instruction: int = NOP_INSTRUCTION
    ex_instruction: int = NOP_INSTRUCTION
    mem_instruction: int = NOP_INSTRUCTION
    wb_instruction: int = NOP_INSTRUCTION
    
    # Hazard bilgisi
    stall: bool = False
    flush: bool = False
    forward_a: str = "None"
    forward_b: str = "None"
    
    # Register ve memory değişiklikleri
    reg_write: Optional[tuple] = None  # (reg_num, value)
    mem_write: Optional[tuple] = None  # (address, value)


class CPU:
    """
    RISC-16 CPU
    5 aşamalı pipeline ile 16-bit RISC işlemci
    """
    
    def __init__(self):
        """CPU'yu başlat"""
        # Core bileşenler
        self.reg_file = RegisterFile()
        self.imem = InstructionMemory()
        self.dmem = DataMemory()
        self.alu = ALU()
        self.control = ControlUnit()
        
        # Pipeline aşamaları
        self.IF = InstructionFetch(self.imem)
        self.ID = InstructionDecode(self.reg_file, self.control)
        self.EX = Execute(self.alu)
        self.MEM = MemoryAccess(self.dmem)
        self.WB = WriteBack(self.reg_file)
        
        # Pipeline register'ları
        self.pipeline_regs = PipelineRegisters()
        
        # Hazard birimleri
        self.hazard_unit = HazardDetectionUnit()
        self.forwarding_unit = ForwardingUnit()
        self.stall_ctrl = StallController()
        
        # Simülasyon durumu
        self._cycle = 0
        self._running = False
        self._finished = False
        self._cycle_history: List[CycleInfo] = []
        
        # İstatistikler
        self._instructions_executed = 0
        self._total_cycles = 0
        
        # Geri adım için snapshot'lar
        self._snapshots = []
        self._max_snapshots = 100  # Max 100 adım geri gidilebilir
    
    def load_program(self, instructions: list):
        """
        Programı instruction memory'ye yükle
        
        Args:
            instructions: 16-bit instruction listesi
        """
        self.reset()
        self.imem.load_program(instructions)
    
    def reset(self):
        """CPU'yu sıfırla"""
        self.reg_file.reset()
        self.imem.reset()
        self.dmem.reset()
        self.alu.reset()
        self.control.reset()
        
        self.IF.reset()
        self.ID.reset()
        self.EX.reset()
        self.MEM.reset()
        self.WB.reset()
        
        self.pipeline_regs.reset()
        
        self.hazard_unit.reset()
        self.forwarding_unit.reset()
        self.stall_ctrl.reset()
        
        self._cycle = 0
        self._running = False
        self._finished = False
        self._halt_detected = False
        self._halt_cycle = 0
        self._cycle_history.clear()
        
        self._instructions_executed = 0
        self._total_cycles = 0
        
        # Snapshot'ları temizle
        self._snapshots = []
    
    def step(self) -> CycleInfo:
        """
        Bir clock cycle çalıştır
        
        Returns:
            CycleInfo - Bu cycle'ın detayları
        """
        if self._finished:
            return self._cycle_history[-1] if self._cycle_history else CycleInfo()
        
        # Adımdan önce snapshot al (geri adım için)
        self._save_snapshot()
        
        self._cycle += 1
        cycle_info = CycleInfo(cycle=self._cycle, pc=self.IF.pc)
        
        # Pipeline register'larını geçici olarak sakla
        if_id = self.pipeline_regs.IF_ID
        id_ex = self.pipeline_regs.ID_EX
        ex_mem = self.pipeline_regs.EX_MEM
        mem_wb = self.pipeline_regs.MEM_WB
        
        # ===== WB Stage =====
        if mem_wb.valid:
            wb_result = self.WB.writeback(
                mem_data=mem_wb.mem_data,
                alu_result=mem_wb.alu_result,
                write_register=mem_wb.write_register,
                mem_to_reg=mem_wb.mem_to_reg,
                reg_write=mem_wb.reg_write
            )
            cycle_info.wb_instruction = mem_wb.instruction
            if wb_result['written']:
                cycle_info.reg_write = (wb_result['write_register'], wb_result['write_data'])
                self._instructions_executed += 1
        
        # ===== MEM Stage =====
        new_mem_wb = self.pipeline_regs.MEM_WB.__class__()
        if ex_mem.valid:
            mem_result = self.MEM.access(
                alu_result=ex_mem.alu_result,
                rt_value=ex_mem.rt_value,
                mem_read=ex_mem.mem_read,
                mem_write=ex_mem.mem_write
            )
            
            # MEM/WB register'ını güncelle
            new_mem_wb.mem_data = mem_result['mem_data']
            new_mem_wb.alu_result = ex_mem.alu_result
            new_mem_wb.write_register = ex_mem.write_register
            new_mem_wb.mem_to_reg = ex_mem.mem_to_reg
            new_mem_wb.reg_write = ex_mem.reg_write
            new_mem_wb.valid = True
            new_mem_wb.instruction = ex_mem.instruction
            new_mem_wb.opcode = ex_mem.opcode
            
            cycle_info.mem_instruction = ex_mem.instruction
            if ex_mem.mem_write:
                cycle_info.mem_write = (ex_mem.alu_result, ex_mem.rt_value)
        
        # ===== EX Stage =====
        new_ex_mem = self.pipeline_regs.EX_MEM.__class__()
        branch_taken = False
        jump_taken = False
        jump_target = 0
        
        if id_ex.valid:
            # Forwarding kontrolü
            forward = self.forwarding_unit.get_forwarding(
                id_ex.rs, id_ex.rt, ex_mem, mem_wb
            )
            
            # Forwarded değerler
            forward_a_src, forward_a_val = forward['forward_a']
            forward_b_src, forward_b_val = forward['forward_b']
            
            rs_value = forward_a_val if forward_a_val is not None else id_ex.rs_value
            rt_value = forward_b_val if forward_b_val is not None else id_ex.rt_value
            
            # Forwarding bilgisini kaydet
            if forward_a_src != ForwardingSource.NONE:
                cycle_info.forward_a = f"R{id_ex.rs} from {'EX/MEM' if forward_a_src == ForwardingSource.EX_MEM else 'MEM/WB'}"
            if forward_b_src != ForwardingSource.NONE:
                cycle_info.forward_b = f"R{id_ex.rt} from {'EX/MEM' if forward_b_src == ForwardingSource.EX_MEM else 'MEM/WB'}"
            
            # ALU operasyonu
            ex_result = self.EX.execute(
                rs_value=id_ex.rs_value,
                rt_value=id_ex.rt_value,
                imm=id_ex.imm,
                shamt=id_ex.shamt,
                pc=id_ex.pc,
                opcode=id_ex.opcode,
                func=id_ex.func,
                alu_src=id_ex.alu_src,
                alu_op=id_ex.alu_op,
                forwarded_rs=forward_a_val,
                forwarded_rt=forward_b_val
            )
            
            # Branch kontrolü
            if id_ex.branch:
                if id_ex.branch_ne:
                    branch_taken = not ex_result['zero_flag']  # BNE
                else:
                    branch_taken = ex_result['zero_flag']      # BEQ
                
                if branch_taken:
                    jump_target = ex_result['branch_target']
            
            # Jump kontrolü
            if id_ex.jump:
                jump_taken = True
                if id_ex.jump_reg:
                    # JR: rs'den adres al
                    jump_target = rs_value
                else:
                    # J/JAL: addr'den hesapla
                    jump_target = self.EX.calculate_jump_target(id_ex.pc - BYTES_PER_WORD, id_ex.addr)
            
            # EX/MEM register'ını güncelle
            new_ex_mem.pc = id_ex.pc
            new_ex_mem.branch_target = ex_result['branch_target']
            new_ex_mem.alu_result = ex_result['alu_result']
            new_ex_mem.zero_flag = ex_result['zero_flag']
            new_ex_mem.rt_value = rt_value  # Store için
            new_ex_mem.write_register = id_ex.get_write_register()
            new_ex_mem.mem_to_reg = id_ex.mem_to_reg
            new_ex_mem.reg_write = id_ex.reg_write
            new_ex_mem.mem_read = id_ex.mem_read
            new_ex_mem.mem_write = id_ex.mem_write
            new_ex_mem.branch = id_ex.branch
            new_ex_mem.branch_ne = id_ex.branch_ne
            new_ex_mem.jump = id_ex.jump
            new_ex_mem.link = id_ex.link
            new_ex_mem.valid = True
            new_ex_mem.instruction = id_ex.instruction
            new_ex_mem.opcode = id_ex.opcode
            
            # JAL için return address
            if id_ex.link:
                new_ex_mem.alu_result = id_ex.pc  # PC+2 kaydet
            
            cycle_info.ex_instruction = id_ex.instruction
        
        # ===== ID Stage =====
        new_id_ex = self.pipeline_regs.ID_EX.__class__()
        load_use_hazard = False
        
        if if_id.valid:
            # Instruction decode
            decoded = self.ID.decode(if_id.instruction, if_id.pc)
            
            # Load-use hazard kontrolü
            if_id_uses_rs = decoded['opcode'] not in [Opcode.J, Opcode.JAL]
            if_id_uses_rt = decoded['opcode'] in [Opcode.R_TYPE, Opcode.BEQ, Opcode.BNE, Opcode.SW]
            
            load_use_hazard = self.hazard_unit.detect_load_use_hazard(
                id_ex,
                decoded['rs'],
                decoded['rt'],
                if_id_uses_rs,
                if_id_uses_rt
            )
            
            if not load_use_hazard:
                # ID/EX register'ını güncelle
                signals = decoded['signals']
                
                new_id_ex.pc = if_id.pc
                new_id_ex.rs_value = decoded['rs_value']
                new_id_ex.rt_value = decoded['rt_value']
                new_id_ex.rs = decoded['rs']
                new_id_ex.rt = decoded['rt']
                new_id_ex.rd = decoded['rd']
                new_id_ex.shamt = decoded['shamt']
                new_id_ex.func = decoded['func']
                new_id_ex.imm = decoded['imm']
                new_id_ex.addr = decoded['addr']
                new_id_ex.opcode = decoded['opcode']
                
                new_id_ex.reg_dst = signals.reg_dst
                new_id_ex.alu_src = signals.alu_src
                new_id_ex.mem_to_reg = signals.mem_to_reg
                new_id_ex.reg_write = signals.reg_write
                new_id_ex.mem_read = signals.mem_read
                new_id_ex.mem_write = signals.mem_write
                new_id_ex.branch = signals.branch
                new_id_ex.branch_ne = signals.branch_ne
                new_id_ex.jump = signals.jump
                new_id_ex.jump_reg = signals.jump_reg
                new_id_ex.link = signals.link
                new_id_ex.alu_op = signals.alu_op
                new_id_ex.valid = True
                new_id_ex.instruction = if_id.instruction
            
            cycle_info.id_instruction = if_id.instruction
        
        # ===== IF Stage =====
        new_if_id = self.pipeline_regs.IF_ID.__class__()
        
        # Stall/Flush sinyalleri
        stall_signals = self.stall_ctrl.generate_stall_signals(
            load_use_hazard=load_use_hazard,
            branch_taken=branch_taken,
            jump=jump_taken
        )
        
        cycle_info.stall = stall_signals.is_stalled()
        cycle_info.flush = stall_signals.is_flushing()
        
        if not stall_signals.is_stalled():
            # Normal fetch
            fetch_result = self.IF.fetch()
            
            new_if_id.instruction = fetch_result['instruction']
            new_if_id.pc = fetch_result['pc_next']
            new_if_id.pc_current = fetch_result['pc']
            new_if_id.valid = True
            
            cycle_info.if_instruction = fetch_result['instruction']
            
            # PC güncelle
            if branch_taken or jump_taken:
                self.IF.set_pc(jump_target)
            else:
                self.IF.advance_pc()
        else:
            # Stall - IF/ID'yi koru
            new_if_id = if_id
            cycle_info.if_instruction = if_id.instruction if if_id.valid else NOP_INSTRUCTION
        
        # ===== Pipeline Register'larını Güncelle =====
        # Flush durumunda IF/ID ve ID/EX'i temizle
        if branch_taken or jump_taken:
            new_if_id.flush()
            new_id_ex.flush()
        
        # Load-use hazard durumunda ID/EX'e bubble (NOP) ekle
        if load_use_hazard:
            new_id_ex.flush()
        
        self.pipeline_regs.IF_ID = new_if_id
        self.pipeline_regs.ID_EX = new_id_ex
        self.pipeline_regs.EX_MEM = new_ex_mem
        self.pipeline_regs.MEM_WB = new_mem_wb
        
        # Simülasyon bitiş kontrolü
        if self._check_finished():
            self._finished = True
        
        # Cycle bilgisini kaydet
        self._cycle_history.append(cycle_info)
        self._total_cycles += 1
        
        return cycle_info
    
    def _check_finished(self) -> bool:
        """Simülasyon bitti mi kontrol et"""
        from ..utils.constants import Opcode
        halt_opcode = Opcode.HALT << 12  # 0xF000
        
        def is_halt(instruction):
            return (instruction & 0xF000) == halt_opcode
        
        # HALT detected - mark it
        if not hasattr(self, '_halt_detected'):
            self._halt_detected = False
            self._halt_cycle = 0
        
        # Check for HALT entering ID stage
        if is_halt(self.pipeline_regs.IF_ID.instruction):
            self._halt_detected = True
            self._halt_cycle = self._cycle
        
        # If halt detected, wait for pipeline to drain (4 more cycles max)
        if self._halt_detected and self._cycle > self._halt_cycle + 4:
            return True
        
        # Tüm pipeline boş mu?
        if not self.pipeline_regs.IF_ID.valid and \
           not self.pipeline_regs.ID_EX.valid and \
           not self.pipeline_regs.EX_MEM.valid and \
           not self.pipeline_regs.MEM_WB.valid:
            return True
        
        # PC instruction memory dışına çıktı mı?
        if self.IF.pc >= self.imem.size:
            return True
        
        # Sonsuz döngü kontrolü (opsiyonel)
        if self._cycle > 10000:
            return True
        
        return False
    
    def run(self, max_cycles: int = 1000) -> List[CycleInfo]:
        """
        Programı sonuna kadar çalıştır
        
        Args:
            max_cycles: Maksimum cycle sayısı
        
        Returns:
            Tüm cycle bilgileri
        """
        self._running = True
        
        while not self._finished and self._cycle < max_cycles:
            self.step()
        
        self._running = False
        return self._cycle_history
    
    def get_pipeline_state(self) -> Dict:
        """Pipeline durumunu döndür"""
        return {
            'IF': {
                'pc': self.IF.pc,
                'instruction': self.pipeline_regs.IF_ID.instruction if self.pipeline_regs.IF_ID.valid else NOP_INSTRUCTION,
                'disasm': disassemble(self.pipeline_regs.IF_ID.instruction) if self.pipeline_regs.IF_ID.valid else "NOP"
            },
            'ID': {
                'instruction': self.pipeline_regs.ID_EX.instruction if self.pipeline_regs.ID_EX.valid else NOP_INSTRUCTION,
                'disasm': disassemble(self.pipeline_regs.ID_EX.instruction) if self.pipeline_regs.ID_EX.valid else "NOP"
            },
            'EX': {
                'instruction': self.pipeline_regs.EX_MEM.instruction if self.pipeline_regs.EX_MEM.valid else NOP_INSTRUCTION,
                'disasm': disassemble(self.pipeline_regs.EX_MEM.instruction) if self.pipeline_regs.EX_MEM.valid else "NOP"
            },
            'MEM': {
                'instruction': self.pipeline_regs.MEM_WB.instruction if self.pipeline_regs.MEM_WB.valid else NOP_INSTRUCTION,
                'disasm': disassemble(self.pipeline_regs.MEM_WB.instruction) if self.pipeline_regs.MEM_WB.valid else "NOP"
            },
            'WB': {
                'instruction': NOP_INSTRUCTION,  # WB zaten tamamlandı
                'disasm': "NOP"
            }
        }
    
    def _save_snapshot(self):
        """Mevcut CPU durumunu kaydet (geri adım için)"""
        import copy
        
        snapshot = {
            'cycle': self._cycle,
            'finished': self._finished,
            'halt_detected': getattr(self, '_halt_detected', False),
            'halt_cycle': getattr(self, '_halt_cycle', 0),
            'instructions_executed': self._instructions_executed,
            'total_cycles': self._total_cycles,
            'pc': self.IF.pc,
            'registers': [self.reg_file.read(i) for i in range(8)],
            'dmem': copy.deepcopy(self.dmem._data),
            'pipeline_IF_ID': copy.deepcopy(self.pipeline_regs.IF_ID.__dict__),
            'pipeline_ID_EX': copy.deepcopy(self.pipeline_regs.ID_EX.__dict__),
            'pipeline_EX_MEM': copy.deepcopy(self.pipeline_regs.EX_MEM.__dict__),
            'pipeline_MEM_WB': copy.deepcopy(self.pipeline_regs.MEM_WB.__dict__),
            'stall_count': self.stall_ctrl.stall_count,
            'flush_count': self.stall_ctrl.flush_count,
            'cycle_history_len': len(self._cycle_history),
        }
        
        self._snapshots.append(snapshot)
        
        # Max snapshot sayısını aşarsa en eskiyi sil
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots.pop(0)
    
    def step_back(self) -> bool:
        """
        Bir adım geri git
        
        Returns:
            True: Başarılı, False: Geri gidilecek adım yok
        """
        if not self._snapshots:
            return False
        
        snapshot = self._snapshots.pop()
        
        # CPU durumunu geri yükle
        self._cycle = snapshot['cycle']
        self._finished = snapshot['finished']
        self._halt_detected = snapshot['halt_detected']
        self._halt_cycle = snapshot['halt_cycle']
        self._instructions_executed = snapshot['instructions_executed']
        self._total_cycles = snapshot['total_cycles']
        
        # PC'yi geri yükle
        self.IF.pc = snapshot['pc']
        
        # Register'ları geri yükle
        for i, val in enumerate(snapshot['registers']):
            self.reg_file.write(i, val)
        
        # Data memory'yi geri yükle
        self.dmem._data = snapshot['dmem']
        
        # Pipeline register'ları geri yükle
        for key, val in snapshot['pipeline_IF_ID'].items():
            setattr(self.pipeline_regs.IF_ID, key, val)
        for key, val in snapshot['pipeline_ID_EX'].items():
            setattr(self.pipeline_regs.ID_EX, key, val)
        for key, val in snapshot['pipeline_EX_MEM'].items():
            setattr(self.pipeline_regs.EX_MEM, key, val)
        for key, val in snapshot['pipeline_MEM_WB'].items():
            setattr(self.pipeline_regs.MEM_WB, key, val)
        
        # Stall/Flush sayılarını geri yükle
        self.stall_ctrl._stall_count = snapshot['stall_count']
        self.stall_ctrl._flush_count = snapshot['flush_count']
        
        # Cycle history'yi kes
        self._cycle_history = self._cycle_history[:snapshot['cycle_history_len']]
        
        return True
    
    def can_step_back(self) -> bool:
        """Geri adım atılabilir mi?"""
        return len(self._snapshots) > 0
    
    def get_statistics(self) -> Dict:
        """Simülasyon istatistiklerini döndür"""
        return {
            'cycles': self._total_cycles,
            'instructions': self._instructions_executed,
            'cpi': self._total_cycles / max(1, self._instructions_executed),
            'stalls': self.stall_ctrl.stall_count,
            'flushes': self.stall_ctrl.flush_count
        }
    
    @property
    def cycle(self) -> int:
        """Mevcut cycle sayısı"""
        return self._cycle
    
    @property
    def pc(self) -> int:
        """Program Counter"""
        return self.IF.pc
    
    @property
    def is_finished(self) -> bool:
        """Simülasyon bitti mi?"""
        return self._finished
    
    @property
    def is_running(self) -> bool:
        """Simülasyon çalışıyor mu?"""
        return self._running
    
    def get_cycle_info(self) -> Optional[CycleInfo]:
        """Son cycle bilgisini döndür"""
        if self._cycle_history:
            return self._cycle_history[-1]
        return CycleInfo()
    
    def __str__(self) -> str:
        return (
            f"RISC-16 CPU - Cycle {self._cycle}\n"
            f"PC: {format_hex(self.IF.pc)}\n"
            f"Pipeline: {self.get_pipeline_state()}\n"
            f"Stats: {self.get_statistics()}"
        )
