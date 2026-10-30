# RISC-16 Verilog Makefile

# Verilog files
SRCS = risc16_cpu.v program_counter.v instruction_memory.v data_memory.v \
       register_file.v alu.v control_unit.v pipeline_regs.v hazard_unit.v

TB = risc16_tb.v

# Simulator
IVERILOG = iverilog
VVP = vvp
GTKWAVE = gtkwave

# Output
OUT = risc16_sim
VCD = risc16_tb.vcd

# Default target
all: compile run

# Compile
compile:
	$(IVERILOG) -o $(OUT) $(TB) $(SRCS)

# Run simulation
run: compile
	$(VVP) $(OUT)

# View waveforms
wave: run
	$(GTKWAVE) $(VCD) &

# Clean
clean:
	rm -f $(OUT) $(VCD)

# Vivado synthesis (optional)
vivado:
	vivado -mode batch -source vivado_synth.tcl

.PHONY: all compile run wave clean vivado
