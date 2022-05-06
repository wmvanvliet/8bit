;
; Demonstrate calling a subroutine.
;
	ld  a,1
	jsr sub
	ld  a,2
	jsr sub
	ld  a,3
	jsr sub
	hlt

; A subroutine that displays the current value of the A register
sub:	out a
	ret
