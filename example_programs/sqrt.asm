; Compute the square root of a number, based on the Babylonian method.
; Uses a subroutine for division, with the self-modifying code technique
; demonstrated in subroutine.asm.

; Compute inital guess of the sqrt (S / 10)
	ld  [numer],[S]  ; prepare for computing S / 10
        ld  [denom],10
	ld  [ans],0
	jsr div
        ld  [x],[ans]     ; this is our inital guess for the sqrt
	out [x]          ; display our initial guess

; Refine the guess of the sqrt
iter:
	ld  [numer],[S]   ; prepare for computing S / x
	ld  [denom],[x]
	ld  [ans],0
	jsr div
	ld  a,[ans]

        add [x]           ; prepare for computing (x + S / x) / 2
	ld  [numer],a
	ld  [denom],2
	ld  [ans],0
	jsr div
	ld  a,[ans]
	ld  [x],a
	out [x]           ; display our refined guess

	sub [x_prev]      ; check for convergence
	jz  end	
	ld  [x_prev],[x]  ; not converged yet. x_prev = x and loop
	jp  iter

end:    hlt

; Subroutine for division
div:	ld  a,[numer]     ; start computing numer / denom
	sub [denom] 
	jc  div_iter
        ret               ; we are done, jump to return address
div_iter:
	ld  [numer],a
	ld  a,1           ; increment `ans` by 1
	add [ans]
	ld  [ans],a
	jp  div           ; loop

; Variables
	section .data
S:	db 49             ; number of compute sqrt of
x:	db 0              ; current guess of the square root
x_prev: db 0              ; used to track convergence
numer:  db 0              ; first parameter for division subroutine
denom:  db 0              ; second parameter for division subroutine
ans:	db 0              ; result of the division subroutine
