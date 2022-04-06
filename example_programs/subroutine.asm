; Demonstrate calling a subroutine with the original instruction set.
; Works by self-modifying code
;
	ldi cont    ; set return address (cont)
	add jmp_op  ; set jmp instruction
	sta sub_ret ; overwrite return jump instruction of subroutine

	ldi 1       ; setup argument for the subroutine
	jmp sub     ; call the subroutine

cont:	ldi 2       ; subroutine returns to here
	out
	hlt

; A subroutine that displays the current value of the A register
sub:
	out
sub_ret:
	jmp 0       ; jump to the return address (param set on line #)

; Data
jmp_op: db 96
