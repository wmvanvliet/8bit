;
; Test program that adds two numbers
;
	lda a  ; Load the memory contents at the (a) label into register "A".
	add b  ; Add the memory contents at the (b) label to the value in register "A".
	out    ; Display the value in register "A" on the 7-segment display.
	hlt    ; Halt the clock. This signals the end of the program.

a:         ; Label that marks memory location (a)
	db 28  ; Write the literatal value "28" at this memory location.
b:         ; Label that marks memory location (b)
	db 14  ; Write the literal value "14" at this memory location.
