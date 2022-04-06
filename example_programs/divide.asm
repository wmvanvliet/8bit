; Program to divide two numbers. Currently set to compute 14 / 2
;
; Credit to Edoardo's comment here:
; https://theshamblog.com/programs-and-more-commands-for-the-ben-eater-8-bit-breadboard-computer
;
loop:
	lda dividend
	sub divisor
	jz end
	jc inc
	jmp end
inc:
	sta dividend
	ldi 1
	add ans
	sta ans
	jmp loop
end:
	lda ans
	out
	hlt
ans:
	db 1   ; to be set to 1 at each start
divisor:
	db 2
dividend:
	db 14
