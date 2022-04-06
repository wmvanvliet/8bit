; Compute the square root of a number, based on the Babylonian method.
iter:
	lda S      ; prepare for computing S / x
	sta numer
	lda x
	sta denom
	ldi 0
	sta ans
	
S_x:	lda numer  ; start computing S / x
	sub denom 
	jc S_x_inc
	jmp S_x_e   ; result was negative

S_x_inc:
	sta numer
	ldi 1    ; increment `ans` by 1
	add ans
	sta ans
	jmp S_x

S_x_e:  lda ans
        add x

	sta numer  ; prepare for computing (x + S / x) / 2
	ldi 2
	sta denom 
	ldi 0
	sta ans

S_2:	lda numer  ; start computing (x + S / x) / 2
	sub denom 
	jc S_2_inc
	jmp S_2_e 

S_2_inc:
	sta numer
	ldi 1
	add ans
	sta ans
	jmp S_2

S_2_e:	lda ans
	sta x
	out

	sub x_prev ; Check for convergence
	jz end	

	lda x      ; Not converged yet. x_prev = x and loop
	sta x_prev
	jmp iter

end:    hlt

S:	db 49  ; number of compute sqrt of
x:	db 5   ; initial guess of the square root
x_prev: db 0
numer:  db 0
denom:  db 0
ans:	db 0
