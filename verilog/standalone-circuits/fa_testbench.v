// fa_testbench.v kodu (Testbench - Simülasyonu Ba?latan Dosya)
module fa_testbench;
    reg A, B, C_IN;
    wire Sum, C_OUT;

    // DUT (Device Under Test): full_adder_1bit modülünü ça??r
    full_adder_1bit DUT (.A(A), .B(B), .C_IN(C_IN), .Sum(Sum), .C_OUT(C_OUT));

    initial begin
        $display("FULL ADDER TEST BASLIYOR");
        A = 0; B = 0; C_IN = 0; #10; // 0+0+0 = 00
        A = 1; B = 0; C_IN = 0; #10; // 1+0+0 = 01
        A = 1; B = 1; C_IN = 0; #10; // 1+1+0 = 10
        A = 1; B = 1; C_IN = 1; #10; // 1+1+1 = 11
        $display("FULL ADDER TEST TAMAMLANDI");
        $finish;
    end
    
    always @(A or B or C_IN) begin
        $monitor("Zaman:%d A:%b B:%b Cin:%b Sum:%b Cout:%b", $time, A, B, C_IN, Sum, C_OUT);
    end
endmodule
