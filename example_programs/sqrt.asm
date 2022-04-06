; Compute the square root of a number, based on the Babylonian method.
; Uses a subroutine for division, with the self-modifying code technique
; demonstrated in subroutine.asm.
iter:
	lda S      ; prepare for computing S / x
	sta numer
	lda x
	sta denom
	ldi 0
	sta ans
	ldi a      ; setup return address
	sta 61     ; address of the param of the jmp instruction
	jmp div    ; call division subroutine
a:	lda ans
        add x

	sta numer  ; prepare for computing (x + S / x) / 2
	ldi 2
	sta denom 
	ldi 0
	sta ans
	ldi b      ; setup return address
	sta 61     ; address of the param of the jmp instruction
	jmp div    ; call division subroutine
b:	lda ans
        sta x
	out
	sub x_prev ; Check for convergence
	jz end	

	lda x      ; Not converged yet. x_prev = x and loop
	sta x_prev
	jmp iter

end:    hlt


; Subroutine for division
div:	lda numer  ; start computing numer / denom
	sub denom 
	jc div_i
	jmp 0      ; we are done, jump to return address
div_i:
	sta numer
	ldi 1      ; increment `ans` by 1
	add ans
	sta ans
	jmp div    ; loop

; Variables
S:	db 49  ; number of compute sqrt of
x:	db 1   ; initial guess of the square root
x_prev: db 0
numer:  db 0
denom:  db 0
ans:	db 0
