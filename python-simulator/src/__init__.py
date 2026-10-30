"""RISC-16 Simulator"""
from .core.cpu import CPU
from .assembler.encoder import Assembler
__version__ = "1.0.0"
__all__ = ['CPU', 'Assembler']
