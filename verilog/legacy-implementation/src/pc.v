//=============================================================================
// Program Counter Register
//=============================================================================

module pc_register (
    input  wire        clk,
    input  wire        rst,
    input  wire        pc_write,    // PC write enable (for stall)
    input  wire [15:0] pc_in,
    output reg  [15:0] pc_out
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            pc_out <= 16'h0000;
        end else if (pc_write) begin
            pc_out <= pc_in;
        end
        // else: hold current value (stall)
    end

endmodule

//=============================================================================
// PC MUX - Selects next PC value
//=============================================================================

module pc_mux (
    input  wire [15:0] pc_plus_2,
    input  wire [15:0] branch_target,
    input  wire [15:0] jump_target,
    input  wire [15:0] jr_target,
    input  wire        pc_src,      // Branch taken
    input  wire        jump,        // J or JAL
    input  wire        jr,          // JR instruction
    output reg  [15:0] pc_next
);

    always @(*) begin
        if (jr) begin
            pc_next = jr_target;
        end else if (jump) begin
            pc_next = jump_target;
        end else if (pc_src) begin
            pc_next = branch_target;
        end else begin
            pc_next = pc_plus_2;
        end
    end

endmodule
