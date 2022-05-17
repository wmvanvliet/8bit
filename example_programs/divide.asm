; Program to divide two numbers. Currently set to compute 14 / 2
;
; Credit to Edoardo's comment here:
; https://theshamblog.com/programs-and-more-commands-for-the-ben-eater-8-bit-breadboard-computer
;
	ld  b,14    ; numerator
	ld  c,2     ; denominator
	ld  d,0     ; answer

loop:	ld  a,b
	sub c
	jnc end     ; result was non-negative

	ld  b,a
	ld  a,1
	add d
	ld  d,a
	jp  loop

end:    out d
	hlt
