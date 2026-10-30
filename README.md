# RISC-16 Processor — Verilog & Python Simulator

An academic RISC-16 computer architecture project collection covering hardware description in Verilog, standalone digital logic modules, and a Python-based pipelined CPU simulator with an assembler and optional GUI.

> **Project status:** Portfolio archive / work in progress. The three components originate from different supplied archives. Their implementations and instruction encodings have **not** been established as identical or interchangeable. Do not assume the Python simulator executes the Verilog design's binaries.

## Repository map

| Folder | Description | Source archive |
|---|---|---|
| `verilog/reference-implementation/` | Alternative 16-bit pipelined CPU implementation, testbench, ISA notes, Makefile and Vivado script | `risc16-verilog (11).zip` |
| `verilog/legacy-implementation/` | Earlier/different CPU module set and testbench, preserved separately | `RISC_16PROJECT.zip` (`src.zip`) |
| `verilog/standalone-circuits/` | 16-bit ALU, one-bit full adder, their testbenches and ALU schematic | `RISC_16PROJECT.zip` |
| `python-simulator/` | Python CPU simulator, assembler, hazard/pipeline components, GUI, assembly examples and tests | `CORG.zip` (`risc16-simulator-with-back.zip`) |
| `docs/` | Provenance, verification and report privacy notes | Curated for this repository |

## Architecture overview

The provided design documents describe a 16-bit architecture with eight general-purpose registers and a five-stage pipeline (IF, ID, EX, MEM, WB). Hazard handling, control flow, and memory operations appear in the implementations. See the separate ISA documents for details: the Verilog reference in `verilog/reference-implementation/ISA_Design.md` and the Python simulator in `python-simulator/docs/ISA_design.md`. These are **implementation-specific documentation**, not proof of identical behavior.

## Run the Python simulator

Python 3 is required. From the repository root:

```bash
cd python-simulator
python main.py --help
python main.py -f programs/simple_add.asm -r
python main.py --gui
```

The GUI may require a working Tkinter installation and desktop environment. To run the provided tests, install `pytest` and execute:

```bash
python -m pytest -q tests/test_basic.py
```

**Observed on 2026-10-29:** 4 tests passed, 1 failed (`test_jal_jr`, expected R3=8, observed R3=0). The four passing tests emit warnings because they return booleans rather than using only assertions. The `simple_add.asm` CLI example completed with R3=8. See `docs/VERIFICATION.md`.

## Run the Verilog reference implementation

Install Icarus Verilog (`iverilog` and `vvp`). From `verilog/reference-implementation`:

```bash
make run
```

Or run without Make:

```bash
iverilog -o risc16_sim risc16_tb.v risc16_cpu.v program_counter.v instruction_memory.v data_memory.v register_file.v alu.v control_unit.v pipeline_regs.v hazard_unit.v
vvp risc16_sim
```

The original Vivado script is preserved for reference and assumes a particular FPGA part; review the target and toolchain before use. **Verilog compilation and simulation were not run in the preparation environment**, so hardware behavior is unverified. The legacy implementation is preserved as source, not claimed to be drop-in compatible with the reference implementation.

## Known limitations and next steps

- Investigate the Python simulator's failing JAL/JR test.
- Run Icarus Verilog simulation and inspect waveforms for both CPU variants.
- Compare instruction encodings and memory conventions before integrating simulator and RTL.
- Add automated HDL assertions and reproducible regression tests.
- Review team ownership, course policies, and third-party licensing before making the repository public.

## Attribution and provenance

This is a reorganized archive of supplied academic project files. The original source and testbench implementations were retained in separate directories rather than merged or silently replaced. The original course report lists multiple team members; obtain collaborators' consent before presenting shared work as solely individual work. See `docs/PROVENANCE.md`.

## License

No license is granted by this repository until all relevant contributors agree on one. All rights remain with their respective owners.
