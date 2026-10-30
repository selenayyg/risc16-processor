//=============================================================================
// RISC-16 Processor - Top Module
// 16-bit, 5-Stage Pipeline with Hazard Detection and Forwarding
//=============================================================================

module risc16_cpu (
    input  wire        clk,
    input  wire        rst,
    output wire [15:0] pc_out,
    output wire [15:0] alu_result_out,
    output wire        halted
);

    //=========================================================================
    // Wire Declarations
    //=========================================================================
    
    // IF Stage
    wire [15:0] pc_current;
    wire [15:0] pc_plus_2;
    wire [15:0] pc_next;
    wire [15:0] instruction;
    wire        pc_write;
    wire        if_id_write;
    wire        if_flush;
    
    // IF/ID Pipeline Register Outputs
    wire [15:0] if_id_pc;
    wire [15:0] if_id_instruction;
    
    // ID Stage
    wire [3:0]  opcode;
    wire [2:0]  rs, rt, rd;
    wire [2:0]  funct;
    wire [5:0]  imm6;
    wire [11:0] addr12;
    wire [15:0] read_data1, read_data2;
    wire [15:0] sign_extended;
    wire [15:0] jump_addr;
    
    // Control Signals
    wire        reg_dst;
    wire        alu_src;
    wire        mem_to_reg;
    wire        reg_write;
    wire        mem_read;
    wire        mem_write;
    wire        branch_eq;
    wire        branch_neq;
    wire        jump;
    wire        jal;
    wire        jr;
    wire [1:0]  alu_op;
    wire        halt;
    
    // ID/EX Pipeline Register Outputs
    wire [15:0] id_ex_pc;
    wire [15:0] id_ex_read_data1;
    wire [15:0] id_ex_read_data2;
    wire [15:0] id_ex_sign_extended;
    wire [2:0]  id_ex_rs, id_ex_rt, id_ex_rd;
    wire [2:0]  id_ex_funct;
    wire        id_ex_reg_dst;
    wire        id_ex_alu_src;
    wire        id_ex_mem_to_reg;
    wire        id_ex_reg_write;
    wire        id_ex_mem_read;
    wire        id_ex_mem_write;
    wire        id_ex_branch_eq;
    wire        id_ex_branch_neq;
    wire [1:0]  id_ex_alu_op;
    wire        id_ex_halt;
    
    // EX Stage
    wire [15:0] alu_input_a;
    wire [15:0] alu_input_b;
    wire [15:0] alu_src_mux_out;
    wire [15:0] alu_result;
    wire        alu_zero;
    wire [3:0]  alu_control;
    wire [2:0]  write_reg_addr;
    wire [15:0] branch_target;
    wire        branch_taken;
    wire [1:0]  forward_a, forward_b;
    wire [15:0] forward_a_data, forward_b_data;
    
    // EX/MEM Pipeline Register Outputs
    wire [15:0] ex_mem_pc;
    wire [15:0] ex_mem_alu_result;
    wire [15:0] ex_mem_read_data2;
    wire [2:0]  ex_mem_write_reg;
    wire        ex_mem_zero;
    wire        ex_mem_mem_to_reg;
    wire        ex_mem_reg_write;
    wire        ex_mem_mem_read;
    wire        ex_mem_mem_write;
    wire        ex_mem_branch_eq;
    wire        ex_mem_branch_neq;
    wire [15:0] ex_mem_branch_target;
    wire        ex_mem_halt;
    
    // MEM Stage
    wire [15:0] mem_read_data;
    wire        pc_src;
    
    // MEM/WB Pipeline Register Outputs
    wire [15:0] mem_wb_alu_result;
    wire [15:0] mem_wb_mem_data;
    wire [2:0]  mem_wb_write_reg;
    wire        mem_wb_mem_to_reg;
    wire        mem_wb_reg_write;
    wire        mem_wb_halt;
    
    // WB Stage
    wire [15:0] write_back_data;
    
    // Hazard Detection
    wire        stall;
    wire        id_flush;
    
    //=========================================================================
    // Instruction Field Extraction
    //=========================================================================
    assign opcode = if_id_instruction[15:12];
    assign rs     = if_id_instruction[11:9];
    assign rt     = if_id_instruction[8:6];
    assign rd     = if_id_instruction[5:3];
    assign funct  = if_id_instruction[2:0];
    assign imm6   = if_id_instruction[5:0];
    assign addr12 = if_id_instruction[11:0];
    
    //=========================================================================
    // IF Stage - Instruction Fetch
    //=========================================================================
    
    // PC Register
    pc_register pc_reg (
        .clk(clk),
        .rst(rst),
        .pc_write(pc_write),
        .pc_in(pc_next),
        .pc_out(pc_current)
    );
    
    // PC + 2
    assign pc_plus_2 = pc_current + 16'd2;
    
    // PC Next MUX (Branch/Jump/Normal)
    pc_mux pc_next_mux (
        .pc_plus_2(pc_plus_2),
        .branch_target(ex_mem_branch_target),
        .jump_target(jump_addr),
        .jr_target(read_data1),
        .pc_src(pc_src),
        .jump(jump),
        .jr(jr),
        .pc_next(pc_next)
    );
    
    // Instruction Memory
    instruction_memory imem (
        .addr(pc_current),
        .instruction(instruction)
    );
    
    // IF/ID Pipeline Register
    if_id_register if_id_reg (
        .clk(clk),
        .rst(rst),
        .if_id_write(if_id_write),
        .if_flush(if_flush | pc_src),
        .pc_in(pc_plus_2),
        .instruction_in(instruction),
        .pc_out(if_id_pc),
        .instruction_out(if_id_instruction)
    );
    
    //=========================================================================
    // ID Stage - Instruction Decode
    //=========================================================================
    
    // Control Unit
    control_unit ctrl (
        .opcode(opcode),
        .funct(funct),
        .reg_dst(reg_dst),
        .alu_src(alu_src),
        .mem_to_reg(mem_to_reg),
        .reg_write(reg_write),
        .mem_read(mem_read),
        .mem_write(mem_write),
        .branch_eq(branch_eq),
        .branch_neq(branch_neq),
        .jump(jump),
        .jal(jal),
        .jr(jr),
        .alu_op(alu_op),
        .halt(halt)
    );
    
    // Register File
    register_file reg_file (
        .clk(clk),
        .rst(rst),
        .read_reg1(rs),
        .read_reg2(rt),
        .write_reg(mem_wb_write_reg),
        .write_data(write_back_data),
        .reg_write(mem_wb_reg_write),
        .read_data1(read_data1),
        .read_data2(read_data2)
    );
    
    // Sign Extend (6-bit to 16-bit)
    sign_extend sign_ext (
        .in(imm6),
        .out(sign_extended)
    );
    
    // Jump Address Calculation
    assign jump_addr = {if_id_pc[15:12], addr12};
    
    // Hazard Detection Unit
    hazard_detection_unit hdu (
        .id_ex_mem_read(id_ex_mem_read),
        .id_ex_rt(id_ex_rt),
        .if_id_rs(rs),
        .if_id_rt(rt),
        .branch_eq(branch_eq),
        .branch_neq(branch_neq),
        .jump(jump),
        .jr(jr),
        .pc_write(pc_write),
        .if_id_write(if_id_write),
        .stall(stall),
        .if_flush(if_flush)
    );
    
    // ID/EX Pipeline Register
    id_ex_register id_ex_reg (
        .clk(clk),
        .rst(rst),
        .flush(stall | id_flush | pc_src),
        .pc_in(if_id_pc),
        .read_data1_in(read_data1),
        .read_data2_in(read_data2),
        .sign_extended_in(sign_extended),
        .rs_in(rs),
        .rt_in(rt),
        .rd_in(rd),
        .funct_in(funct),
        .reg_dst_in(reg_dst),
        .alu_src_in(alu_src),
        .mem_to_reg_in(mem_to_reg),
        .reg_write_in(reg_write),
        .mem_read_in(mem_read),
        .mem_write_in(mem_write),
        .branch_eq_in(branch_eq),
        .branch_neq_in(branch_neq),
        .alu_op_in(alu_op),
        .halt_in(halt),
        // Outputs
        .pc_out(id_ex_pc),
        .read_data1_out(id_ex_read_data1),
        .read_data2_out(id_ex_read_data2),
        .sign_extended_out(id_ex_sign_extended),
        .rs_out(id_ex_rs),
        .rt_out(id_ex_rt),
        .rd_out(id_ex_rd),
        .funct_out(id_ex_funct),
        .reg_dst_out(id_ex_reg_dst),
        .alu_src_out(id_ex_alu_src),
        .mem_to_reg_out(id_ex_mem_to_reg),
        .reg_write_out(id_ex_reg_write),
        .mem_read_out(id_ex_mem_read),
        .mem_write_out(id_ex_mem_write),
        .branch_eq_out(id_ex_branch_eq),
        .branch_neq_out(id_ex_branch_neq),
        .alu_op_out(id_ex_alu_op),
        .halt_out(id_ex_halt)
    );
    
    //=========================================================================
    // EX Stage - Execute
    //=========================================================================
    
    // Forwarding Unit
    forwarding_unit fwd_unit (
        .id_ex_rs(id_ex_rs),
        .id_ex_rt(id_ex_rt),
        .ex_mem_rd(ex_mem_write_reg),
        .mem_wb_rd(mem_wb_write_reg),
        .ex_mem_reg_write(ex_mem_reg_write),
        .mem_wb_reg_write(mem_wb_reg_write),
        .forward_a(forward_a),
        .forward_b(forward_b)
    );
    
    // Forwarding MUX A
    mux4to1 #(16) fwd_mux_a (
        .in0(id_ex_read_data1),
        .in1(write_back_data),
        .in2(ex_mem_alu_result),
        .in3(16'b0),
        .sel(forward_a),
        .out(forward_a_data)
    );
    
    // Forwarding MUX B
    mux4to1 #(16) fwd_mux_b (
        .in0(id_ex_read_data2),
        .in1(write_back_data),
        .in2(ex_mem_alu_result),
        .in3(16'b0),
        .sel(forward_b),
        .out(forward_b_data)
    );
    
    // ALU Source MUX
    assign alu_input_a = forward_a_data;
    assign alu_src_mux_out = id_ex_alu_src ? id_ex_sign_extended : forward_b_data;
    assign alu_input_b = alu_src_mux_out;
    
    // ALU Control
    alu_control alu_ctrl (
        .alu_op(id_ex_alu_op),
        .funct(id_ex_funct),
        .alu_control(alu_control)
    );
    
    // ALU
    alu alu_unit (
        .a(alu_input_a),
        .b(alu_input_b),
        .alu_control(alu_control),
        .shamt(id_ex_sign_extended[2:0]),
        .result(alu_result),
        .zero(alu_zero)
    );
    
    // Write Register MUX (rd or rt)
    assign write_reg_addr = id_ex_reg_dst ? id_ex_rd : id_ex_rt;
    
    // Branch Target Calculation
    assign branch_target = id_ex_pc + (id_ex_sign_extended << 1);
    
    // EX/MEM Pipeline Register
    ex_mem_register ex_mem_reg (
        .clk(clk),
        .rst(rst),
        .flush(pc_src),
        .pc_in(id_ex_pc),
        .alu_result_in(alu_result),
        .read_data2_in(forward_b_data),
        .write_reg_in(write_reg_addr),
        .zero_in(alu_zero),
        .mem_to_reg_in(id_ex_mem_to_reg),
        .reg_write_in(id_ex_reg_write),
        .mem_read_in(id_ex_mem_read),
        .mem_write_in(id_ex_mem_write),
        .branch_eq_in(id_ex_branch_eq),
        .branch_neq_in(id_ex_branch_neq),
        .branch_target_in(branch_target),
        .halt_in(id_ex_halt),
        // Outputs
        .pc_out(ex_mem_pc),
        .alu_result_out(ex_mem_alu_result),
        .read_data2_out(ex_mem_read_data2),
        .write_reg_out(ex_mem_write_reg),
        .zero_out(ex_mem_zero),
        .mem_to_reg_out(ex_mem_mem_to_reg),
        .reg_write_out(ex_mem_reg_write),
        .mem_read_out(ex_mem_mem_read),
        .mem_write_out(ex_mem_mem_write),
        .branch_eq_out(ex_mem_branch_eq),
        .branch_neq_out(ex_mem_branch_neq),
        .branch_target_out(ex_mem_branch_target),
        .halt_out(ex_mem_halt)
    );
    
    //=========================================================================
    // MEM Stage - Memory Access
    //=========================================================================
    
    // Branch Decision
    assign branch_taken = (ex_mem_branch_eq & ex_mem_zero) | 
                          (ex_mem_branch_neq & ~ex_mem_zero);
    assign pc_src = branch_taken;
    
    // Data Memory
    data_memory dmem (
        .clk(clk),
        .addr(ex_mem_alu_result),
        .write_data(ex_mem_read_data2),
        .mem_read(ex_mem_mem_read),
        .mem_write(ex_mem_mem_write),
        .read_data(mem_read_data)
    );
    
    // MEM/WB Pipeline Register
    mem_wb_register mem_wb_reg (
        .clk(clk),
        .rst(rst),
        .alu_result_in(ex_mem_alu_result),
        .mem_data_in(mem_read_data),
        .write_reg_in(ex_mem_write_reg),
        .mem_to_reg_in(ex_mem_mem_to_reg),
        .reg_write_in(ex_mem_reg_write),
        .halt_in(ex_mem_halt),
        // Outputs
        .alu_result_out(mem_wb_alu_result),
        .mem_data_out(mem_wb_mem_data),
        .write_reg_out(mem_wb_write_reg),
        .mem_to_reg_out(mem_wb_mem_to_reg),
        .reg_write_out(mem_wb_reg_write),
        .halt_out(mem_wb_halt)
    );
    
    //=========================================================================
    // WB Stage - Write Back
    //=========================================================================
    
    // Write Back MUX
    assign write_back_data = mem_wb_mem_to_reg ? mem_wb_mem_data : mem_wb_alu_result;
    
    //=========================================================================
    // Outputs
    //=========================================================================
    assign pc_out = pc_current;
    assign alu_result_out = alu_result;
    
    // Halt latch - once set, stays set (triggered from WB stage)
    reg halt_latched;
    always @(posedge clk or posedge rst) begin
        if (rst)
            halt_latched <= 1'b0;
        else if (mem_wb_halt)
            halt_latched <= 1'b1;
    end
    assign halted = mem_wb_halt | halt_latched;

endmodule
