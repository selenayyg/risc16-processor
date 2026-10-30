// full_adder_1bit.v kodu
module full_adder_1bit(A, B, C_IN, Sum, C_OUT);
    input A, B, C_IN;
    output Sum, C_OUT;
    wire S1, C1, C2;
    xor(S1, A, B);
    xor(Sum, S1, C_IN);
    and(C1, A, B);
    and(C2, C_IN, S1);
    or(C_OUT, C1, C2);
endmodule
