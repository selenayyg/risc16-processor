/*
 * RISC-16 Processor Testbench
 * Tests the 5-stage pipelined processor
 */

`timescale 1ns/1ps

module risc16_tb;

    // Clock and reset
    reg clk;
    reg rst;
    
    // Outputs
    wire [15:0] pc;
    wire [15:0] instruction;
    wire halted;
    
    // Clock period
    parameter CLK_PERIOD = 10;
    
    // Instantiate CPU
    risc16_cpu cpu (
        .clk(clk),
        .rst(rst),
        .pc_out(pc),
        .instruction_out(instruction),
        .halted(halted)
    );
    
    // Clock generation
    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end
    
    // Test sequence
    initial begin
        // Initialize
        $display("========================================");
        $display("RISC-16 Processor Testbench");
        $display("========================================");
        $display("");
        
        // Reset
        rst = 1;
        #(CLK_PERIOD * 2);
        rst = 0;
        
        $display("Time\t\tPC\tInstruction\tR1\tR2\tR3");
        $display("----\t\t--\t-----------\t--\t--\t--");
        
        // Run until halt or timeout
        repeat (100) begin
            @(posedge clk);
            #1;
            
            $display("%0t\tPC=%h\tR1=%0d\tR2=%0d\tbranch_taken=%b",
                $time, pc,
                cpu.regfile.registers[1],
                cpu.regfile.registers[2],
                cpu.mem_branch_taken
            );
            
            if (halted) begin
                // Wait one more cycle for SW to complete memory write
                @(posedge clk);
                #1;
                
                $display("");
                $display("========================================");
                $display("Processor Halted!");
                $display("========================================");
                $display("");
                $display("Final Register Values:");
                $display("  R0 = %d (0x%h)", cpu.regfile.registers[0], cpu.regfile.registers[0]);
                $display("  R1 = %d (0x%h)", cpu.regfile.registers[1], cpu.regfile.registers[1]);
                $display("  R2 = %d (0x%h)", cpu.regfile.registers[2], cpu.regfile.registers[2]);
                $display("  R3 = %d (0x%h)", cpu.regfile.registers[3], cpu.regfile.registers[3]);
                $display("  R4 = %d (0x%h)", cpu.regfile.registers[4], cpu.regfile.registers[4]);
                $display("  R5 = %d (0x%h)", cpu.regfile.registers[5], cpu.regfile.registers[5]);
                $display("  R6 = %d (0x%h)", cpu.regfile.registers[6], cpu.regfile.registers[6]);
                $display("  R7 = %d (0x%h)", cpu.regfile.registers[7], cpu.regfile.registers[7]);
                $display("");
                $display("Data Memory[0] = %d (0x%h)", cpu.dmem.mem[0], cpu.dmem.mem[0]);
                $display("Data Memory[1] = %d (0x%h)", cpu.dmem.mem[1], cpu.dmem.mem[1]);
                $display("");
                
                // Verify result
                if (cpu.regfile.registers[2] == 15 && cpu.dmem.mem[0] == 15) begin
                    $display("========================================");
                    $display("TEST PASSED!");
                    $display("Sum of 1+2+3+4+5 = 15 verified!");
                    $display("========================================");
                end else begin
                    $display("========================================");
                    $display("TEST FAILED!");
                    $display("Expected R2=15, Mem[0]=15");
                    $display("Got R2=%d, Mem[0]=%d", cpu.regfile.registers[2], cpu.dmem.mem[0]);
                    $display("========================================");
                end
                
                $finish;
            end
        end
        
        $display("");
        $display("Timeout! Processor did not halt.");
        $finish;
    end
    
    // Waveform dump
    initial begin
        $dumpfile("risc16_tb.vcd");
        $dumpvars(0, risc16_tb);
    end

endmodule
