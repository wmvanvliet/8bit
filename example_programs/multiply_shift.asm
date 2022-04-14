;
; Multiply two numbers (x and y) using left-shift
;
loop:	lda y
	shl
	sta y
	lda prod
	jnc a
	add x
	out
a:	shl
	sta prod
	jmp loop

x:	db 5
y:	db 7
prod:	db 0
