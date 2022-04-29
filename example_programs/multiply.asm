;
; Multiply two numbers using a loop
;
        ld  b,5
	ld  c,7
loop:	ld  a,d
        add b
	ld  d,a
	ld  a,c
	sub 1
	jz  end
	ld  c,a
	jp  loop
end:    out c
	hlt
