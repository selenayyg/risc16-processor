"""RISC-16 Label Table"""
from typing import Dict
from ..utils.exceptions import UndefinedLabelError, DuplicateLabelError

class LabelTable:
    def __init__(self):
        self._labels: Dict[str, int] = {}
    
    def define(self, name: str, address: int, line_num: int = None):
        if name in self._labels:
            raise DuplicateLabelError(name, line_num or 0)
        self._labels[name] = address
    
    def lookup(self, name: str, line_num: int = None) -> int:
        if name not in self._labels:
            raise UndefinedLabelError(name, line_num)
        return self._labels[name]
    
    def exists(self, name: str) -> bool:
        return name in self._labels
    
    def get_all(self) -> Dict[str, int]:
        return self._labels.copy()
    
    def clear(self):
        self._labels.clear()
