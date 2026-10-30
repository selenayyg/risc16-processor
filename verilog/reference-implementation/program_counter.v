/*
 * Program Counter Module
 * Holds and updates the current instruction address
 */

module program_counter (
    input  wire        clk,
    input  wire        rst,
    input  wire        stall,
    input  wire        halt,
    input  wire [15:0] pc_next,
    output reg  [15:0] pc_current
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            pc_current <= 16'h0000;
        end else if (!stall && !halt) begin
            pc_current <= pc_next;
        end
    end

endmodule
