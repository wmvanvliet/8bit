;
; Test program that adds two numbers
;
	ld  a, 28  ; a = 28
	add a, 14  ; a += 14
	out a      ; Display the value in register "A" on the 7-segment display.
	hlt        ; Halt the clock. This signals the end of the program.
