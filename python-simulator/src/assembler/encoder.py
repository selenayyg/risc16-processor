"""RISC-16 Assembler Encoder"""
from typing import List, Dict
from .parser import ParsedInstruction
from .labels import LabelTable
from ..utils.constants import Opcode, FuncCode, BYTES_PER_WORD
from ..utils.helpers import encode_r_type, encode_i_type, encode_j_type
from ..utils.exceptions import ImmediateOverflowError, AddressOverflowError

class Encoder:
    R_TYPE_FUNCS = {
        'add': FuncCode.ADD, 'sub': FuncCode.SUB, 'and': FuncCode.AND,
        'or': FuncCode.OR, 'slt': FuncCode.SLT, 'sll': FuncCode.SLL, 'srl': FuncCode.SRL,
    }
    I_TYPE_OPCODES = {
        'addi': Opcode.ADDI, 'lw': Opcode.LW, 'sw': Opcode.SW,
        'beq': Opcode.BEQ, 'bne': Opcode.BNE,
    }
    J_TYPE_OPCODES = {'j': Opcode.J, 'jal': Opcode.JAL, 'jr': Opcode.JR}
    
    def __init__(self, labels: LabelTable):
        self.labels = labels
    
    def encode_all(self, instructions: List[ParsedInstruction]) -> List[int]:
        return [self.encode(inst) for inst in instructions]
    
    def encode(self, inst: ParsedInstruction) -> int:
        mnemonic = inst.mnemonic.lower()
        if mnemonic == 'nop':
            return encode_r_type(Opcode.R_TYPE, 0, 0, 0, FuncCode.ADD)
        if mnemonic == 'halt':
            return (Opcode.HALT << 12)  # 0xF000 - special halt instruction
        if mnemonic in self.R_TYPE_FUNCS:
            return self._encode_r_type(inst)
        if mnemonic in self.I_TYPE_OPCODES:
            return self._encode_i_type(inst)
        if mnemonic in self.J_TYPE_OPCODES:
            return self._encode_j_type(inst)
        return 0
    
    def _encode_r_type(self, inst: ParsedInstruction) -> int:
        mnemonic = inst.mnemonic.lower()
        func = self.R_TYPE_FUNCS[mnemonic]
        if mnemonic in ['sll', 'srl']:
            rd, rt, shamt = inst.operands[0][1], inst.operands[1][1], inst.operands[2][1]
            if not (0 <= shamt <= 7):
                raise ImmediateOverflowError(shamt, 3, inst.line)
            return encode_r_type(Opcode.R_TYPE, 0, rt, shamt, func)
        else:
            rd, rs, rt = inst.operands[0][1], inst.operands[1][1], inst.operands[2][1]
            return encode_r_type(Opcode.R_TYPE, rs, rt, rd, func)
    
    def _encode_i_type(self, inst: ParsedInstruction) -> int:
        mnemonic = inst.mnemonic.lower()
        opcode = self.I_TYPE_OPCODES[mnemonic]
        
        if mnemonic == 'addi':
            rt, rs, imm = inst.operands[0][1], inst.operands[1][1], inst.operands[2][1]
            self._check_immediate(imm, 6, inst.line)
            return encode_i_type(opcode, rs, rt, imm)
        elif mnemonic in ['lw', 'sw']:
            rt, offset, rs = inst.operands[0][1], inst.operands[1][1], inst.operands[2][1]
            self._check_immediate(offset, 6, inst.line)
            return encode_i_type(opcode, rs, rt, offset)
        elif mnemonic in ['beq', 'bne']:
            rs, rt = inst.operands[0][1], inst.operands[1][1]
            if inst.operands[2][0] == 'label':
                target = self.labels.lookup(inst.operands[2][1], inst.line)
                offset = (target - (inst.address + BYTES_PER_WORD)) // BYTES_PER_WORD
            else:
                offset = inst.operands[2][1]
            self._check_immediate(offset, 6, inst.line)
            return encode_i_type(opcode, rs, rt, offset)
        return 0
    
    def _encode_j_type(self, inst: ParsedInstruction) -> int:
        mnemonic = inst.mnemonic.lower()
        if mnemonic == 'jr':
            rs = inst.operands[0][1]
            return encode_i_type(Opcode.JR, rs, 0, 0)
        opcode = self.J_TYPE_OPCODES[mnemonic]
        if inst.operands[0][0] == 'label':
            target = self.labels.lookup(inst.operands[0][1], inst.line)
        else:
            target = inst.operands[0][1]
        addr = target >> 1
        if not (0 <= addr <= 0xFFF):
            raise AddressOverflowError(target, 12, inst.line)
        return encode_j_type(opcode, addr)
    
    def _check_immediate(self, value: int, bits: int, line: int):
        min_val, max_val = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
        if not (min_val <= value <= max_val):
            raise ImmediateOverflowError(value, bits, line)


class Assembler:
    def __init__(self):
        self.labels = LabelTable()
        self.instructions: List[ParsedInstruction] = []
        self.machine_code: List[int] = []
    
    def assemble(self, source: str) -> List[int]:
        from .lexer import Lexer
        from .parser import Parser
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        self.instructions = parser.parse()
        self.labels = parser.labels
        
        encoder = Encoder(self.labels)
        self.machine_code = encoder.encode_all(self.instructions)
        return self.machine_code
    
    def assemble_file(self, filename: str) -> List[int]:
        with open(filename, 'r') as f:
            return self.assemble(f.read())
    
    def get_listing(self) -> str:
        lines = ["Address  Code     Assembly", "-" * 40]
        for inst, code in zip(self.instructions, self.machine_code):
            label = f"{inst.label}: " if inst.label else ""
            ops = ', '.join(str(o[1]) if o[0] != 'label' else o[1] for o in inst.operands)
            lines.append(f"0x{inst.address:04X}   0x{code:04X}   {label}{inst.mnemonic} {ops}")
        return "\n".join(lines)
    
    def get_labels(self) -> Dict[str, int]:
        return self.labels.get_all()
