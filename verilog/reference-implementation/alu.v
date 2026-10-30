/*
 * Arithmetic Logic Unit (ALU)
 * Operations: ADD, SUB, AND, OR, SLT, SLL, SRL, PASS
 */

module alu (
    input  wire [15:0] a,
    input  wire [15:0] b,
    input  wire [2:0]  alu_op,
    input  wire [2:0]  funct,
    input  wire [2:0]  shamt,
    output reg  [15:0] result,
    output wire        zero
);

    // ALU Operation codes
    localparam ALU_RTYPE = 3'b000;  // R-type (use funct)
    localparam ALU_ADD   = 3'b001;  // Add (for ADDI, LW, SW)
    localparam ALU_SUB   = 3'b010;  // Subtract (for BEQ, BNE)
    localparam ALU_PASS  = 3'b011;  // Pass B (for LUI)
    
    // R-type function codes
    localparam FUNCT_ADD = 3'b000;
    localparam FUNCT_SUB = 3'b001;
    localparam FUNCT_AND = 3'b010;
    localparam FUNCT_OR  = 3'b011;
    localparam FUNCT_SLT = 3'b100;
    localparam FUNCT_SLL = 3'b101;
    localparam FUNCT_SRL = 3'b110;
    
    // Zero flag
    assign zero = (result == 16'h0000);
    
    // ALU operation
    always @(*) begin
        case (alu_op)
            ALU_RTYPE: begin
                case (funct)
                    FUNCT_ADD: result = a + b;
                    FUNCT_SUB: result = a - b;
                    FUNCT_AND: result = a & b;
                    FUNCT_OR:  result = a | b;
                    FUNCT_SLT: result = ($signed(a) < $signed(b)) ? 16'h0001 : 16'h0000;
                    FUNCT_SLL: result = b << shamt;
                    FUNCT_SRL: result = b >> shamt;
                    default:   result = 16'h0000;
                endcase
            end
            ALU_ADD: result = a + b;
            ALU_SUB: result = a - b;
            ALU_PASS: result = b;
            default: result = 16'h0000;
        endcase
    end

endmodule
