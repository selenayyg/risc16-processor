/*
 * Pipeline Registers
 * IF/ID, ID/EX, EX/MEM, MEM/WB
 */

// =========================================================================
// IF/ID Pipeline Register
// =========================================================================
module if_id_reg (
    input  wire        clk,
    input  wire        rst,
    input  wire        stall,
    input  wire        flush,
    input  wire [15:0] if_pc,
    input  wire [15:0] if_instruction,
    output reg  [15:0] id_pc,
    output reg  [15:0] id_instruction
);

    always @(posedge clk or posedge rst) begin
        if (rst || flush) begin
            id_pc <= 16'h0000;
            id_instruction <= 16'h0000;  // NOP
        end else if (!stall) begin
            id_pc <= if_pc;
            id_instruction <= if_instruction;
        end
    end

endmodule

// =========================================================================
// ID/EX Pipeline Register
// =========================================================================
module id_ex_reg (
    input  wire        clk,
    input  wire        rst,
    input  wire        flush,
    // Data inputs
    input  wire [15:0] id_pc,
    input  wire [15:0] id_read_data1,
    input  wire [15:0] id_read_data2,
    input  wire [15:0] id_imm_ext,
    input  wire [2:0]  id_rs,
    input  wire [2:0]  id_rt,
    input  wire [2:0]  id_rd,
    input  wire [2:0]  id_shamt,
    input  wire [2:0]  id_funct,
    input  wire [3:0]  id_opcode,
    // Control inputs
    input  wire        id_reg_write,
    input  wire        id_mem_to_reg,
    input  wire        id_mem_read,
    input  wire        id_mem_write,
    input  wire [2:0]  id_alu_op,
    input  wire        id_alu_src,
    input  wire        id_branch,
    input  wire        id_branch_ne,
    // Data outputs
    output reg  [15:0] ex_pc,
    output reg  [15:0] ex_read_data1,
    output reg  [15:0] ex_read_data2,
    output reg  [15:0] ex_imm_ext,
    output reg  [2:0]  ex_rs,
    output reg  [2:0]  ex_rt,
    output reg  [2:0]  ex_rd,
    output reg  [2:0]  ex_shamt,
    output reg  [2:0]  ex_funct,
    output reg  [3:0]  ex_opcode,
    // Control outputs
    output reg         ex_reg_write,
    output reg         ex_mem_to_reg,
    output reg         ex_mem_read,
    output reg         ex_mem_write,
    output reg  [2:0]  ex_alu_op,
    output reg         ex_alu_src,
    output reg         ex_branch,
    output reg         ex_branch_ne
);

    always @(posedge clk or posedge rst) begin
        if (rst || flush) begin
            ex_pc <= 16'h0000;
            ex_read_data1 <= 16'h0000;
            ex_read_data2 <= 16'h0000;
            ex_imm_ext <= 16'h0000;
            ex_rs <= 3'b000;
            ex_rt <= 3'b000;
            ex_rd <= 3'b000;
            ex_shamt <= 3'b000;
            ex_funct <= 3'b000;
            ex_opcode <= 4'b0000;
            ex_reg_write <= 1'b0;
            ex_mem_to_reg <= 1'b0;
            ex_mem_read <= 1'b0;
            ex_mem_write <= 1'b0;
            ex_alu_op <= 3'b000;
            ex_alu_src <= 1'b0;
            ex_branch <= 1'b0;
            ex_branch_ne <= 1'b0;
        end else begin
            ex_pc <= id_pc;
            ex_read_data1 <= id_read_data1;
            ex_read_data2 <= id_read_data2;
            ex_imm_ext <= id_imm_ext;
            ex_rs <= id_rs;
            ex_rt <= id_rt;
            ex_rd <= id_rd;
            ex_shamt <= id_shamt;
            ex_funct <= id_funct;
            ex_opcode <= id_opcode;
            ex_reg_write <= id_reg_write;
            ex_mem_to_reg <= id_mem_to_reg;
            ex_mem_read <= id_mem_read;
            ex_mem_write <= id_mem_write;
            ex_alu_op <= id_alu_op;
            ex_alu_src <= id_alu_src;
            ex_branch <= id_branch;
            ex_branch_ne <= id_branch_ne;
        end
    end

