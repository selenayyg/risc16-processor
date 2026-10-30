"""
RISC-16 Write Back Stage (WB)
Register file'a sonuç yazma
"""


class WriteBack:
    """
    Write Back (WB) Stage
    
    Görevler:
    - ALU sonucunu veya memory verisini register'a yazma
    - Write register seçimi
    """
    
    def __init__(self, register_file):
        """
        WB stage başlat
        
        Args:
            register_file: RegisterFile objesi
        """
        self.reg_file = register_file
        self._history = []
    
    def writeback(self,
                  mem_data: int,
                  alu_result: int,
                  write_register: int,
                  mem_to_reg: int,
                  reg_write: int) -> dict:
        """
        Register'a geri yazma
        
        Args:
            mem_data: Memory'den okunan veri
            alu_result: ALU sonucu
            write_register: Yazılacak register numarası
            mem_to_reg: Veri kaynağı seçimi (0: ALU, 1: Memory)
            reg_write: Register yazma aktif mi?
        
        Returns:
            {
                'write_data': Yazılan veri,
                'write_register': Yazılan register,
                'written': Yazma yapıldı mı?
            }
        """
        # Yazılacak veriyi seç
        if mem_to_reg:
            write_data = mem_data
        else:
            write_data = alu_result
        
        # Register'a yaz
        written = False
        if reg_write and write_register is not None:
            self.reg_file.write(write_register, write_data)
            written = True
        
        # Sonuç
        result = {
            'write_data': write_data,
            'write_register': write_register,
            'written': written,
            'mem_to_reg': mem_to_reg,
            'reg_write': reg_write
        }
        
        # Geçmişe kaydet
        self._history.append(result.copy())
        
        return result
    
    def get_write_data(self, mem_data: int, alu_result: int, mem_to_reg: int) -> int:
        """
        Yazılacak veriyi hesapla (forwarding için)
        
        Args:
            mem_data: Memory'den okunan veri
            alu_result: ALU sonucu
            mem_to_reg: Veri kaynağı seçimi
        
        Returns:
            Yazılacak veri
        """
        return mem_data if mem_to_reg else alu_result
    
    def reset(self):
        """WB stage'i sıfırla"""
        self._history.clear()
    
    def get_history(self) -> list:
        """Writeback geçmişini döndür"""
        return self._history.copy()
    
    def clear_history(self):
        """Geçmişi temizle"""
        self._history.clear()
    
    def __str__(self) -> str:
        if self._history:
            last = self._history[-1]
            if last['written']:
                return f"WB Stage: R{last['write_register']} <- 0x{last['write_data']:04X}"
            else:
                return "WB Stage: No write"
        return "WB Stage: Empty"
