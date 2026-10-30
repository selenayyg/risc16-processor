# Vivado Synthesis Script for RISC-16 Processor
# Run with: vivado -mode batch -source vivado_synth.tcl

# Create project
create_project risc16_project ./vivado_project -part xc7a35tcpg236-1 -force

# Add source files
add_files -norecurse {
    risc16_cpu.v
    program_counter.v
    instruction_memory.v
    data_memory.v
    register_file.v
    alu.v
    control_unit.v
    pipeline_regs.v
    hazard_unit.v
}

# Add testbench
add_files -fileset sim_1 -norecurse risc16_tb.v

# Set top module
set_property top risc16_cpu [current_fileset]
set_property top risc16_tb [get_filesets sim_1]

# Update compile order
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

# Run synthesis
launch_runs synth_1
wait_on_run synth_1

# Generate utilization report
open_run synth_1
report_utilization -file utilization_report.txt
report_timing_summary -file timing_report.txt

puts "Synthesis complete!"
puts "Check utilization_report.txt and timing_report.txt"
