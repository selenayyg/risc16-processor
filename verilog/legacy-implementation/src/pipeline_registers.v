//=============================================================================
// IF/ID Pipeline Register
//=============================================================================

module if_id_register (
    input  wire        clk,
    input  wire        rst,
    input  wire        if_id_write,   // Write enable (for stall)
    input  wire        if_flush,      // Flush signal
    input  wire [15:0] pc_in,
    input  wire [15:0] instruction_in,
    output reg  [15:0] pc_out,
    output reg  [15:0] instruction_out
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            pc_out <= 16'h0000;
            instruction_out <= 16'h0000;  // NOP
        end else if (if_flush) begin
            pc_out <= 16'h0000;
            instruction_out <= 16'h0000;  // Insert bubble
        end else if (if_id_write) begin
            pc_out <= pc_in;
            instruction_out <= instruction_in;
        end
        // else: hold current values (stall)
    end

endmodule

//=============================================================================
// ID/EX Pipeline Register
//=============================================================================

module id_ex_register (
    input  wire        clk,
    input  wire        rst,
    input  wire        flush,
    // Data inputs
    input  wire [15:0] pc_in,
    input  wire [15:0] read_data1_in,
    input  wire [15:0] read_data2_in,
    input  wire [15:0] sign_extended_in,
    input  wire [2:0]  rs_in,
    input  wire [2:0]  rt_in,
    input  wire [2:0]  rd_in,
    input  wire [2:0]  funct_in,
    // Control inputs
    input  wire        reg_dst_in,
    input  wire        alu_src_in,
    input  wire        mem_to_reg_in,
    input  wire        reg_write_in,
    input  wire        mem_read_in,
    input  wire        mem_write_in,
    input  wire        branch_eq_in,
    input  wire        branch_neq_in,
    input  wire [1:0]  alu_op_in,
    input  wire        halt_in,
    // Data outputs
    output reg  [15:0] pc_out,
    output reg  [15:0] read_data1_out,
    output reg  [15:0] read_data2_out,
    output reg  [15:0] sign_extended_out,
    output reg  [2:0]  rs_out,
    output reg  [2:0]  rt_out,
    output reg  [2:0]  rd_out,
    output reg  [2:0]  funct_out,
    // Control outputs
    output reg         reg_dst_out,
    output reg         alu_src_out,
    output reg         mem_to_reg_out,
    output reg         reg_write_out,
    output reg         mem_read_out,
    output reg         mem_write_out,
    output reg         branch_eq_out,
    output reg         branch_neq_out,
    output reg  [1:0]  alu_op_out,
    output reg         halt_out
);

    always @(posedge clk or posedge rst) begin
        if (rst || flush) begin
            // Insert bubble (NOP)
            pc_out           <= 16'h0000;
            read_data1_out   <= 16'h0000;
            read_data2_out   <= 16'h0000;
            sign_extended_out <= 16'h0000;
            rs_out           <= 3'b000;
            rt_out           <= 3'b000;
            rd_out           <= 3'b000;
            funct_out        <= 3'b000;
            reg_dst_out      <= 1'b0;
            alu_src_out      <= 1'b0;
            mem_to_reg_out   <= 1'b0;
            reg_write_out    <= 1'b0;
            mem_read_out     <= 1'b0;
            mem_write_out    <= 1'b0;
            branch_eq_out    <= 1'b0;
            branch_neq_out   <= 1'b0;
            alu_op_out       <= 2'b00;
            halt_out         <= 1'b0;
        end else begin
            pc_out           <= pc_in;
            read_data1_out   <= read_data1_in;
            read_data2_out   <= read_data2_in;
            sign_extended_out <= sign_extended_in;
            rs_out           <= rs_in;
            rt_out           <= rt_in;
            rd_out           <= rd_in;
            funct_out        <= funct_in;
            reg_dst_out      <= reg_dst_in;
            alu_src_out      <= alu_src_in;
            mem_to_reg_out   <= mem_to_reg_in;
            reg_write_out    <= reg_write_in;
            mem_read_out     <= mem_read_in;
            mem_write_out    <= mem_write_in;
            branch_eq_out    <= branch_eq_in;
            branch_neq_out   <= branch_neq_in;
            alu_op_out       <= alu_op_in;
            halt_out         <= halt_in;
        end
    end

endmodule

//=============================================================================
// EX/MEM Pipeline Register
//=============================================================================

module ex_mem_register (
    input  wire        clk,
    input  wire        rst,
    input  wire        flush,
    // Data inputs
    input  wire [15:0] pc_in,
    input  wire [15:0] alu_result_in,
    input  wire [15:0] read_data2_in,
    input  wire [2:0]  write_reg_in,
    input  wire        zero_in,
    // Control inputs
    input  wire        mem_to_reg_in,
    input  wire        reg_write_in,
    input  wire        mem_read_in,
    input  wire        mem_write_in,
    input  wire        branch_eq_in,
    input  wire        branch_neq_in,
    input  wire [15:0] branch_target_in,
    input  wire        halt_in,
    // Data outputs
    output reg  [15:0] pc_out,
    output reg  [15:0] alu_result_out,
    output reg  [15:0] read_data2_out,
    output reg  [2:0]  write_reg_out,
    output reg         zero_out,
    // Control outputs
    output reg         mem_to_reg_out,
    output reg         reg_write_out,
    output reg         mem_read_out,
    output reg         mem_write_out,
    output reg         branch_eq_out,
    output reg         branch_neq_out,
    output reg  [15:0] branch_target_out,
    output reg         halt_out
);

    always @(posedge clk or posedge rst) begin
        if (rst || flush) begin
            pc_out           <= 16'h0000;
            alu_result_out   <= 16'h0000;
            read_data2_out   <= 16'h0000;
            write_reg_out    <= 3'b000;
            zero_out         <= 1'b0;
            mem_to_reg_out   <= 1'b0;
            reg_write_out    <= 1'b0;
            mem_read_out     <= 1'b0;
            mem_write_out    <= 1'b0;
            branch_eq_out    <= 1'b0;
            branch_neq_out   <= 1'b0;
            branch_target_out <= 16'h0000;
            halt_out         <= 1'b0;
        end else begin
            pc_out           <= pc_in;
            alu_result_out   <= alu_result_in;
            read_data2_out   <= read_data2_in;
            write_reg_out    <= write_reg_in;
            zero_out         <= zero_in;
            mem_to_reg_out   <= mem_to_reg_in;
            reg_write_out    <= reg_write_in;
            mem_read_out     <= mem_read_in;
            mem_write_out    <= mem_write_in;
            branch_eq_out    <= branch_eq_in;
            branch_neq_out   <= branch_neq_in;
            branch_target_out <= branch_target_in;
            halt_out         <= halt_in;
        end
    end

endmodule

//=============================================================================
// MEM/WB Pipeline Register
//=============================================================================

module mem_wb_register (
    input  wire        clk,
    input  wire        rst,
    // Data inputs
    input  wire [15:0] alu_result_in,
    input  wire [15:0] mem_data_in,
    input  wire [2:0]  write_reg_in,
    // Control inputs
    input  wire        mem_to_reg_in,
    input  wire        reg_write_in,
    input  wire        halt_in,
    // Data outputs
    output reg  [15:0] alu_result_out,
    output reg  [15:0] mem_data_out,
    output reg  [2:0]  write_reg_out,
    // Control outputs
    output reg         mem_to_reg_out,
    output reg         reg_write_out,
    output reg         halt_out
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            alu_result_out <= 16'h0000;
            mem_data_out   <= 16'h0000;
            write_reg_out  <= 3'b000;
            mem_to_reg_out <= 1'b0;
            reg_write_out  <= 1'b0;
            halt_out       <= 1'b0;
        end else begin
            alu_result_out <= alu_result_in;
            mem_data_out   <= mem_data_in;
            write_reg_out  <= write_reg_in;
            mem_to_reg_out <= mem_to_reg_in;
            reg_write_out  <= reg_write_in;
            halt_out       <= halt_in;
        end
    end

endmodule
