; Program to divide two numbers. Currently set to compute 14 / 2
;
; Credit to Edoardo's comment here:
; https://theshamblog.com/programs-and-more-commands-for-the-ben-eater-8-bit-breadboard-computer
;
loop:	lda numer
	sub denom
	jc inc     ; result was non-negative
	jmp end

inc:
	sta numer
	ldi 1
	add ans
	sta ans
	jmp loop

end:    lda ans
	out
	hlt

numer:	db 14
denom:	db 2
ans:	db 0