endmodule

// =========================================================================
// EX/MEM Pipeline Register
// =========================================================================
module ex_mem_reg (
    input  wire        clk,
    input  wire        rst,
    input  wire        flush,
    // Data inputs
    input  wire [15:0] ex_pc,
    input  wire [15:0] ex_alu_result,
    input  wire [15:0] ex_write_data,
    input  wire [2:0]  ex_write_reg,
    input  wire        ex_zero,
    input  wire [15:0] ex_imm_ext,
    // Control inputs
    input  wire        ex_reg_write,
    input  wire        ex_mem_to_reg,
    input  wire        ex_mem_read,
    input  wire        ex_mem_write,
    input  wire        ex_branch,
    input  wire        ex_branch_ne,
    // Data outputs
    output reg  [15:0] mem_pc,
    output reg  [15:0] mem_alu_result,
    output reg  [15:0] mem_write_data,
    output reg  [2:0]  mem_write_reg,
    output reg         mem_zero,
    output reg  [15:0] mem_imm_ext,
    // Control outputs
    output reg         mem_reg_write,
    output reg         mem_mem_to_reg,
    output reg         mem_mem_read,
    output reg         mem_mem_write,
    output reg         mem_branch,
    output reg         mem_branch_ne
);

    always @(posedge clk or posedge rst) begin
        if (rst || flush) begin
            mem_pc <= 16'h0000;
            mem_alu_result <= 16'h0000;
            mem_write_data <= 16'h0000;
            mem_write_reg <= 3'b000;
            mem_zero <= 1'b0;
            mem_imm_ext <= 16'h0000;
            mem_reg_write <= 1'b0;
            mem_mem_to_reg <= 1'b0;
            mem_mem_read <= 1'b0;
            mem_mem_write <= 1'b0;
            mem_branch <= 1'b0;
            mem_branch_ne <= 1'b0;
        end else begin
            mem_pc <= ex_pc;
            mem_alu_result <= ex_alu_result;
            mem_write_data <= ex_write_data;
            mem_write_reg <= ex_write_reg;
            mem_zero <= ex_zero;
            mem_imm_ext <= ex_imm_ext;
            mem_reg_write <= ex_reg_write;
            mem_mem_to_reg <= ex_mem_to_reg;
            mem_mem_read <= ex_mem_read;
            mem_mem_write <= ex_mem_write;
            mem_branch <= ex_branch;
            mem_branch_ne <= ex_branch_ne;
        end
    end

endmodule

// =========================================================================
// MEM/WB Pipeline Register
// =========================================================================
module mem_wb_reg (
    input  wire        clk,
    input  wire        rst,
    // Data inputs
    input  wire [15:0] mem_alu_result,
    input  wire [15:0] mem_mem_data,
    input  wire [2:0]  mem_write_reg,
    // Control inputs
    input  wire        mem_reg_write,
    input  wire        mem_mem_to_reg,
    // Data outputs
    output reg  [15:0] wb_alu_result,
    output reg  [15:0] wb_mem_data,
    output reg  [2:0]  wb_write_reg,
    // Control outputs
    output reg         wb_reg_write,
    output reg         wb_mem_to_reg
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            wb_alu_result <= 16'h0000;
            wb_mem_data <= 16'h0000;
            wb_write_reg <= 3'b000;
            wb_reg_write <= 1'b0;
            wb_mem_to_reg <= 1'b0;
        end else begin
            wb_alu_result <= mem_alu_result;
            wb_mem_data <= mem_mem_data;
            wb_write_reg <= mem_write_reg;
            wb_reg_write <= mem_reg_write;
            wb_mem_to_reg <= mem_mem_to_reg;
        end
    end

endmodule
