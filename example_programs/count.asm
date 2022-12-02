	ld a,0

count_up:
	out a
	inc
	cp 10
	jnz count_up

count_down:
	out a
	dec
	jnz count_down

	jp count_up
