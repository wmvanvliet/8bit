; Divides two positive numbers.
loop:	lda numer
	sub denom
	jc inc     ; result was non-negative
	jmp end

inc:
	sta numer
	lda ans
	add one
	sta ans
	jmp loop

end:    lda ans
	out
	hlt

one:    db 1
numer:	db 8 
denom:	db 8
ans:	db 0
