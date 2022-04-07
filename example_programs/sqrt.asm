; Compute the square root of a number, based on the Babylonian method.
; Uses a subroutine for division, with the self-modifying code technique
; demonstrated in subroutine.asm.

; Compute inital guess of the sqrt (S / 10)
	lda S            ; prepare for computing S / 10
        sta numer
        ldi 10
        sta denom
        ldi 0
        sta ans
	ldi a            ; setup return address
	sta div_ret + 1  ; address of the param of the jmp instruction
	jmp div          ; call division subroutine
a:	lda ans          ; subroutine returns here
        sta x            ; this is our inital guess for the sqrt

; Refine the guess of the sqrt
iter:
	lda S            ; prepare for computing S / x
	sta numer
	lda x
	sta denom
	ldi 0
	sta ans
	ldi b            ; setup return address
	sta div_ret + 1  ; address of the param of the jmp instruction
	jmp div          ; call division subroutine
b:	lda ans          ; subroutine returns here

        add x            ; prepare for computing (x + S / x) / 2
	sta numer
	ldi 2
	sta denom 
	ldi 0
	sta ans
	ldi c            ; setup return address
	sta div_ret + 1  ; address of the param of the jmp instruction
	jmp div          ; call division subroutine
c:	lda ans          ; subroutine returns here
        sta x
	out              ; display our refined guess

	sub x_prev       ; check for convergence
	jz end	
	lda x            ; not converged yet. x_prev = x and loop
	sta x_prev
	jmp iter

end:    hlt

; Subroutine for division
div:	lda numer         ; start computing numer / denom
	sub denom 
	jc div_iter
div_ret:
        jmp 0             ; we are done, jump to return address
div_iter:
	sta numer
	ldi 1             ; increment `ans` by 1
	add ans
	sta ans
	jmp div           ; loop

; Variables
S:	db 49             ; number of compute sqrt of
x:	db 0              ; current guess of the square root
x_prev: db 0              ; used to track convergence
numer:  db 0              ; first parameter for division subroutine
denom:  db 0              ; second parameter for division subroutine
ans:	db 0              ; result of the division subroutine
