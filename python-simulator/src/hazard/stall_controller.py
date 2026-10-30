"""
RISC-16 Stall Controller
Pipeline stall ve flush yönetimi
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StallSignals:
    """Pipeline stall sinyalleri"""
    pc_write: bool = True          # PC güncelleme (False = stall)
    if_id_write: bool = True       # IF/ID register yazma
    id_ex_flush: bool = False      # ID/EX register'a NOP ekle
    if_flush: bool = False         # IF stage flush (branch/jump)
    id_flush: bool = False         # ID stage flush
    
    def is_stalled(self) -> bool:
        """Herhangi bir stall var mı?"""
        return not self.pc_write or not self.if_id_write
    
    def is_flushing(self) -> bool:
        """Flush işlemi var mı?"""
        return self.if_flush or self.id_flush or self.id_ex_flush


class StallController:
    """
    Stall Controller
    
    Pipeline stall durumlarını yönetir:
    - Load-use hazard: 1 cycle stall
    - Branch/Jump: Flush (branch prediction yok, her zaman taken varsay)
    """
    
    def __init__(self):
        """Stall controller başlat"""
        self._stall_count = 0
        self._flush_count = 0
        self._current_signals = StallSignals()
        self._history = []
    
    def generate_stall_signals(self,
                                load_use_hazard: bool,
                                branch_taken: bool,
                                jump: bool) -> StallSignals:
        """
        Stall ve flush sinyallerini üret
        
        Args:
            load_use_hazard: Load-use hazard tespit edildi mi?
            branch_taken: Branch alındı mı?
            jump: Jump instruction mı?
        
        Returns:
            StallSignals objesi
        """
        signals = StallSignals()
        
        # Load-use hazard: 1 cycle stall
        if load_use_hazard:
            signals.pc_write = False      # PC'yi dondur
            signals.if_id_write = False   # IF/ID'yi dondur
            signals.id_ex_flush = True    # ID/EX'e NOP ekle (bubble)
            self._stall_count += 1
        
        # Branch taken veya Jump: Flush
        if branch_taken or jump:
            signals.if_flush = True       # IF'deki instruction'ı iptal et
            signals.id_flush = True       # ID'deki instruction'ı iptal et
            self._flush_count += 1
        
        # Geçmişe kaydet
        self._history.append({
            'load_use_hazard': load_use_hazard,
            'branch_taken': branch_taken,
            'jump': jump,
            'signals': {
                'pc_write': signals.pc_write,
                'if_id_write': signals.if_id_write,
                'id_ex_flush': signals.id_ex_flush,
                'if_flush': signals.if_flush,
                'id_flush': signals.id_flush
            }
        })
        
        self._current_signals = signals
        return signals
    
    def stall_for_load_use(self) -> StallSignals:
        """Load-use hazard için stall sinyalleri"""
        return self.generate_stall_signals(
            load_use_hazard=True,
            branch_taken=False,
            jump=False
        )
    
    def flush_for_branch(self) -> StallSignals:
        """Branch taken için flush sinyalleri"""
        return self.generate_stall_signals(
            load_use_hazard=False,
            branch_taken=True,
            jump=False
        )
    
    def flush_for_jump(self) -> StallSignals:
        """Jump için flush sinyalleri"""
        return self.generate_stall_signals(
            load_use_hazard=False,
            branch_taken=False,
            jump=True
        )
    
    def no_stall(self) -> StallSignals:
        """Normal çalışma (stall/flush yok)"""
        return self.generate_stall_signals(
            load_use_hazard=False,
            branch_taken=False,
            jump=False
        )
    
    @property
    def current_signals(self) -> StallSignals:
        """Mevcut stall sinyalleri"""
        return self._current_signals
    
    @property
    def stall_count(self) -> int:
        """Toplam stall sayısı"""
        return self._stall_count
    
    @property
    def flush_count(self) -> int:
        """Toplam flush sayısı"""
        return self._flush_count
    
    def get_statistics(self) -> dict:
        """Stall/flush istatistiklerini döndür"""
        return {
            'total_stalls': self._stall_count,
            'total_flushes': self._flush_count,
            'history_length': len(self._history)
        }
    
    def get_history(self) -> list:
        """Stall geçmişini döndür"""
        return self._history.copy()
    
    def clear_history(self):
        """Geçmişi temizle"""
        self._history.clear()
    
    def reset(self):
        """Stall controller'ı sıfırla"""
        self._stall_count = 0
        self._flush_count = 0
        self._current_signals = StallSignals()
        self._history.clear()
    
    def __str__(self) -> str:
        signals = self._current_signals
        status = []
        if not signals.pc_write:
            status.append("PC_STALL")
        if not signals.if_id_write:
            status.append("IF_ID_STALL")
        if signals.id_ex_flush:
            status.append("ID_EX_FLUSH")
        if signals.if_flush:
            status.append("IF_FLUSH")
        if signals.id_flush:
            status.append("ID_FLUSH")
        
        if status:
            return f"Stall: [{', '.join(status)}]"
        return "Stall: None"
