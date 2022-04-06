; Divides two positive numbers, can deal with a remainder.
; Works in signed integer modes, so numbers need to be <= 127.
loop:	lda numer
	sub denom
	sta numer
	add check  ; check the sign bit of the result
	jc end     ; result was negative
	lda res
	add one
	sta res
	jmp loop
end:    lda res
        out
	hlt
one:    db 1
check:	db 64  ; checks for the sign bit
numer:	db 35 
denom:	db 8
res:	db 0
