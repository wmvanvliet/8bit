; 16-bit sqrt program. The computation method is to try all possible squares
; until we find the one that matches.
;
; Inspired by the challenge issued by /u/Positive_Pie6876 on /r/beneater:
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
; We do this in 16 bit!
;
	ld  b,0
	ld  c,0
	ld  d,0
	ld  e,238
	ld  f,81

loop:	
	ld  a,b     ; Increase 'b' by 1
	inc
	jc  end     ; If we are overflowing, end the program
	ld  b,a
	out b

	ld  a,d     ; cd = b + b - 1 + cd
	add b       
	ld  d,a
	ld  a,c
	adc 0
	ld  c,a
	ld  a,b
	dec
	add d
	ld  d,a
	ld  a,c
	adc 0
	ld  c,a

	ld  a,c	    ; check if we have found the sqrt
	cp  e
	jnz loop
	ld  a,d
	cp  f
	jnz loop

end:
	out b
	hlt
