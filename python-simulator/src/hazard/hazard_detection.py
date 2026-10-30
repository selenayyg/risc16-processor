"""
RISC-16 Hazard Detection Unit
Data hazard ve control hazard tespiti
"""

from ..utils.constants import HazardType, Opcode
from ..pipeline.pipeline_registers import ID_EX_Register, EX_MEM_Register


class HazardDetectionUnit:
    """
    Hazard Detection Unit
    
    Data Hazards:
    - RAW (Read After Write): Önceki instruction'ın sonucu henüz yazılmamış
    - Load-Use: LW'den hemen sonra değeri kullanma (stall gerektirir)
    
    Control Hazards:
    - Branch: Branch kararı belli olana kadar
    - Jump: Jump hedefi hesaplanana kadar
    """
    
    def __init__(self):
        """Hazard detection unit başlat"""
        self._detected_hazards = []
        self._history = []
    
    def detect_load_use_hazard(self,
                                id_ex: ID_EX_Register,
                                if_id_rs: int,
                                if_id_rt: int,
                                if_id_uses_rs: bool,
                                if_id_uses_rt: bool) -> bool:
        """
        Load-use hazard tespit et
        
        LW instruction'dan hemen sonra değerini kullanan instruction
        Bu durumda stall gerekir (forwarding yetersiz)
        
        Args:
            id_ex: ID/EX pipeline register
            if_id_rs: IF/ID'deki instruction'ın rs'i
            if_id_rt: IF/ID'deki instruction'ın rt'si
            if_id_uses_rs: IF/ID instruction rs kullanıyor mu?
            if_id_uses_rt: IF/ID instruction rt kullanıyor mu?
        
        Returns:
            True: Load-use hazard var (stall gerekli)
            False: Hazard yok
        """
        # ID/EX'deki instruction LW mi?
        if not id_ex.valid or not id_ex.mem_read:
            return False
        
        # ID/EX'in write register'ı
        write_reg = id_ex.get_write_register()
        
        # IF/ID'deki instruction bu register'ı okuyor mu?
        hazard = False
        
        if if_id_uses_rs and write_reg == if_id_rs:
            hazard = True
        
        if if_id_uses_rt and write_reg == if_id_rt:
            hazard = True
        
        if hazard:
            self._detected_hazards.append({
                'type': HazardType.LOAD_USE,
                'producer_reg': write_reg,
                'consumer_rs': if_id_rs if if_id_uses_rs else None,
                'consumer_rt': if_id_rt if if_id_uses_rt else None
            })
        
        return hazard
    
    def detect_data_hazard(self,
                           id_ex: ID_EX_Register,
                           ex_mem: EX_MEM_Register,
                           if_id_rs: int,
                           if_id_rt: int) -> dict:
        """
        Data hazard tespit et (forwarding ile çözülebilir olanlar)
        
        Args:
            id_ex: ID/EX pipeline register
            ex_mem: EX/MEM pipeline register
            if_id_rs: IF/ID'deki instruction'ın rs'i
            if_id_rt: IF/ID'deki instruction'ın rt'si
        
        Returns:
            {
                'rs_hazard': HazardType,
                'rt_hazard': HazardType,
                'rs_forward_from': 'EX_MEM' | 'MEM_WB' | None,
                'rt_forward_from': 'EX_MEM' | 'MEM_WB' | None
            }
        """
        result = {
            'rs_hazard': HazardType.NONE,
            'rt_hazard': HazardType.NONE,
            'rs_forward_from': None,
            'rt_forward_from': None
        }
        
        # EX/MEM hazard kontrolü (daha öncelikli)
        if ex_mem.valid and ex_mem.reg_write:
            ex_mem_write_reg = ex_mem.write_register
            
            if if_id_rs == ex_mem_write_reg and ex_mem_write_reg != 0:
                result['rs_hazard'] = HazardType.RAW
                result['rs_forward_from'] = 'EX_MEM'
            
            if if_id_rt == ex_mem_write_reg and ex_mem_write_reg != 0:
                result['rt_hazard'] = HazardType.RAW
                result['rt_forward_from'] = 'EX_MEM'
        
        # ID/EX hazard kontrolü (EX/MEM'de yoksa)
        if id_ex.valid and id_ex.reg_write:
            id_ex_write_reg = id_ex.get_write_register()
            
            if result['rs_hazard'] == HazardType.NONE:
                if if_id_rs == id_ex_write_reg and id_ex_write_reg != 0:
                    # Load-use hazard ayrı kontrol ediliyor
                    if not id_ex.mem_read:
                        result['rs_hazard'] = HazardType.RAW
                        result['rs_forward_from'] = 'ID_EX'
            
            if result['rt_hazard'] == HazardType.NONE:
                if if_id_rt == id_ex_write_reg and id_ex_write_reg != 0:
                    if not id_ex.mem_read:
                        result['rt_hazard'] = HazardType.RAW
                        result['rt_forward_from'] = 'ID_EX'
        
        return result
    
    def detect_control_hazard(self, opcode: int) -> bool:
        """
        Control hazard tespit et
        
        Args:
            opcode: Instruction opcode
        
        Returns:
            True: Control hazard var (branch/jump)
        """
        is_branch = opcode in [Opcode.BEQ, Opcode.BNE]
        is_jump = opcode in [Opcode.J, Opcode.JAL, Opcode.JR]
        
        if is_branch or is_jump:
            self._detected_hazards.append({
                'type': HazardType.CONTROL,
                'is_branch': is_branch,
                'is_jump': is_jump
            })
            return True
        
        return False
    
    def should_stall(self,
                     id_ex: ID_EX_Register,
                     if_id_rs: int,
                     if_id_rt: int,
                     if_id_uses_rs: bool,
                     if_id_uses_rt: bool) -> bool:
        """
        Pipeline stall gerekiyor mu?
        
        Args:
            id_ex: ID/EX pipeline register
            if_id_rs: IF/ID'deki instruction'ın rs'i
            if_id_rt: IF/ID'deki instruction'ın rt'si
            if_id_uses_rs: IF/ID instruction rs kullanıyor mu?
            if_id_uses_rt: IF/ID instruction rt kullanıyor mu?
        
        Returns:
            True: Stall gerekli
        """
        return self.detect_load_use_hazard(
            id_ex, if_id_rs, if_id_rt, if_id_uses_rs, if_id_uses_rt
        )
    
    def get_detected_hazards(self) -> list:
        """Tespit edilen hazard'ları döndür"""
        return self._detected_hazards.copy()
    
    def clear_hazards(self):
        """Hazard listesini temizle"""
        self._detected_hazards.clear()
    
    def reset(self):
        """Hazard detection unit'i sıfırla"""
        self._detected_hazards.clear()
        self._history.clear()
    
    def __str__(self) -> str:
        if self._detected_hazards:
            hazards = [h['type'] for h in self._detected_hazards]
            return f"Hazards: {hazards}"
        return "Hazards: None"
