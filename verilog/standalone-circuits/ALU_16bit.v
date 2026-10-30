module ALU_16bit (
    input [15:0] A,             // 16-bit birinci giri?
    input [15:0] B,             // 16-bit ikinci giri?
    input [1:0] ALUOp,          // 2-bit ALU Kontrol Sinyali: 00=ADD, 01=SUB, 10=AND, 11=OR
    output [15:0] ALU_Result,   // 16-bit ALU Sonucu
    output Zero                 // S?f?r bayra?? (Sonuç 0 ise 1)
);

    reg [15:0] result_reg;

    always @(*) begin
        case (ALUOp)
            2'b00: begin // Toplama (ADD)
                result_reg = A + B;
            end
            2'b01: begin // Ç?karma (SUB)
                result_reg = A - B;
            end
            2'b10: begin // Mant?ksal AND
                result_reg = A & B;
            end
            2'b11: begin // Mant?ksal OR
                result_reg = A | B;
            end
            default: begin
                result_reg = 16'hXXXX; // Tan?ms?z durum
            end
        endcase
    end

    // ALU Sonucu
    assign ALU_Result = result_reg;

    // Zero bayra??n? hesaplama (Sonuç s?f?r ise Zero=1)
    assign Zero = (ALU_Result == 16'h0000) ? 1'b1 : 1'b0;

endmodule
