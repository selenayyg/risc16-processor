"""RISC-16 Assembler Lexer"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import List

class TokenType(Enum):
    INSTRUCTION = auto()
    REGISTER = auto()
    NUMBER = auto()
    LABEL_DEF = auto()
    LABEL_REF = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    NEWLINE = auto()
    DIRECTIVE = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

INSTRUCTIONS = {'add','sub','and','or','slt','sll','srl','addi','lw','sw','beq','bne','j','jal','jr','nop','halt'}
REGISTERS = {'r0','r1','r2','r3','r4','r5','r6','r7','zero','ra'}

def parse_number(value: str) -> int:
    value = value.strip()
    if value.lower().startswith('0x'): return int(value, 16)
    if value.lower().startswith('0b'): return int(value, 2)
    return int(value)

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        self.tokens = []
        self.pos = 0
        self.line = 1
        self.column = 1
        
        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source): break
            
            char = self.source[self.pos]
            
            if char in '#;': self._skip_comment()
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.pos += 1; self.line += 1; self.column = 1
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self.pos += 1; self.column += 1
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, self.column))
                self.pos += 1; self.column += 1
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, self.column))
                self.pos += 1; self.column += 1
            elif char == '.': self._read_directive()
            elif char.isdigit() or (char == '-' and self.pos + 1 < len(self.source) and self.source[self.pos+1].isdigit()):
                self._read_number()
            elif char.isalpha() or char == '_': self._read_identifier()
            else: self.pos += 1; self.column += 1
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def _skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r':
            self.pos += 1; self.column += 1
    
    def _skip_comment(self):
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.pos += 1
    
    def _read_directive(self):
        start = self.column
        directive = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '.'):
            directive += self.source[self.pos]; self.pos += 1; self.column += 1
        self.tokens.append(Token(TokenType.DIRECTIVE, directive.lower(), self.line, start))
    
    def _read_number(self):
        start = self.column
        number = ''
        if self.source[self.pos] == '-':
            number += self.source[self.pos]; self.pos += 1; self.column += 1
        if self.pos + 1 < len(self.source) and self.source[self.pos] == '0' and self.source[self.pos+1].lower() in 'xb':
            number += self.source[self.pos:self.pos+2]; self.pos += 2; self.column += 2
            while self.pos < len(self.source) and self.source[self.pos] in '0123456789abcdefABCDEF':
                number += self.source[self.pos]; self.pos += 1; self.column += 1
        else:
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                number += self.source[self.pos]; self.pos += 1; self.column += 1
        self.tokens.append(Token(TokenType.NUMBER, number, self.line, start))
    
    def _read_identifier(self):
        start = self.column
        ident = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            ident += self.source[self.pos]; self.pos += 1; self.column += 1
        
        lower = ident.lower()
        if self.pos < len(self.source) and self.source[self.pos] == ':':
            self.pos += 1; self.column += 1
            self.tokens.append(Token(TokenType.LABEL_DEF, ident, self.line, start))
        elif lower in INSTRUCTIONS:
            self.tokens.append(Token(TokenType.INSTRUCTION, lower, self.line, start))
        elif lower in REGISTERS:
            self.tokens.append(Token(TokenType.REGISTER, lower, self.line, start))
        else:
            self.tokens.append(Token(TokenType.LABEL_REF, ident, self.line, start))
