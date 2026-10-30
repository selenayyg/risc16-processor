# Archive comparison and decisions

- `RISC_16PROJECT.zip`: standalone ALU and full adder source/testbenches, a separate 9-module CPU under nested `src.zip`, CPU testbench, and generated simulation artifacts. Source and schematic retained; generated binary outputs, tool caches, `.bak` files and redundant nested ZIPs omitted.
- `risc16-verilog (11).zip`: another 9-module CPU RTL design, its testbench, Makefile, ISA design document and Vivado script. Retained together as the **reference implementation** (a directory label, not a claim that it is newer or correct).
- `CORG.zip`: `risc16-simulator-with-back.zip` contains a Python simulator, assembler, GUI, assembly programs and tests. Retained; Python caches omitted. `raporson.pdf` excluded from the public-ready copy because it contains contributor names and student identifiers.

**Version uncertainty:** No reliable creation history, Git commit metadata or authoritative assignment rubric was supplied. The latest or canonical Verilog implementation cannot be established from filenames alone. The two RTL versions are therefore preserved independently.

**Ownership:** The supplied report identifies multiple contributors. Confirm team consent, institutional rules and rights before publishing this repository publicly.
