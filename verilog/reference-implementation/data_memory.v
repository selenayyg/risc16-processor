/*
 * Data Memory (RAM)
 * Size: 512 Bytes = 256 x 16-bit words
 * Byte-addressable, synchronous write
 */

module data_memory (
    input  wire        clk,
    input  wire [15:0] addr,
    input  wire [15:0] write_data,
    input  wire        mem_read,
    input  wire        mem_write,
    output wire [15:0] read_data
);

    // 256 x 16-bit memory
    reg [15:0] mem [0:255];
    
    // Word-aligned address
    wire [7:0] word_addr = addr[8:1];
    
    // Synchronous write
    always @(posedge clk) begin
        if (mem_write) begin
            mem[word_addr] <= write_data;
        end
    end
    
    // Asynchronous read
    assign read_data = mem_read ? mem[word_addr] : 16'h0000;
    
    // Initialize to zero
    integer i;
    initial begin
        for (i = 0; i < 256; i = i + 1) begin
            mem[i] = 16'h0000;
        end
    end

endmodule
