; Demonstrate calling a subroutine
	ldi cont  ; load the return address (cont) into (ret)
	sta ret
	ldi 1     ; setup argument for the subroutine
	jmp sub   ; call the subroutine
cont:	ldi 2     ; subroutine returned to here
	out
	hlt

; A subroutine that displays the current value of the A register
sub:
	out
	ji ret    ; indirect jump to whatever return address was setup

; Data
ret:    db 0      ; return address
