;
; Generate Fibonacci sequence
;
	ldi 1
	sta x
	ldi 0
loop:
	sta y
	out
	lda x
	add y
	sta x
	out 
	lda y
	add x 
	jc end
	jmp loop
end:
	hlt
x:
	db 0
y:
	db 0
