"""
RISC-16 Forwarding Unit
Data forwarding (bypassing) logic
"""

from ..utils.constants import ForwardingSource
from ..pipeline.pipeline_registers import EX_MEM_Register, MEM_WB_Register


class ForwardingUnit:
    """
    Forwarding (Bypassing) Unit
    
    RAW hazard'ları stall olmadan çözmek için
    EX/MEM veya MEM/WB register'larından değer forward eder
    
    Forwarding öncelik sırası:
    1. EX/MEM (en güncel değer)
    2. MEM/WB
    3. Register file (normal okuma)
    """
    
    def __init__(self):
        """Forwarding unit başlat"""
        self._forward_history = []
    
    def get_forward_a(self,
                      id_ex_rs: int,
                      ex_mem: EX_MEM_Register,
                      mem_wb: MEM_WB_Register) -> tuple:
        """
        ALU A girişi için forwarding kaynağını belirle
        
        Args:
            id_ex_rs: ID/EX register'daki rs numarası
            ex_mem: EX/MEM pipeline register
            mem_wb: MEM/WB pipeline register
        
        Returns:
            (ForwardingSource, forwarded_value)
        """
        # EX/MEM forwarding (öncelikli)
        if (ex_mem.valid and 
            ex_mem.reg_write and 
            ex_mem.write_register != 0 and
            ex_mem.write_register == id_ex_rs):
            
            # EX/MEM'den forward et
            # Not: Load instruction için MEM'den okunan değer henüz yok
            # Bu durumda load-use hazard olur ve stall gerekir
            value = ex_mem.alu_result
            
            self._log_forward('A', id_ex_rs, 'EX_MEM', value)
            return (ForwardingSource.EX_MEM, value)
        
        # MEM/WB forwarding
        if (mem_wb.valid and
            mem_wb.reg_write and
            mem_wb.write_register != 0 and
            mem_wb.write_register == id_ex_rs):
            
            # MEM/WB'den forward et
            if mem_wb.mem_to_reg:
                value = mem_wb.mem_data
            else:
                value = mem_wb.alu_result
            
            self._log_forward('A', id_ex_rs, 'MEM_WB', value)
            return (ForwardingSource.MEM_WB, value)
        
        # Forwarding yok
        return (ForwardingSource.NONE, None)
    
    def get_forward_b(self,
                      id_ex_rt: int,
                      ex_mem: EX_MEM_Register,
                      mem_wb: MEM_WB_Register) -> tuple:
        """
        ALU B girişi için forwarding kaynağını belirle
        
        Args:
            id_ex_rt: ID/EX register'daki rt numarası
            ex_mem: EX/MEM pipeline register
            mem_wb: MEM/WB pipeline register
        
        Returns:
            (ForwardingSource, forwarded_value)
        """
        # EX/MEM forwarding (öncelikli)
        if (ex_mem.valid and
            ex_mem.reg_write and
            ex_mem.write_register != 0 and
            ex_mem.write_register == id_ex_rt):
            
            value = ex_mem.alu_result
            
            self._log_forward('B', id_ex_rt, 'EX_MEM', value)
            return (ForwardingSource.EX_MEM, value)
        
        # MEM/WB forwarding
        if (mem_wb.valid and
            mem_wb.reg_write and
            mem_wb.write_register != 0 and
            mem_wb.write_register == id_ex_rt):
            
            if mem_wb.mem_to_reg:
                value = mem_wb.mem_data
            else:
                value = mem_wb.alu_result
            
            self._log_forward('B', id_ex_rt, 'MEM_WB', value)
            return (ForwardingSource.MEM_WB, value)
        
        # Forwarding yok
        return (ForwardingSource.NONE, None)
    
    def get_forwarding(self,
                       id_ex_rs: int,
                       id_ex_rt: int,
                       ex_mem: EX_MEM_Register,
                       mem_wb: MEM_WB_Register) -> dict:
        """
        Her iki ALU girişi için forwarding bilgisini döndür
        
        Args:
            id_ex_rs: ID/EX register'daki rs numarası
            id_ex_rt: ID/EX register'daki rt numarası
            ex_mem: EX/MEM pipeline register
            mem_wb: MEM/WB pipeline register
        
        Returns:
            {
                'forward_a': (source, value),
                'forward_b': (source, value)
            }
        """
        forward_a = self.get_forward_a(id_ex_rs, ex_mem, mem_wb)
        forward_b = self.get_forward_b(id_ex_rt, ex_mem, mem_wb)
        
        return {
            'forward_a': forward_a,
            'forward_b': forward_b
        }
    
    def _log_forward(self, input_name: str, reg: int, source: str, value: int):
        """Forward işlemini logla"""
        self._forward_history.append({
            'input': input_name,
            'register': reg,
            'source': source,
            'value': value
        })
    
    def get_forward_history(self) -> list:
        """Forward geçmişini döndür"""
        return self._forward_history.copy()
    
    def clear_history(self):
        """Geçmişi temizle"""
        self._forward_history.clear()
    
    def reset(self):
        """Forwarding unit'i sıfırla"""
        self._forward_history.clear()
    
    def __str__(self) -> str:
        if self._forward_history:
            last = self._forward_history[-1]
            return f"Forward: {last['input']} <- R{last['register']} from {last['source']} = 0x{last['value']:04X}"
        return "Forwarding: None"


# Forwarding tablosu (debug için)
FORWARDING_TABLE = """
+------------------+------------------+--------------------+------------------+
| EX/MEM.RegWrite  | MEM/WB.RegWrite  | Condition          | Forward Source   |
+------------------+------------------+--------------------+------------------+
| 1                | X                | EX/MEM.Rd = ID/EX.Rs| EX/MEM          |
| 0                | 1                | MEM/WB.Rd = ID/EX.Rs| MEM/WB          |
| 1                | X                | EX/MEM.Rd = ID/EX.Rt| EX/MEM          |
| 0                | 1                | MEM/WB.Rd = ID/EX.Rt| MEM/WB          |
| 0                | 0                | -                  | No forwarding    |
+------------------+------------------+--------------------+------------------+

Not: EX/MEM, MEM/WB'den önceliklidir (daha güncel değer)
"""
