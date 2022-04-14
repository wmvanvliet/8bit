;
; Multiply two numbers (x and y) using left-shift
;
loop:	lda y
	add y
	sta y
	lda prod
	jc a
	jmp b
a:	add x
	out
b:	sta prod
        add prod
	sta prod
	jmp loop

x:	db 17
y:	db 15
prod:	db 0
