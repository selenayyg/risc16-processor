#!/usr/bin/env python3
"""RISC-16 Basic Tests"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.cpu import CPU
from src.assembler.encoder import Assembler

def test_simple_add():
    print("Test: Simple Addition")
    source = """
        addi r1, r0, 5
        addi r2, r0, 3
        add  r3, r1, r2
        halt
    """
    cpu = CPU()
    cpu.load_program(Assembler().assemble(source))
    cpu.run()
    
    r1, r2, r3 = cpu.reg_file.read(1), cpu.reg_file.read(2), cpu.reg_file.read(3)
    assert r1 == 5 and r2 == 3 and r3 == 8, f"Failed: R1={r1}, R2={r2}, R3={r3}"
    print(f"  R1={r1}, R2={r2}, R3={r3} - PASSED")
    return True

def test_data_hazard():
    print("Test: Data Hazard")
    source = """
        addi r1, r0, 10
        addi r2, r1, 5
        add  r3, r1, r2
        halt
    """
    cpu = CPU()
    cpu.load_program(Assembler().assemble(source))
    cpu.run()
    
    r1, r2, r3 = cpu.reg_file.read(1), cpu.reg_file.read(2), cpu.reg_file.read(3)
    assert r1 == 10 and r2 == 15 and r3 == 25, f"Failed: R1={r1}, R2={r2}, R3={r3}"
    print(f"  R1={r1}, R2={r2}, R3={r3} - PASSED")
    return True

def test_load_store():
    print("Test: Load/Store")
    # 6-bit signed immediate: -32 to 31
    source = """
        addi r1, r0, 25
        sw   r1, 0(r0)
        lw   r2, 0(r0)
        halt
    """
    cpu = CPU()
    cpu.load_program(Assembler().assemble(source))
    cpu.run()
    
    r2 = cpu.reg_file.read(2)
    assert r2 == 25, f"Failed: R2={r2}"
    print(f"  R2={r2} - PASSED")
    return True

def test_branch():
    print("Test: Branch Loop")
    source = """
        addi r1, r0, 5
        addi r2, r0, 0
loop:   add  r2, r2, r1
        addi r1, r1, -1
        bne  r1, r0, loop
        halt
    """
    cpu = CPU()
    cpu.load_program(Assembler().assemble(source))
    cpu.run()
    
    r2 = cpu.reg_file.read(2)
    assert r2 == 15, f"Failed: R2={r2} (expected 15)"
    print(f"  R2={r2} (5+4+3+2+1=15) - PASSED")
    return True

def test_jal_jr():
    print("Test: JAL/JR")
    source = """
        addi r1, r0, 5
        addi r2, r0, 3
        jal  func
        halt
func:   add  r3, r1, r2
        jr   r7
    """
    cpu = CPU()
    cpu.load_program(Assembler().assemble(source))
    cpu.run()
    
    r3 = cpu.reg_file.read(3)
    assert r3 == 8, f"Failed: R3={r3}"
    print(f"  R3={r3} - PASSED")
    return True

if __name__ == '__main__':
    print("="*50)
    print("RISC-16 Simulator Tests")
    print("="*50)
    tests = [test_simple_add, test_data_hazard, test_load_store, test_branch, test_jal_jr]
    passed = 0
    for t in tests:
        try:
            if t():
                passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
    print(f"\nResults: {passed}/{len(tests)} passed")
