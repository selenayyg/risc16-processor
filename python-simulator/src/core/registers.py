"""
RISC-16 Register File
8 adet 16-bit general purpose register (R0-R7)
"""

from ..utils.constants import NUM_REGISTERS, WORD_SIZE, REGISTER_NAMES
from ..utils.exceptions import InvalidRegisterError
from ..utils.helpers import to_unsigned_16, format_hex


class RegisterFile:
    """
    Register File sınıfı
    
    8 adet 16-bit register içerir (R0-R7)
    Not: R0 normal register olarak kullanılır (MIPS'ten farklı olarak zero register DEĞİL)
    """
    
    def __init__(self):
        """Register file'ı başlat"""
        self._registers = [0] * NUM_REGISTERS
        self._write_history = []  # Debug için yazma geçmişi
    
    def read(self, reg_num: int) -> int:
        """
        Register'dan değer oku
        
        Args:
            reg_num: Register numarası (0-7)
        
        Returns:
            16-bit register değeri
        
        Raises:
            InvalidRegisterError: Geçersiz register numarası
        """
        self._validate_register(reg_num)
        return self._registers[reg_num]
    
    def write(self, reg_num: int, value: int) -> None:
        """
        Register'a değer yaz
        
        Args:
            reg_num: Register numarası (0-7)
            value: Yazılacak 16-bit değer
        
        Raises:
            InvalidRegisterError: Geçersiz register numarası
        """
        self._validate_register(reg_num)
        
        # 16-bit'e mask'le
        value = to_unsigned_16(value)
        
        # Geçmişe kaydet (debug için)
        old_value = self._registers[reg_num]
        self._write_history.append({
            'register': reg_num,
            'old_value': old_value,
            'new_value': value
        })
        
        self._registers[reg_num] = value
    
    def _validate_register(self, reg_num: int) -> None:
        """Register numarasını doğrula"""
        if not (0 <= reg_num < NUM_REGISTERS):
            raise InvalidRegisterError(reg_num)
    
    def reset(self) -> None:
        """Tüm register'ları sıfırla"""
        self._registers = [0] * NUM_REGISTERS
        self._write_history.clear()
    
    def get_all(self) -> list:
        """
        Tüm register değerlerini döndür
        
        Returns:
            8 elemanlı liste
        """
        return self._registers.copy()
    
    def set_all(self, values: list) -> None:
        """
        Tüm register değerlerini ayarla
        
        Args:
            values: 8 elemanlı değer listesi
        """
        if len(values) != NUM_REGISTERS:
            raise ValueError(f"Expected {NUM_REGISTERS} values, got {len(values)}")
        
        for i, value in enumerate(values):
            self._registers[i] = to_unsigned_16(value)
    
    def get_write_history(self) -> list:
        """Debug için yazma geçmişini döndür"""
        return self._write_history.copy()
    
    def clear_history(self) -> None:
        """Yazma geçmişini temizle"""
        self._write_history.clear()
    
    def __str__(self) -> str:
        """Register durumunu string olarak döndür"""
        lines = ["Register File:"]
        for i in range(NUM_REGISTERS):
            name = REGISTER_NAMES[i]
            value = self._registers[i]
            lines.append(f"  {name}: {format_hex(value)} ({value})")
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"RegisterFile({self._registers})"
    
    def to_dict(self) -> dict:
        """
        Register durumunu dictionary olarak döndür
        
        Returns:
            {0: value0, 1: value1, ..., 7: value7}
        """
        return {i: self._registers[i] for i in range(NUM_REGISTERS)}
    
    def get_formatted_table(self) -> list:
        """
        GUI için formatlanmış tablo verisi
        
        Returns:
            [(name, hex_value, decimal_value, binary_value), ...]
        """
        table = []
        for i in range(NUM_REGISTERS):
            name = REGISTER_NAMES[i]
            value = self._registers[i]
            table.append((
                name,
                format_hex(value),
                str(value),
                format(value, '016b')
            ))
        return table
