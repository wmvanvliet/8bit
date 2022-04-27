; Program to divide two numbers. Currently set to compute 14 / 2
;
; Credit to Edoardo's comment here:
; https://theshamblog.com/programs-and-more-commands-for-the-ben-eater-8-bit-breadboard-computer
;
loop:	ld  a,numer
	sub a,denom
	jc  inc     ; result was non-negative
	jp  end

inc:
	ld  numer,a
	ld  a,1
	add a,ans
	ld  ans,a
	jp  loop

end:    ld  a,ans
	out a
	hlt

numer:	db 14
denom:	db 2
ans:	db 0
