"""
RISC-16 Memory System
Instruction Memory (ROM) ve Data Memory (RAM)
"""

from ..utils.constants import (
    INSTRUCTION_MEMORY_SIZE, DATA_MEMORY_SIZE,
    WORD_SIZE, BYTES_PER_WORD
)
from ..utils.exceptions import MemoryAccessError, MemoryAlignmentError
from ..utils.helpers import to_unsigned_16, format_hex


class Memory:
    """
    Temel Memory sınıfı
    Byte-addressable, word-aligned erişim
    """
    
    def __init__(self, size: int, name: str = "Memory"):
        """
        Memory başlat
        
        Args:
            size: Memory boyutu (byte)
            name: Memory ismi (debug için)
        """
        self.size = size
        self.name = name
        self._data = bytearray(size)
        self._access_history = []  # Debug için erişim geçmişi
    
    def read_byte(self, address: int) -> int:
        """
        Tek byte oku
        
        Args:
            address: Byte adresi
        
        Returns:
            8-bit değer
        """
        self._validate_address(address, 1)
        return self._data[address]
    
    def write_byte(self, address: int, value: int) -> None:
        """
        Tek byte yaz
        
        Args:
            address: Byte adresi
            value: 8-bit değer
        """
        self._validate_address(address, 1)
        self._data[address] = value & 0xFF
    
    def read_word(self, address: int) -> int:
        """
        16-bit word oku (Big Endian)
        
        Args:
            address: Word adresi (2'nin katı olmalı)
        
        Returns:
            16-bit değer
        """
        self._validate_address(address, BYTES_PER_WORD)
        self._validate_alignment(address)
        
        # Big Endian: MSB önce
        high = self._data[address]
        low = self._data[address + 1]
        value = (high << 8) | low
        
        # Geçmişe kaydet
        self._access_history.append({
            'type': 'read',
            'address': address,
            'value': value
        })
        
        return value
    
    def write_word(self, address: int, value: int) -> None:
        """
        16-bit word yaz (Big Endian)
        
        Args:
            address: Word adresi (2'nin katı olmalı)
            value: 16-bit değer
        """
        self._validate_address(address, BYTES_PER_WORD)
        self._validate_alignment(address)
        
        value = to_unsigned_16(value)
        
        # Geçmişe kaydet
        old_value = self.read_word(address) if address < self.size - 1 else 0
        self._access_history.append({
            'type': 'write',
            'address': address,
            'old_value': old_value,
            'new_value': value
        })
        
        # Big Endian: MSB önce
        self._data[address] = (value >> 8) & 0xFF
        self._data[address + 1] = value & 0xFF
    
    def _validate_address(self, address: int, size: int) -> None:
        """Adres geçerliliğini kontrol et"""
        if address < 0 or address + size > self.size:
            raise MemoryAccessError(address, self.name)
    
    def _validate_alignment(self, address: int) -> None:
        """Word alignment kontrolü"""
        if address % BYTES_PER_WORD != 0:
            raise MemoryAlignmentError(address)
    
    def reset(self) -> None:
        """Memory'yi sıfırla"""
        self._data = bytearray(self.size)
        self._access_history.clear()
    
    def load_data(self, data: bytes, start_address: int = 0) -> None:
        """
        Binary data yükle
        
        Args:
            data: Yüklenecek byte dizisi
            start_address: Başlangıç adresi
        """
        end_address = start_address + len(data)
        if end_address > self.size:
            raise MemoryAccessError(end_address - 1, self.name)
        
        for i, byte in enumerate(data):
            self._data[start_address + i] = byte
    
    def load_words(self, words: list, start_address: int = 0) -> None:
        """
        Word listesi yükle
        
        Args:
            words: 16-bit değer listesi
            start_address: Başlangıç adresi
        """
        for i, word in enumerate(words):
            address = start_address + (i * BYTES_PER_WORD)
            self.write_word(address, word)
    
    def get_range(self, start: int, end: int) -> list:
        """
        Belirli aralıktaki word'leri döndür
        
        Args:
            start: Başlangıç adresi
            end: Bitiş adresi
        
        Returns:
            Word listesi
        """
        words = []
        for addr in range(start, end, BYTES_PER_WORD):
            try:
                words.append(self.read_word(addr))
            except (MemoryAccessError, MemoryAlignmentError):
                break
        return words
    
    def get_access_history(self) -> list:
        """Erişim geçmişini döndür"""
        return self._access_history.copy()
    
    def clear_history(self) -> None:
        """Erişim geçmişini temizle"""
        self._access_history.clear()
    
    def __str__(self) -> str:
        """Memory durumunu string olarak döndür"""
        lines = [f"{self.name} ({self.size} bytes):"]
        
        # Non-zero değerleri göster
        for addr in range(0, self.size, BYTES_PER_WORD):
            value = self.read_word(addr)
            if value != 0:
                lines.append(f"  [{format_hex(addr)}]: {format_hex(value)}")
        
        if len(lines) == 1:
            lines.append("  (empty)")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Memory içeriğini dictionary olarak döndür"""
        result = {}
        for addr in range(0, self.size, BYTES_PER_WORD):
            value = self.read_word(addr)
            if value != 0:
                result[addr] = value
        return result
    
    def get_formatted_table(self, start: int = 0, count: int = 16) -> list:
        """
        GUI için formatlanmış tablo verisi
        
        Args:
            start: Başlangıç adresi
            count: Gösterilecek word sayısı
        
        Returns:
            [(address, hex_value, decimal_value), ...]
        """
        table = []
        for i in range(count):
            addr = start + (i * BYTES_PER_WORD)
            if addr >= self.size:
                break
            value = self.read_word(addr)
            table.append((
                format_hex(addr),
                format_hex(value),
                str(value)
            ))
        return table


class InstructionMemory(Memory):
    """
    Instruction Memory (ROM)
    512 Byte, read-only during execution
    """
    
    def __init__(self):
        super().__init__(INSTRUCTION_MEMORY_SIZE, "Instruction Memory")
    
    def fetch(self, pc: int) -> int:
        """
        PC adresinden instruction fetch et
        
        Args:
            pc: Program Counter değeri
        
        Returns:
            16-bit instruction
        """
        return self.read_word(pc)
    
    def load_program(self, instructions: list) -> None:
        """
        Program yükle (instruction listesi)
        
        Args:
            instructions: 16-bit instruction listesi
        """
        self.reset()
        self.load_words(instructions)
    
    def get_program_size(self) -> int:
        """Yüklü programın boyutunu döndür (word sayısı)"""
        # Son non-zero instruction'ı bul
        for addr in range(self.size - BYTES_PER_WORD, -1, -BYTES_PER_WORD):
            if self.read_word(addr) != 0:
                return (addr // BYTES_PER_WORD) + 1
        return 0


class DataMemory(Memory):
    """
    Data Memory (RAM)
    512 Byte, read-write
    """
    
    def __init__(self):
        super().__init__(DATA_MEMORY_SIZE, "Data Memory")
    
    def load(self, address: int) -> int:
        """
        LW instruction için memory'den oku
        
        Args:
            address: Memory adresi
        
        Returns:
            16-bit değer
        """
        return self.read_word(address)
    
    def store(self, address: int, value: int) -> None:
        """
        SW instruction için memory'ye yaz
        
        Args:
            address: Memory adresi
            value: 16-bit değer
        """
        self.write_word(address, value)
