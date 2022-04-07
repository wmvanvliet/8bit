;
; Demonstrate calling a subroutine with the original instruction set.
; Works through self-modifying code
;
	ldi cont1       ; set return address (cont1)
	sta sub_ret + 1 ; overwrite parameter of return jump instruction of subroutine
	ldi 1           ; setup argument for the subroutine
	jmp sub         ; call the subroutine

cont1:  ldi cont2       ; set return address (cont2)
	sta sub_ret + 1 ; overwrite parameter of return jump instruction of subroutine
	ldi 2           ; setup argument for the subroutine
	jmp sub         ; call the subroutine

cont2:	ldi 3           ; subroutine returns to here
	out
	hlt

; A subroutine that displays the current value of the A register
sub:
	out
sub_ret:
	jmp 0           ; jump to the return address (param set at runtime)
