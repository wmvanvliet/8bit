; Program that counts to 10 and then back to 0.
; And than back to 10. And then back again to 0.
; Forever.

increment:	
	lda x
	add one
	out
	sta x
	sub ten		; When we reach 10, start decrementing
	jz decrement
	jmp increment

decrement:
	lda x
	sub one
	out
	sta x
	jz increment	; When we reach 0, start incrementing
	jmp decrement

ten:	db 10		; Maximum value we are counting to
one:	db 1		; Counting step size
x:	db 0		; Current count
