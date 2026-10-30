module alu_testbench;

    // Sinyal Tan?mlar?
    reg [15:0] A_in, B_in;
    reg [1:0] ALUOp_in;
    wire [15:0] Result_out;
    wire Zero_out;

    // Test Edilecek Modülün Örneklenmesi (DUT - Device Under Test)
    ALU_16bit DUT (
        .A(A_in),
        .B(B_in),
        .ALUOp(ALUOp_in),
        .ALU_Result(Result_out),
        .Zero(Zero_out)
    );

    // **********************************************
    // S?MÜLASYON BA?LANGICI VE TEST SENARYOLARI
    // **********************************************
    initial begin
        $display("ALU 16-Bit Test Basliyor...");

        // 1. TOPLAMA (ADD) Testi (ALUOp = 00)
        A_in = 16'h000A; // 10
        B_in = 16'h0005; // 5
        ALUOp_in = 2'b00;
        #10 $display("Saat=%t, Islem: ADD, A=%h, B=%h, Sonuc=%h, Zero=%b", $time, A_in, B_in, Result_out, Zero_out);
        // Beklenen Sonuç: 000F, Zero: 0

        // 2. ÇIKARMA (SUB) Testi (ALUOp = 01)
        A_in = 16'h0014; // 20
        B_in = 16'h0014; // 20
        ALUOp_in = 2'b01;
        #10 $display("Saat=%t, Islem: SUB, A=%h, B=%h, Sonuc=%h, Zero=%b", $time, A_in, B_in, Result_out, Zero_out);
        // Beklenen Sonuç: 0000, Zero: 1 (Zero bayra??n? test etmeli)
        
        // 3. AND Testi (ALUOp = 10)
        A_in = 16'hF00F;
        B_in = 16'h0F0F;
        ALUOp_in = 2'b10;
        #10 $display("Saat=%t, Islem: AND, A=%h, B=%h, Sonuc=%h, Zero=%b", $time, A_in, B_in, Result_out, Zero_out);
        // Beklenen Sonuç: 000F, Zero: 0

        // 4. OR Testi (ALUOp = 11)
        A_in = 16'hF000;
        B_in = 16'h000F;
        ALUOp_in = 2'b11;
        #10 $display("Saat=%t, Islem: OR, A=%h, B=%h, Sonuc=%h, Zero=%b", $time, A_in, B_in, Result_out, Zero_out);
        // Beklenen Sonuç: F00F, Zero: 0

        $display("\nALU Test Tamamlandi.");
        $finish; // Simülasyonu sonland?r
    end

endmodule
