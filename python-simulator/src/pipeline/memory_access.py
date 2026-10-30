"""
RISC-16 Memory Access Stage (MEM)
Data Memory okuma ve yazma
"""

from ..utils.helpers import to_unsigned_16


class MemoryAccess:
    """
    Memory Access (MEM) Stage
    
    Görevler:
    - Load: Data Memory'den okuma
    - Store: Data Memory'ye yazma
    - Branch kararı (opsiyonel - bazı implementasyonlarda EX'de)
    """
    
    def __init__(self, data_memory):
        """
        MEM stage başlat
        
        Args:
            data_memory: DataMemory objesi
        """
        self.dmem = data_memory
        self._history = []
    
    def access(self,
               alu_result: int,
               rt_value: int,
               mem_read: int,
               mem_write: int) -> dict:
        """
        Memory erişimi gerçekleştir
        
        Args:
            alu_result: ALU'dan gelen adres/değer
            rt_value: Store için yazılacak değer
            mem_read: Memory okuma sinyali
            mem_write: Memory yazma sinyali
        
        Returns:
            {
                'mem_data': Memory'den okunan veri (veya 0),
                'alu_result': ALU sonucu (pass-through)
            }
        """
        mem_data = 0
        address = to_unsigned_16(alu_result)
        
        # Memory Read (LW)
        if mem_read:
            try:
                mem_data = self.dmem.load(address)
            except Exception as e:
                # Memory erişim hatası
                print(f"Memory read error at 0x{address:04X}: {e}")
                mem_data = 0
        
        # Memory Write (SW)
        if mem_write:
            try:
                self.dmem.store(address, rt_value)
            except Exception as e:
                # Memory erişim hatası
                print(f"Memory write error at 0x{address:04X}: {e}")
        
        # Sonuç
        result = {
            'mem_data': mem_data,
            'alu_result': alu_result,
            'address': address,
            'mem_read': mem_read,
            'mem_write': mem_write,
            'write_value': rt_value if mem_write else None
        }
        
        # Geçmişe kaydet
        self._history.append(result.copy())
        
        return result
    
    def load(self, address: int) -> int:
        """
        Memory'den oku
        
        Args:
            address: Memory adresi
        
        Returns:
            16-bit değer
        """
        return self.dmem.load(address)
    
    def store(self, address: int, value: int):
        """
        Memory'ye yaz
        
        Args:
            address: Memory adresi
            value: Yazılacak değer
        """
        self.dmem.store(address, value)
    
    def reset(self):
        """MEM stage'i sıfırla"""
        self._history.clear()
    
    def get_history(self) -> list:
        """Memory access geçmişini döndür"""
        return self._history.copy()
    
    def clear_history(self):
        """Geçmişi temizle"""
        self._history.clear()
    
    def __str__(self) -> str:
        if self._history:
            last = self._history[-1]
            if last['mem_read']:
                return f"MEM Stage: Read 0x{last['mem_data']:04X} from 0x{last['address']:04X}"
            elif last['mem_write']:
                return f"MEM Stage: Write 0x{last['write_value']:04X} to 0x{last['address']:04X}"
            else:
                return f"MEM Stage: Pass-through 0x{last['alu_result']:04X}"
        return "MEM Stage: Empty"
