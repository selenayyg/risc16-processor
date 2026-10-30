//=============================================================================
// Sign Extend
// Extends 6-bit immediate to 16-bit signed value
//=============================================================================

module sign_extend (
    input  wire [5:0]  in,
    output wire [15:0] out
);

    // Sign extend: replicate MSB
    assign out = {{10{in[5]}}, in};

endmodule

//=============================================================================
// 2-to-1 MUX
//=============================================================================

module mux2to1 #(parameter WIDTH = 16) (
    input  wire [WIDTH-1:0] in0,
    input  wire [WIDTH-1:0] in1,
    input  wire             sel,
    output wire [WIDTH-1:0] out
);

    assign out = sel ? in1 : in0;

endmodule

//=============================================================================
// 4-to-1 MUX
//=============================================================================

module mux4to1 #(parameter WIDTH = 16) (
    input  wire [WIDTH-1:0] in0,
    input  wire [WIDTH-1:0] in1,
    input  wire [WIDTH-1:0] in2,
    input  wire [WIDTH-1:0] in3,
    input  wire [1:0]       sel,
    output reg  [WIDTH-1:0] out
);

    always @(*) begin
        case (sel)
            2'b00: out = in0;
            2'b01: out = in1;
            2'b10: out = in2;
            2'b11: out = in3;
            default: out = in0;
        endcase
    end

endmodule

//=============================================================================
// Shift Left 1 (for branch offset - multiply by 2)
//=============================================================================

module shift_left_1 (
    input  wire [15:0] in,
    output wire [15:0] out
);

    assign out = {in[14:0], 1'b0};

endmodule
