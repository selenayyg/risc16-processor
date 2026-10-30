"""
RISC-16 Pipeline Module
5 aşamalı pipeline bileşenleri
"""

from .pipeline_registers import (
    IF_ID_Register,
    ID_EX_Register,
    EX_MEM_Register,
    MEM_WB_Register,
    PipelineRegisters
)
from .fetch import InstructionFetch
from .decode import InstructionDecode
from .execute import Execute
from .memory_access import MemoryAccess
from .writeback import WriteBack

__all__ = [
    'IF_ID_Register',
    'ID_EX_Register', 
    'EX_MEM_Register',
    'MEM_WB_Register',
    'PipelineRegisters',
    'InstructionFetch',
    'InstructionDecode',
    'Execute',
    'MemoryAccess',
    'WriteBack'
]
