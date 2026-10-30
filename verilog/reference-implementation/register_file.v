/*
 * Register File
 * 8 x 16-bit general purpose registers
 * R0 is hardwired to zero
 * 2 read ports, 1 write port
 * Internal forwarding: if reading same register being written, return write data
 */

module register_file (
    input  wire        clk,
    input  wire        rst,
    input  wire [2:0]  read_reg1,
    input  wire [2:0]  read_reg2,
    input  wire [2:0]  write_reg,
    input  wire [15:0] write_data,
    input  wire        reg_write,
    output wire [15:0] read_data1,
    output wire [15:0] read_data2
);

    // 8 registers
    reg [15:0] registers [0:7];
    
    // Read with internal forwarding (bypass)
    // If writing to same register being read, forward the write data
    assign read_data1 = (read_reg1 == 3'b000) ? 16'h0000 :
                        (reg_write && write_reg == read_reg1 && write_reg != 3'b000) ? write_data :
                        registers[read_reg1];
    
    assign read_data2 = (read_reg2 == 3'b000) ? 16'h0000 :
                        (reg_write && write_reg == read_reg2 && write_reg != 3'b000) ? write_data :
                        registers[read_reg2];
    
    // Write (R0 cannot be written)
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            registers[0] <= 16'h0000;
            registers[1] <= 16'h0000;
            registers[2] <= 16'h0000;
            registers[3] <= 16'h0000;
            registers[4] <= 16'h0000;
            registers[5] <= 16'h0000;
            registers[6] <= 16'h0000;
            registers[7] <= 16'h0000;
        end else if (reg_write && write_reg != 3'b000) begin
            registers[write_reg] <= write_data;
        end
    end

endmodule
