//=============================================================================
// RISC-16 CPU Testbench
//=============================================================================

`timescale 1ns / 1ps

module risc16_tb;

    // Clock and Reset
    reg clk;
    reg rst;
    
    // Outputs
    wire [15:0] pc_out;
    wire [15:0] alu_result_out;
    wire halted;
    
    // Instantiate the CPU
    risc16_cpu uut (
        .clk(clk),
        .rst(rst),
        .pc_out(pc_out),
        .alu_result_out(alu_result_out),
        .halted(halted)
    );
    
    // Clock generation: 100MHz (10ns period)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
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
        #20;
        rst = 0;
        
        $display("Cycle\tPC\tIF_Inst\t\tR1\tR2");
        $display("-----\t--\t-------\t\t--\t--");
        
        // Run simulation
        repeat(100) begin
            @(posedge clk);
            #1;
            $display("%0d\t%h\t%h\t\t%0d\t%0d", 
                     ($time-20)/10, 
                     pc_out, 
                     uut.instruction,
                     $signed(uut.reg_file.registers[1]),
                     $signed(uut.reg_file.registers[2]));
            
            // Check for halt
            if (halted) begin
                $display("");
                $display("========================================");
                $display("Program Halted at cycle %0d!", ($time-20)/10);
                $display("========================================");
                $display("");
                $display("Final Register Values:");
                $display("R0 = %0d (always 0)", uut.reg_file.registers[0]);
                $display("R1 = %0d", $signed(uut.reg_file.registers[1]));
                $display("R2 = %0d (expected: 15)", $signed(uut.reg_file.registers[2]));
                $display("R3 = %0d", $signed(uut.reg_file.registers[3]));
                $display("R4 = %0d", $signed(uut.reg_file.registers[4]));
                $display("R5 = %0d", $signed(uut.reg_file.registers[5]));
                $display("R6 = %0d", $signed(uut.reg_file.registers[6]));
                $display("R7 = %0d", $signed(uut.reg_file.registers[7]));
                $display("");
                
                // Verify result
                if (uut.reg_file.registers[2] == 16'd15) begin
                    $display("========================================");
                    $display("TEST PASSED: R2 = 15 (1+2+3+4+5)");
                    $display("========================================");
                end else begin
                    $display("========================================");
                    $display("TEST FAILED: R2 = %0d (expected 15)", 
                             $signed(uut.reg_file.registers[2]));
                    $display("========================================");
                end
                
                $finish;
            end
        end
        
        $display("");
        $display("Simulation timeout - program did not halt");
        $finish;
    end
    
    // VCD dump for waveform viewing
    initial begin
        $dumpfile("risc16_tb.vcd");
        $dumpvars(0, risc16_tb);
    end

endmodule

