;
; Multiply two numbers using a loop (Ben Eater's design)
;
loop:	lda prod
	add x
	sta prod
	lda y
	sub one
	jz end
	sta y
	jmp loop
end:    lda prod
	out
	hlt
one:	db 1
x:	db 5
y:	db 7
prod:	db 0
