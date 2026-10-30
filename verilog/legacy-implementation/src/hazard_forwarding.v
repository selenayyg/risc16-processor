//=============================================================================
// Hazard Detection Unit
// Detects data hazards and generates stall signals
//=============================================================================

module hazard_detection_unit (
    input  wire       id_ex_mem_read,   // Load instruction in EX stage
    input  wire [2:0] id_ex_rt,         // Load destination register
    input  wire [2:0] if_id_rs,         // Source register 1 in ID
    input  wire [2:0] if_id_rt,         // Source register 2 in ID
    input  wire       branch_eq,        // BEQ instruction
    input  wire       branch_neq,       // BNE instruction
    input  wire       jump,             // Jump instruction
    input  wire       jr,               // JR instruction
    output wire       pc_write,         // PC write enable
    output wire       if_id_write,      // IF/ID write enable
    output wire       stall,            // Stall signal
    output wire       if_flush          // Flush IF stage
);

    // Load-Use Hazard Detection
    // Stall if: Load in EX and next instruction uses load destination
    wire load_use_hazard;
    assign load_use_hazard = id_ex_mem_read && 
                             ((id_ex_rt == if_id_rs) || (id_ex_rt == if_id_rt)) &&
                             (id_ex_rt != 3'b000);  // Not R0
    
    // Stall pipeline for load-use hazard
    assign stall = load_use_hazard;
    
    // PC and IF/ID write control
    assign pc_write = ~load_use_hazard;
    assign if_id_write = ~load_use_hazard;
    
    // Flush only for jumps (branches handled by pc_src in main module)
    assign if_flush = jump | jr;

endmodule

//=============================================================================
// Forwarding Unit
// Detects data dependencies and generates forwarding control signals
//=============================================================================

module forwarding_unit (
    input  wire [2:0] id_ex_rs,         // Source register 1 in EX stage
    input  wire [2:0] id_ex_rt,         // Source register 2 in EX stage
    input  wire [2:0] ex_mem_rd,        // Destination in MEM stage
    input  wire [2:0] mem_wb_rd,        // Destination in WB stage
    input  wire       ex_mem_reg_write, // RegWrite in MEM stage
    input  wire       mem_wb_reg_write, // RegWrite in WB stage
    output reg  [1:0] forward_a,        // Forwarding control for ALU input A
    output reg  [1:0] forward_b         // Forwarding control for ALU input B
);

    // Forwarding control values:
    // 00 = No forwarding (use ID/EX register value)
    // 01 = Forward from MEM/WB stage
    // 10 = Forward from EX/MEM stage

    always @(*) begin
        // Default: no forwarding
        forward_a = 2'b00;
        forward_b = 2'b00;
        
        // Forward A (for rs)
        if (ex_mem_reg_write && (ex_mem_rd != 3'b000) && (ex_mem_rd == id_ex_rs)) begin
            // EX hazard - forward from EX/MEM
            forward_a = 2'b10;
        end else if (mem_wb_reg_write && (mem_wb_rd != 3'b000) && (mem_wb_rd == id_ex_rs)) begin
            // MEM hazard - forward from MEM/WB
            forward_a = 2'b01;
        end
        
        // Forward B (for rt)
        if (ex_mem_reg_write && (ex_mem_rd != 3'b000) && (ex_mem_rd == id_ex_rt)) begin
            // EX hazard - forward from EX/MEM
            forward_b = 2'b10;
        end else if (mem_wb_reg_write && (mem_wb_rd != 3'b000) && (mem_wb_rd == id_ex_rt)) begin
            // MEM hazard - forward from MEM/WB
            forward_b = 2'b01;
        end
    end

endmodule
