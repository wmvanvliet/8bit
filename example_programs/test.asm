;
; Test program that adds two numbers
;
	ld  a,[x]  ; Load the memory contents at the [x] label into register "A".
	add [y]    ; Add the memory contents at the [y] label to the value in register "A".
	out a      ; Display the value in register "A" on the 7-segment display.
	hlt        ; Halt the clock. This signals the end of the program.

	section .data
x:                 ; Label that marks memory location (x)
	db 28      ; Write the literatal value "28" at this memory location.
y:                 ; Label that marks memory location (y)
	db 14      ; Write the literal value "14" at this memory location.
