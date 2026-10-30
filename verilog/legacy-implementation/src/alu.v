//=============================================================================
// ALU Control Unit
// Generates ALU control signals based on ALUOp and Function code
//=============================================================================

module alu_control (
    input  wire [1:0] alu_op,
    input  wire [2:0] funct,
    output reg  [3:0] alu_control
);

    // ALU Operations
    localparam ALU_ADD = 4'b0000;
    localparam ALU_SUB = 4'b0001;
    localparam ALU_AND = 4'b0010;
    localparam ALU_OR  = 4'b0011;
    localparam ALU_SLT = 4'b0100;
    localparam ALU_SLL = 4'b0101;
    localparam ALU_SRL = 4'b0110;
    
    always @(*) begin
        case (alu_op)
            2'b00: begin  // R-Type: use function code
                case (funct)
                    3'b000: alu_control = ALU_ADD;  // ADD
                    3'b001: alu_control = ALU_SUB;  // SUB
                    3'b010: alu_control = ALU_AND;  // AND
                    3'b011: alu_control = ALU_OR;   // OR
                    3'b100: alu_control = ALU_SLT;  // SLT
                    3'b101: alu_control = ALU_SLL;  // SLL
                    3'b110: alu_control = ALU_SRL;  // SRL
                    default: alu_control = ALU_ADD;
                endcase
            end
            2'b01: alu_control = ALU_ADD;  // ADDI, LW, SW (add for address calc)
            2'b10: alu_control = ALU_SUB;  // BEQ, BNE (subtract for comparison)
            default: alu_control = ALU_ADD;
        endcase
    end

endmodule

//=============================================================================
// ALU (Arithmetic Logic Unit)
// Performs arithmetic and logical operations
//=============================================================================

module alu (
    input  wire [15:0] a,
    input  wire [15:0] b,
    input  wire [3:0]  alu_control,
    input  wire [2:0]  shamt,         // Shift amount for SLL/SRL
    output reg  [15:0] result,
    output wire        zero
);

    // ALU Operations
    localparam ALU_ADD = 4'b0000;
    localparam ALU_SUB = 4'b0001;
    localparam ALU_AND = 4'b0010;
    localparam ALU_OR  = 4'b0011;
    localparam ALU_SLT = 4'b0100;
    localparam ALU_SLL = 4'b0101;
    localparam ALU_SRL = 4'b0110;
    
    always @(*) begin
        case (alu_control)
            ALU_ADD: result = a + b;
            ALU_SUB: result = a - b;
            ALU_AND: result = a & b;
            ALU_OR:  result = a | b;
            ALU_SLT: result = ($signed(a) < $signed(b)) ? 16'd1 : 16'd0;
            ALU_SLL: result = b << shamt;
            ALU_SRL: result = b >> shamt;
            default: result = 16'h0000;
        endcase
    end
    
    assign zero = (result == 16'h0000);

endmodule
