/*
 * Hazard Detection Unit
 * Detects load-use hazards and generates stall signal
 */

module hazard_unit (
    input  wire       idex_mem_read,
    input  wire [2:0] idex_rt,
    input  wire [2:0] ifid_rs,
    input  wire [2:0] ifid_rt,
    output wire       stall
);

    // Load-use hazard detection
    // If instruction in EX stage is a load (LW) and
    // the destination register matches source of instruction in ID stage
    assign stall = idex_mem_read && 
                   (idex_rt != 3'b000) &&
                   ((idex_rt == ifid_rs) || (idex_rt == ifid_rt));

endmodule


/*
 * Forwarding Unit
 * Resolves data hazards by forwarding results from later pipeline stages
 * 
 * Forward select values:
 * 00: No forwarding (use register file)
 * 01: Forward from MEM/WB stage
 * 10: Forward from EX/MEM stage
 */

module forwarding_unit (
    input  wire [2:0] idex_rs,
    input  wire [2:0] idex_rt,
    input  wire [2:0] exmem_rd,
    input  wire [2:0] memwb_rd,
    input  wire       exmem_reg_write,
    input  wire       memwb_reg_write,
    output reg  [1:0] forward_a,
    output reg  [1:0] forward_b
);

    // Forward A (for rs operand)
    always @(*) begin
        if (exmem_reg_write && (exmem_rd != 3'b000) && (exmem_rd == idex_rs)) begin
            forward_a = 2'b10;  // Forward from EX/MEM
        end else if (memwb_reg_write && (memwb_rd != 3'b000) && (memwb_rd == idex_rs)) begin
            forward_a = 2'b01;  // Forward from MEM/WB
        end else begin
            forward_a = 2'b00;  // No forwarding
        end
    end
    
    // Forward B (for rt operand)
    always @(*) begin
        if (exmem_reg_write && (exmem_rd != 3'b000) && (exmem_rd == idex_rt)) begin
            forward_b = 2'b10;  // Forward from EX/MEM
        end else if (memwb_reg_write && (memwb_rd != 3'b000) && (memwb_rd == idex_rt)) begin
            forward_b = 2'b01;  // Forward from MEM/WB
        end else begin
            forward_b = 2'b00;  // No forwarding
        end
    end

endmodule


/*
 * Halt Control
 * Latches halt signal (but not if instruction is being flushed)
 */

module halt_control (
    input  wire clk,
    input  wire rst,
    input  wire halt_in,
    input  wire flush,
    output reg  halt_out
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            halt_out <= 1'b0;
        end else if (halt_in && !flush) begin
            halt_out <= 1'b1;
        end
    end

endmodule
