"""RISC-16 Assembler Parser"""
from dataclasses import dataclass, field
from typing import List, Optional
from .lexer import Token, TokenType, parse_number
from .labels import LabelTable
from ..utils.exceptions import SyntaxError as AsmSyntaxError

@dataclass
class ParsedInstruction:
    mnemonic: str
    operands: list = field(default_factory=list)
    line: int = 0
    address: int = 0
    label: Optional[str] = None

class Parser:
    FORMATS = {
        'add': ('R', ['rd', 'rs', 'rt']), 'sub': ('R', ['rd', 'rs', 'rt']),
        'and': ('R', ['rd', 'rs', 'rt']), 'or':  ('R', ['rd', 'rs', 'rt']),
        'slt': ('R', ['rd', 'rs', 'rt']), 'sll': ('R', ['rd', 'rt', 'shamt']),
        'srl': ('R', ['rd', 'rt', 'shamt']),
        'addi': ('I', ['rt', 'rs', 'imm']),
        'lw': ('I', ['rt', 'offset(rs)']), 'sw': ('I', ['rt', 'offset(rs)']),
        'beq': ('I', ['rs', 'rt', 'label']), 'bne': ('I', ['rs', 'rt', 'label']),
        'j': ('J', ['label']), 'jal': ('J', ['label']), 'jr': ('J', ['rs']),
        'nop': ('P', []), 'halt': ('P', []),
    }
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.instructions: List[ParsedInstruction] = []
        self.labels = LabelTable()
        self.current_address = 0
    
    def parse(self) -> List[ParsedInstruction]:
        self.instructions = []; self.pos = 0; self.current_address = 0
        
        while not self._is_at_end():
            self._skip_newlines()
            if self._is_at_end(): break
            
            label = None
            if self._check(TokenType.LABEL_DEF):
                label = self._advance().value
                self.labels.define(label, self.current_address, self._current_line())
                self._skip_newlines()
                if self._is_at_end(): break
            
            if self._check(TokenType.DIRECTIVE):
                self._parse_directive(); continue
            
            if self._check(TokenType.INSTRUCTION):
                inst = self._parse_instruction()
                inst.label = label
                inst.address = self.current_address
                self.instructions.append(inst)
                self.current_address += 2
            
            self._skip_newlines()
        
        return self.instructions
    
    def _parse_instruction(self) -> ParsedInstruction:
        token = self._advance()
        mnemonic = token.value.lower()
        line = token.line
        
        if mnemonic not in self.FORMATS:
            raise AsmSyntaxError(line, mnemonic, f"Unknown instruction")
        
        fmt_type, operand_types = self.FORMATS[mnemonic]
        operands = []
        
        if fmt_type == 'P':
            return ParsedInstruction(mnemonic, [], line)
        
        for i, op_type in enumerate(operand_types):
            if i > 0: self._expect(TokenType.COMMA, "Expected ','")
            
            if op_type in ['rd', 'rs', 'rt']:
                reg = self._expect(TokenType.REGISTER, "Expected register")
                operands.append(('reg', self._parse_register(reg.value)))
            elif op_type in ['shamt', 'imm']:
                num = self._expect(TokenType.NUMBER, "Expected number")
                operands.append(('imm', parse_number(num.value)))
            elif op_type == 'label':
                if self._check(TokenType.LABEL_REF):
                    operands.append(('label', self._advance().value))
                elif self._check(TokenType.NUMBER):
                    operands.append(('imm', parse_number(self._advance().value)))
                else:
                    raise AsmSyntaxError(line, "", "Expected label or address")
            elif op_type == 'offset(rs)':
                offset = parse_number(self._advance().value) if self._check(TokenType.NUMBER) else 0
                self._expect(TokenType.LPAREN, "Expected '('")
                reg = self._expect(TokenType.REGISTER, "Expected register")
                self._expect(TokenType.RPAREN, "Expected ')'")
                operands.append(('imm', offset))
                operands.append(('reg', self._parse_register(reg.value)))
        
        return ParsedInstruction(mnemonic, operands, line)
    
    def _parse_directive(self):
        directive = self._advance().value
        if directive == '.word':
            while self._check(TokenType.NUMBER):
                self._advance(); self.current_address += 2
                if not self._check(TokenType.COMMA): break
                self._advance()
    
    def _parse_register(self, reg_str: str) -> int:
        reg_str = reg_str.lower()
        if reg_str in ['zero', 'r0']: return 0
        if reg_str == 'ra': return 7
        if reg_str.startswith('r') and reg_str[1:].isdigit(): return int(reg_str[1:])
        return 0
    
    def _advance(self) -> Token:
        if not self._is_at_end():
            token = self.tokens[self.pos]; self.pos += 1; return token
        return self.tokens[-1]
    
    def _check(self, token_type: TokenType) -> bool:
        return not self._is_at_end() and self.tokens[self.pos].type == token_type
    
    def _expect(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type): return self._advance()
        current = self.tokens[self.pos] if not self._is_at_end() else self.tokens[-1]
        raise AsmSyntaxError(current.line, current.value, message)
    
    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE): self._advance()
    
    def _is_at_end(self) -> bool:
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF
    
    def _current_line(self) -> int:
        return self.tokens[self.pos].line if self.pos < len(self.tokens) else 0
