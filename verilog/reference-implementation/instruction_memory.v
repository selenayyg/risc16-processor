/*
 * Instruction Memory (ROM)
 * Size: 512 Bytes = 256 x 16-bit words
 * Byte-addressable
 */

module instruction_memory (
    input  wire [15:0] addr,
    output wire [15:0] instruction
);

    // 256 x 16-bit memory
    reg [15:0] mem [0:255];
    
    // Word-aligned address (addr / 2)
    wire [7:0] word_addr = addr[8:1];
    
    // Read instruction
    assign instruction = mem[word_addr];
    
    // Initialize with test program
    integer i;
    initial begin
        // Default: all zeros (NOP)
        for (i = 0; i < 256; i = i + 1) begin
            mem[i] = 16'h0000;
        end
        
        // =============================================
        // Test Program: Sum 1 to 5 = 15
        // =============================================
        // addi r1, r0, 5     ; r1 = 5 (counter)
        // addi r2, r0, 0     ; r2 = 0 (sum)
        // loop:
        // add  r2, r2, r1    ; r2 = r2 + r1
        // addi r1, r1, -1    ; r1 = r1 - 1
        // bne  r1, r0, loop  ; if r1 != 0, goto loop
        // sw   r2, 0(r0)     ; Mem[0] = r2
        // halt
        
        // Instruction encoding:
        // R-type: [opcode:4][rs:3][rt:3][rd:3][shamt/funct:3]
        // I-type: [opcode:4][rs:3][rt:3][imm:6]
        
        // addi r1, r0, 5  -> opcode=0001, rs=000, rt=001, imm=000101
        mem[0] = 16'b0001_000_001_000101;  // 0x1045
        
        // addi r2, r0, 0  -> opcode=0001, rs=000, rt=010, imm=000000
        mem[1] = 16'b0001_000_010_000000;  // 0x1080
        
        // add r2, r2, r1  -> opcode=0000, rs=010, rt=001, rd=010, funct=000
        mem[2] = 16'b0000_010_001_010_000;  // 0x0250
        
        // addi r1, r1, -1 -> opcode=0001, rs=001, rt=001, imm=111111
        mem[3] = 16'b0001_001_001_111111;  // 0x127F
        
        // bne r1, r0, -3  -> opcode=0101, rs=001, rt=000, imm=111101 (-3)
        mem[4] = 16'b0101_001_000_111101;  // 0x523D
        
        // sw r2, 0(r0)    -> opcode=0011, rs=000, rt=010, imm=000000
        mem[5] = 16'b0011_000_010_000000;  // 0x3080
        
        // halt            -> opcode=1111
        mem[6] = 16'b1111_000_000_000000;  // 0xF000
    end

endmodule
