/*
 * RISC-16 Pipelined Processor - Top Module
 * 5-Stage Pipeline: IF -> ID -> EX -> MEM -> WB
 * 
 * Features:
 * - 16-bit instruction width
 * - 8 general-purpose registers (R0-R7)
 * - 512 Byte Instruction Memory (256 words)
 * - 512 Byte Data Memory (256 words)
 * - Data forwarding
 * - Hazard detection (stall + flush)
 * - All instructions: ADD, SUB, AND, OR, SLT, SLL, SRL, ADDI, LW, SW, BEQ, BNE, J, JAL, JR
 * 
 * Instruction Formats:
 * R-type: [opcode:4][rs:3][rt:3][rd:3][shamt/funct:3]
 * I-type: [opcode:4][rs:3][rt:3][imm:6]
 * J-type: [opcode:4][address:12]
 * 
 * Computer Architecture Course 2024-2025
 */

module risc16_cpu (
    input  wire        clk,
    input  wire        rst,
    output wire [15:0] pc_out,
    output wire [15:0] instruction_out,
    output wire        halted
);

    // =========================================================================
    // Wire Declarations
    // =========================================================================
    
    // PC signals
    wire [15:0] pc_current, pc_next, pc_plus2, pc_branch, pc_jump;
    
    // IF stage
    wire [15:0] if_instruction, if_pc;
    
    // IF/ID register outputs
    wire [15:0] ifid_instruction, ifid_pc;
    
    // ID stage - decoded fields
    wire [3:0]  id_opcode;
    wire [2:0]  id_rs, id_rt, id_rd, id_shamt, id_funct;
    wire [5:0]  id_imm6;
    wire [11:0] id_addr12;
    wire [15:0] id_imm_ext, id_read_data1, id_read_data2, id_jump_addr;
    
    // ID stage - control signals
    wire id_reg_write, id_mem_to_reg, id_mem_read, id_mem_write;
    wire id_alu_src, id_branch, id_branch_ne, id_jump, id_jal, id_jr, id_halt;
    wire [2:0] id_alu_op;
    wire [2:0] id_write_reg_sel;
    
    // ID/EX register outputs
    wire [15:0] idex_pc, idex_read_data1, idex_read_data2, idex_imm_ext;
    wire [2:0]  idex_rs, idex_rt, idex_rd, idex_shamt, idex_funct;
    wire [3:0]  idex_opcode;
    wire idex_reg_write, idex_mem_to_reg, idex_mem_read, idex_mem_write;
    wire idex_alu_src, idex_branch, idex_branch_ne;
    wire [2:0] idex_alu_op;
    
    // EX stage
    wire [15:0] ex_alu_result, ex_forward_a, ex_forward_b, ex_alu_b;
    wire ex_zero;
    wire [2:0] ex_write_reg;
    wire [1:0] forward_a_sel, forward_b_sel;
    
    // EX/MEM register outputs
    wire [15:0] exmem_pc, exmem_alu_result, exmem_write_data, exmem_imm_ext;
    wire [2:0]  exmem_write_reg;
    wire exmem_reg_write, exmem_mem_to_reg, exmem_mem_read, exmem_mem_write;
    wire exmem_branch, exmem_branch_ne, exmem_zero;
    
    // MEM stage
    wire [15:0] mem_read_data;
    wire mem_branch_taken;
    
    // MEM/WB register outputs
    wire [15:0] memwb_alu_result, memwb_mem_data;
    wire [2:0]  memwb_write_reg;
    wire memwb_reg_write, memwb_mem_to_reg;
    
    // WB stage
    wire [15:0] wb_write_data;
    
    // Hazard signals
    wire stall, flush, halt_reg;
    
    // =========================================================================
    // Output Assignments
    // =========================================================================
    assign pc_out = pc_current;
    assign instruction_out = if_instruction;
    assign halted = halt_reg;
    
    // =========================================================================
    // Program Counter
    // =========================================================================
    program_counter pc_unit (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .halt(halt_reg),
        .pc_next(pc_next),
        .pc_current(pc_current)
    );
    
    assign pc_plus2 = pc_current + 16'd2;
    assign pc_branch = exmem_pc + 16'd2 + {exmem_imm_ext[14:0], 1'b0};
    assign pc_jump = {ifid_pc[15:13], id_addr12, 1'b0};
    
    // Branch taken
    assign mem_branch_taken = (exmem_branch & exmem_zero) | (exmem_branch_ne & ~exmem_zero);
    
    // PC MUX
    assign pc_next = id_jr ? id_read_data1 :
                     (id_jump | id_jal) ? pc_jump :
                     mem_branch_taken ? pc_branch :
                     pc_plus2;
    
    // =========================================================================
    // IF Stage - Instruction Memory
    // =========================================================================
    instruction_memory imem (
        .addr(pc_current),
        .instruction(if_instruction)
    );
    
    assign if_pc = pc_current;
    
    // =========================================================================
    // IF/ID Pipeline Register
    // =========================================================================
    if_id_reg ifid (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .flush(flush | mem_branch_taken | id_jump | id_jal | id_jr),
        .if_pc(if_pc),
        .if_instruction(if_instruction),
        .id_pc(ifid_pc),
        .id_instruction(ifid_instruction)
    );
    
    // =========================================================================
    // ID Stage - Instruction Decode
    // =========================================================================
    assign id_opcode = ifid_instruction[15:12];
    assign id_rs     = ifid_instruction[11:9];
    assign id_rt     = ifid_instruction[8:6];
    assign id_rd     = ifid_instruction[5:3];
    assign id_shamt  = ifid_instruction[5:3];
    assign id_funct  = ifid_instruction[2:0];
    assign id_imm6   = ifid_instruction[5:0];
    assign id_addr12 = ifid_instruction[11:0];
    
    // Sign extend
    assign id_imm_ext = {{10{id_imm6[5]}}, id_imm6};
    
    // Jump address
    assign id_jump_addr = {ifid_pc[15:13], id_addr12, 1'b0};
    
    // Control Unit
    control_unit ctrl (
        .opcode(id_opcode),
        .funct(id_funct),
        .reg_write(id_reg_write),
        .mem_to_reg(id_mem_to_reg),
        .mem_read(id_mem_read),
        .mem_write(id_mem_write),
        .alu_op(id_alu_op),
        .alu_src(id_alu_src),
        .branch(id_branch),
        .branch_ne(id_branch_ne),
        .jump(id_jump),
        .jal(id_jal),
        .jr(id_jr),
        .halt(id_halt)
    );
    
    // Register File
    register_file regfile (
        .clk(clk),
        .rst(rst),
        .read_reg1(id_rs),
        .read_reg2(id_rt),
        .write_reg(memwb_write_reg),
        .write_data(wb_write_data),
        .reg_write(memwb_reg_write),
        .read_data1(id_read_data1),
        .read_data2(id_read_data2)
    );
    
    // Hazard Detection
    hazard_unit hazard (
        .idex_mem_read(idex_mem_read),
        .idex_rt(idex_rt),
        .ifid_rs(id_rs),
        .ifid_rt(id_rt),
        .stall(stall)
    );
    
    // Halt Control
    halt_control halt_ctrl (
        .clk(clk),
        .rst(rst),
        .halt_in(id_halt),
        .flush(flush | mem_branch_taken | id_jump | id_jal | id_jr),
        .halt_out(halt_reg)
    );
    
    // =========================================================================
    // ID/EX Pipeline Register
    // =========================================================================
    id_ex_reg idex (
        .clk(clk),
        .rst(rst),
        .flush(stall | flush),  // Flush on stall OR branch taken
        .id_pc(ifid_pc),
        .id_read_data1(id_read_data1),
        .id_read_data2(id_read_data2),
        .id_imm_ext(id_imm_ext),
        .id_rs(id_rs),
        .id_rt(id_rt),
        .id_rd(id_rd),
        .id_shamt(id_shamt),
        .id_funct(id_funct),
        .id_opcode(id_opcode),
        .id_reg_write(id_reg_write),
        .id_mem_to_reg(id_mem_to_reg),
        .id_mem_read(id_mem_read),
        .id_mem_write(id_mem_write),
        .id_alu_op(id_alu_op),
        .id_alu_src(id_alu_src),
        .id_branch(id_branch),
        .id_branch_ne(id_branch_ne),
        .ex_pc(idex_pc),
        .ex_read_data1(idex_read_data1),
        .ex_read_data2(idex_read_data2),
        .ex_imm_ext(idex_imm_ext),
        .ex_rs(idex_rs),
        .ex_rt(idex_rt),
        .ex_rd(idex_rd),
        .ex_shamt(idex_shamt),
        .ex_funct(idex_funct),
        .ex_opcode(idex_opcode),
        .ex_reg_write(idex_reg_write),
        .ex_mem_to_reg(idex_mem_to_reg),
        .ex_mem_read(idex_mem_read),
        .ex_mem_write(idex_mem_write),
        .ex_alu_op(idex_alu_op),
        .ex_alu_src(idex_alu_src),
        .ex_branch(idex_branch),
        .ex_branch_ne(idex_branch_ne)
    );
    
    // =========================================================================
    // EX Stage - Execute
    // =========================================================================
    
    // Forwarding Unit
    forwarding_unit fwd (
        .idex_rs(idex_rs),
        .idex_rt(idex_rt),
        .exmem_rd(exmem_write_reg),
        .memwb_rd(memwb_write_reg),
        .exmem_reg_write(exmem_reg_write),
        .memwb_reg_write(memwb_reg_write),
        .forward_a(forward_a_sel),
        .forward_b(forward_b_sel)
    );
    
    // Forwarding MUXes
    assign ex_forward_a = (forward_a_sel == 2'b10) ? exmem_alu_result :
                          (forward_a_sel == 2'b01) ? wb_write_data :
                          idex_read_data1;
    
    assign ex_forward_b = (forward_b_sel == 2'b10) ? exmem_alu_result :
                          (forward_b_sel == 2'b01) ? wb_write_data :
                          idex_read_data2;
    
    // ALU inputs
    assign ex_alu_b = idex_alu_src ? idex_imm_ext : ex_forward_b;
    
    // Write register (R-type: rd, I-type: rt)
    assign ex_write_reg = (idex_opcode == 4'b0000) ? idex_rd : idex_rt;
    
    // ALU
    alu alu_unit (
        .a(ex_forward_a),
        .b(ex_alu_b),
        .alu_op(idex_alu_op),
        .funct(idex_funct),
        .shamt(idex_shamt),
        .result(ex_alu_result),
        .zero(ex_zero)
    );
    
    // =========================================================================
    // EX/MEM Pipeline Register
    // =========================================================================
    ex_mem_reg exmem (
        .clk(clk),
        .rst(rst),
        .flush(flush),  // Flush on branch taken
        .ex_pc(idex_pc),
        .ex_alu_result(ex_alu_result),
        .ex_write_data(ex_forward_b),
        .ex_write_reg(ex_write_reg),
        .ex_zero(ex_zero),
        .ex_imm_ext(idex_imm_ext),
        .ex_reg_write(idex_reg_write),
        .ex_mem_to_reg(idex_mem_to_reg),
        .ex_mem_read(idex_mem_read),
        .ex_mem_write(idex_mem_write),
        .ex_branch(idex_branch),
        .ex_branch_ne(idex_branch_ne),
        .mem_pc(exmem_pc),
        .mem_alu_result(exmem_alu_result),
        .mem_write_data(exmem_write_data),
        .mem_write_reg(exmem_write_reg),
        .mem_zero(exmem_zero),
        .mem_imm_ext(exmem_imm_ext),
        .mem_reg_write(exmem_reg_write),
        .mem_mem_to_reg(exmem_mem_to_reg),
        .mem_mem_read(exmem_mem_read),
        .mem_mem_write(exmem_mem_write),
        .mem_branch(exmem_branch),
        .mem_branch_ne(exmem_branch_ne)
    );
    
    // =========================================================================
    // MEM Stage - Memory Access
    // =========================================================================
    data_memory dmem (
        .clk(clk),
        .addr(exmem_alu_result),
        .write_data(exmem_write_data),
        .mem_read(exmem_mem_read),
        .mem_write(exmem_mem_write),
        .read_data(mem_read_data)
    );
    
    assign flush = mem_branch_taken;
    
    // =========================================================================
    // MEM/WB Pipeline Register
    // =========================================================================
    mem_wb_reg memwb (
        .clk(clk),
        .rst(rst),
        .mem_alu_result(exmem_alu_result),
        .mem_mem_data(mem_read_data),
        .mem_write_reg(exmem_write_reg),
        .mem_reg_write(exmem_reg_write),
        .mem_mem_to_reg(exmem_mem_to_reg),
        .wb_alu_result(memwb_alu_result),
        .wb_mem_data(memwb_mem_data),
        .wb_write_reg(memwb_write_reg),
        .wb_reg_write(memwb_reg_write),
        .wb_mem_to_reg(memwb_mem_to_reg)
    );
    
    // =========================================================================
    // WB Stage - Write Back
    // =========================================================================
    assign wb_write_data = memwb_mem_to_reg ? memwb_mem_data : memwb_alu_result;

endmodule
