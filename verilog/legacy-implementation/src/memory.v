//=============================================================================
// Instruction Memory (ROM)
// 512 bytes = 256 x 16-bit words
//=============================================================================

module instruction_memory (
    input  wire [15:0] addr,
    output wire [15:0] instruction
);

    reg [15:0] memory [0:255];  // 256 words
    integer i;  // Loop variable (moved outside initial block)
    
    // Word-aligned access (addr >> 1)
    assign instruction = memory[addr[8:1]];
    
    // Initialize with test program
    initial begin
        // Default: NOP (all zeros)
        for (i = 0; i < 256; i = i + 1) begin
            memory[i] = 16'h0000;
        end
        
        // Test Program: Sum 1 to 5
        // R-Type: [opcode:4][rs:3][rt:3][rd:3][func:3]
        // I-Type: [opcode:4][rs:3][rt:3][imm:6]
        
        // addi r1, r0, 5    ; r1 = 5 (counter)
        // 0001 000 001 000101 = 0x1045
        memory[0] = 16'h1045;
        
        // addi r2, r0, 0    ; r2 = 0 (sum)
        // 0001 000 010 000000 = 0x1080
        memory[1] = 16'h1080;
        
        // loop: add r2, r2, r1  ; sum += counter (rd=r2, rs=r2, rt=r1)
        // 0000 010 001 010 000 = 0x0450
        memory[2] = 16'h0450;
        
        // addi r1, r1, -1   ; counter-- (rt=r1, rs=r1, imm=-1=111111)
        // 0001 001 001 111111 = 0x127F
        memory[3] = 16'h127F;
        
        // bne r1, r0, -3    ; if r1 != 0, goto loop 
        // Target = PC+2 + offset*2 = 0x000A + (-3)*2 = 0x0004
        // 0101 001 000 111101 = 0x523D
        memory[4] = 16'h523D;
        
        // halt (custom: opcode 1111)
        memory[5] = 16'hF000;
    end

endmodule

//=============================================================================
// Data Memory (RAM)
// 512 bytes = 256 x 16-bit words
//=============================================================================

module data_memory (
    input  wire        clk,
    input  wire [15:0] addr,
    input  wire [15:0] write_data,
    input  wire        mem_read,
    input  wire        mem_write,
    output wire [15:0] read_data
);

    reg [15:0] memory [0:255];  // 256 words
    integer i;  // Loop variable
    
    // Word-aligned access
    wire [7:0] word_addr = addr[8:1];
    
    // Read (combinational)
    assign read_data = mem_read ? memory[word_addr] : 16'h0000;
    
    // Write (sequential)
    always @(posedge clk) begin
        if (mem_write) begin
            memory[word_addr] <= write_data;
        end
    end
    
    // Initialize to zero
    initial begin
        for (i = 0; i < 256; i = i + 1) begin
            memory[i] = 16'h0000;
        end
    end

endmodule
