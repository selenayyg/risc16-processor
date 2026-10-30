//=============================================================================
// Control Unit
// Generates control signals based on opcode
//=============================================================================

module control_unit (
    input  wire [3:0] opcode,
    input  wire [2:0] funct,
    output reg        reg_dst,
    output reg        alu_src,
    output reg        mem_to_reg,
    output reg        reg_write,
    output reg        mem_read,
    output reg        mem_write,
    output reg        branch_eq,
    output reg        branch_neq,
    output reg        jump,
    output reg        jal,
    output reg        jr,
    output reg  [1:0] alu_op,
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
    
    always @(*) begin
        // Default values
        reg_dst    = 1'b0;
        alu_src    = 1'b0;
        mem_to_reg = 1'b0;
        reg_write  = 1'b0;
        mem_read   = 1'b0;
        mem_write  = 1'b0;
        branch_eq  = 1'b0;
        branch_neq = 1'b0;
        jump       = 1'b0;
        jal        = 1'b0;
        jr         = 1'b0;
        alu_op     = 2'b00;
        halt       = 1'b0;
        
        case (opcode)
            OP_RTYPE: begin
                // R-Type: ADD, SUB, AND, OR, SLT, SLL, SRL
                reg_dst   = 1'b1;   // Write to rd
                alu_src   = 1'b0;   // ALU input from register
                mem_to_reg = 1'b0;  // Write ALU result
                reg_write = 1'b1;   // Enable register write
                alu_op    = 2'b00;  // R-Type (use funct)
            end
            
            OP_ADDI: begin
                reg_dst   = 1'b0;   // Write to rt
                alu_src   = 1'b1;   // ALU input from immediate
                mem_to_reg = 1'b0;  // Write ALU result
                reg_write = 1'b1;   // Enable register write
                alu_op    = 2'b01;  // Add operation
            end
            
            OP_LW: begin
                reg_dst   = 1'b0;   // Write to rt
                alu_src   = 1'b1;   // ALU input from immediate (offset)
                mem_to_reg = 1'b1;  // Write memory data
                reg_write = 1'b1;   // Enable register write
                mem_read  = 1'b1;   // Enable memory read
                alu_op    = 2'b01;  // Add for address calculation
            end
            
            OP_SW: begin
                alu_src   = 1'b1;   // ALU input from immediate (offset)
                mem_write = 1'b1;   // Enable memory write
                alu_op    = 2'b01;  // Add for address calculation
            end
            
            OP_BEQ: begin
                branch_eq = 1'b1;   // Branch if equal
                alu_op    = 2'b10;  // Subtract for comparison
            end
            
            OP_BNE: begin
                branch_neq = 1'b1;  // Branch if not equal
                alu_op    = 2'b10;  // Subtract for comparison
            end
            
            OP_J: begin
                jump = 1'b1;        // Unconditional jump
            end
            
            OP_JAL: begin
                jump      = 1'b1;   // Jump
                jal       = 1'b1;   // Save return address
                reg_write = 1'b1;   // Write to R7
                reg_dst   = 1'b1;   // (Special handling for R7)
            end
            
            OP_JR: begin
                jr = 1'b1;          // Jump to register
            end
            
            OP_HALT: begin
                halt = 1'b1;        // Halt execution
            end
            
            default: begin
                // NOP - do nothing
            end
        endcase
    end

endmodule
