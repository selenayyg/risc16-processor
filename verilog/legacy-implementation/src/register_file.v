//=============================================================================
// Register File
// 8 x 16-bit registers (R0-R7)
// R0 is hardwired to zero
// R7 is used as return address (ra) for JAL
//=============================================================================

module register_file (
    input  wire        clk,
    input  wire        rst,
    input  wire [2:0]  read_reg1,    // rs
    input  wire [2:0]  read_reg2,    // rt
    input  wire [2:0]  write_reg,    // Destination register
    input  wire [15:0] write_data,   // Data to write
    input  wire        reg_write,    // Write enable
    output wire [15:0] read_data1,   // rs value
    output wire [15:0] read_data2    // rt value
);

    reg [15:0] registers [0:7];
    
    // Read ports with bypass (combinational)
    // If reading the same register being written, forward the write data
    // R0 always returns 0
    assign read_data1 = (read_reg1 == 3'b000) ? 16'h0000 :
                        (reg_write && (read_reg1 == write_reg)) ? write_data :
                        registers[read_reg1];
                        
    assign read_data2 = (read_reg2 == 3'b000) ? 16'h0000 :
                        (reg_write && (read_reg2 == write_reg)) ? write_data :
                        registers[read_reg2];
    
    // Write port (sequential, on positive edge)
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
