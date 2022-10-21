; Challenge issued by /u/Positive_Pie6876 on /r/beneater:
; https://www.reddit.com/r/beneater/comments/ucz5fo
;
; Compute x² for x = [1..15]
;
; The trick to this is this equation:
;       a² - b² = (a - b)(a + b)
;
; Since we are computing consecutive squares (a - b) is always 1.
; If we have just computed 8² = 64 and we want 9²,
; all we need to compute is: 64 + (9 + 8),
; which we actually compute as 9 + 9 - 1 + 64.
;
	ld  b,0
	ld  c,0
loop:	
	ld  a,b     ; Increase 'b' by 1
	inc
	ld  b,a
	add b       ; b + b - 1 + c
	dec
	add c
	jc  end     ; If we are overflowing, end the program
	out a       ; Display the result
	ld  c,a     ; Keep track of the last computed square
	jp  loop    ; Compute the next square

end:    hlt
