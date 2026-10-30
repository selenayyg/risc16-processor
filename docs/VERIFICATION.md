# Verification record — 2026-10-29

## Python simulator

Command from `python-simulator/`:

`python -m pytest -q tests/test_basic.py`

Result: **4 passed, 1 failed**. `test_jal_jr` fails with `AssertionError: Failed: R3=0` (expected 8). The other four tests produce `PytestReturnNotNoneWarning` because they return `True`.

Command: `python main.py -f programs/simple_add.asm -r -m 100`

Result: completed, R1=5, R2=3, R3=8, 9 cycles.

## Verilog

No Icarus Verilog, Verilator or Vivado installation was available in the preparation environment. HDL files were preserved and organized, but compilation, synthesis and functional correctness have **not** been verified.

## Integrity

No claim is made that the legacy Verilog, reference Verilog and Python simulator share identical instruction encodings or behavior. Original project logic was not silently rewritten.
