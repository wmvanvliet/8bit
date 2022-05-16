;
; Generate Fibonacci sequence
;
	ld  b,1
	ld  c,0

loop:
	out b
	ld  a,b
	add c
	jc  end
	ld  c,b
	ld  b,a
	jp  loop
end:
	hlt
