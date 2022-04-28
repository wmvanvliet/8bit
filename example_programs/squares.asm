; Challange issued by /u/Positive_Pie6876 on /r/beneater:
; https://www.reddit.com/r/beneater/comments/ucz5fo
;
; Compute x² for x = [1..15]
;
; The trick to this is this equation:
;       a² - b² = (a - b)(a + b)
;
; Since we are computing consequtive squares (a - b) is always 1.
; If we have just computed 8² = 64 and we want 9²,
; all we need to compute is: 64 + (9 + 8),
; which we actually compute as 9 + 9 - 1 + 64.
;
loop:	lda x       ; Increase 'x' by 1
	add one
	sta x       ; Compute the square of x
	add x       ; x + x - 1 + square
	sub one
	add square
	jc  end     ; If we are overflowing, end the program
	out         ; Display the result
	sta square  ; Keep track of the last computed square
	jmp loop    ; Compute the next square
end:    hlt
x:      db 0        ; The square we are computing
square: db 0        ; The last square we computed
one:    db 1        ; A literal "1"
