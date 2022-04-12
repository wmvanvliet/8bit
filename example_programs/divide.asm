; Program to divide two numbers. Currently set to compute 14 / 2
;
; Credit to Edoardo's comment here:
; https://theshamblog.com/programs-and-more-commands-for-the-ben-eater-8-bit-breadboard-computer
;
loop:	lda numer
	sub denom
	jnc end     ; result was negative
	sta numer
	lda ans
	inc 1
	sta ans
	jmp loop

end:    lda ans
	out
	hlt

numer:	db 14
denom:	db 2
ans:	db 0
