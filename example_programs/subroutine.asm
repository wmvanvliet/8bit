; Demonstrate calling a subroutine with the original instruction set.
; Works by self-modifying code
;
	ldi cont  ; set return address (cont)
	sta 14    ; overwrite parameter of the jump instruction

	ldi 1     ; setup argument for the subroutine
	jmp sub   ; call the subroutine

cont:	ldi 2     ; subroutine returns to here
	out
	hlt

; A subroutine that displays the current value of the A register
sub:
	out
	jmp 0     ; jump to the return address (param set on line #)
