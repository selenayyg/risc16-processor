/*
 * Control Unit
 * Generates control signals based on opcode
 * 
 * Opcode Map:
 * 0000: R-type (ADD, SUB, AND, OR, SLT, SLL, SRL)
 * 0001: ADDI
 * 0010: LW
 * 0011: SW
 * 0100: BEQ
 * 0101: BNE
 * 0110: J
 * 0111: JAL
 * 1000: JR
 * 1111: HALT
 */

module control_unit (
    input  wire [3:0] opcode,
    input  wire [2:0] funct,
    output reg        reg_write,
    output reg        mem_to_reg,
    output reg        mem_read,
    output reg        mem_write,
    output reg  [2:0] alu_op,
    output reg        alu_src,
    output reg        branch,
    output reg        branch_ne,
    output reg        jump,
    output reg        jal,
    output reg        jr,
    output reg        halt
);

    // Opcodes
    localparam OP_RTYPE = 4'b0000;
    localparam OP_ADDI  = 4'b0001;
    localparam OP_LW    = 4'b0010;
    localparam OP_SW    = 4'b0011;
    localparam OP_BEQ   = 4'b0100;
    localparam OP_BNE   = 4'b0101;
    localparam OP_J     = 4'b0110;
    localparam OP_JAL   = 4'b0111;
    localparam OP_JR    = 4'b1000;
    localparam OP_HALT  = 4'b1111;
    
    // ALU operations
    localparam ALU_RTYPE = 3'b000;
    localparam ALU_ADD   = 3'b001;
    localparam ALU_SUB   = 3'b010;
    
    always @(*) begin
        // Default values
        reg_write  = 1'b0;
        mem_to_reg = 1'b0;
        mem_read   = 1'b0;
        mem_write  = 1'b0;
        alu_op     = ALU_ADD;
        alu_src    = 1'b0;
        branch     = 1'b0;
        branch_ne  = 1'b0;
        jump       = 1'b0;
        jal        = 1'b0;
        jr         = 1'b0;
        halt       = 1'b0;
        
        case (opcode)
            OP_RTYPE: begin
                reg_write = 1'b1;
                alu_op    = ALU_RTYPE;
            end
            
            OP_ADDI: begin
                reg_write = 1'b1;
                alu_src   = 1'b1;
                alu_op    = ALU_ADD;
            end
            
            OP_LW: begin
                reg_write  = 1'b1;
                mem_to_reg = 1'b1;
                mem_read   = 1'b1;
                alu_src    = 1'b1;
                alu_op     = ALU_ADD;
            end
            
            OP_SW: begin
                mem_write = 1'b1;
                alu_src   = 1'b1;
                alu_op    = ALU_ADD;
            end
            
            OP_BEQ: begin
                branch = 1'b1;
                alu_op = ALU_SUB;
            end
            
            OP_BNE: begin
                branch_ne = 1'b1;
                alu_op    = ALU_SUB;
            end
            
            OP_J: begin
                jump = 1'b1;
            end
            
            OP_JAL: begin
                reg_write = 1'b1;  // Write PC+2 to R7
                jal       = 1'b1;
                jump      = 1'b1;
            end
            
            OP_JR: begin
                jr = 1'b1;
            end
            
            OP_HALT: begin
                halt = 1'b1;
            end
            
            default: begin
                // NOP - all signals stay at default
            end
        endcase
    end

endmodule
