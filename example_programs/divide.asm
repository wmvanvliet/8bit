; Divides two positive numbers, also computes the remainder.
; Works in signed integer modes, so numbers need to be <= 127.
loop:	lda numer
	sta remain
	sub denom
	sta numer
	add check  ; check the sign bit of the result
	jc end     ; result was negative
	lda ans
	add one
	sta ans
	jmp loop
end:    lda ans
        out
	hlt
one:    db 1
check:	db 64  ; checks for the sign bit
numer:	db 35 
denom:	db 8
ans:	db 0
remain: db 0
