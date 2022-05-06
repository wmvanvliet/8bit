;
; Multiply two numbers using a loop
;
; computes d = b * c
        ld  b,5  ; 5 x 7
	ld  c,7
	ld  d,0  ; result
loop:	ld  a,d
        add b
	ld  d,a
	ld  a,c
	sub 1
	jz  end
	ld  c,a
	jp  loop
end:    out d
	hlt
