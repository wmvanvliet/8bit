;
; Test program that adds two numbers
;
	ld  a, 28    ; a = 28
	ld  b, data1 ; b = 42
	out a        ; Display the value in register "A" on the 7-segment display.
	out b        ; Display the value in register "B" on the 7-segment display.
	out data2    ; Display the value at memory adress "data2" on the 7-segment display.
	hlt          ; Halt the clock. This signals the end of the program.

data1:  db 42
data2:  db 10
