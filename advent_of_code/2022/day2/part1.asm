	ld b,0
	ld c,0

begin:	
	nop
	nop
	nop
	inp
	cp 10  ; newline
	jz begin
	cp 65  ; 'A'
	jz opp_rock
	cp 66  ; 'B'
	jz opp_paper
	cp 67  ; 'C'
	jz opp_scissor
	jp end

opp_rock:
	inp
	nop
	nop
	inp
	cp 88  ; 'X'
	jz tie
	cp 89  ; 'Y'
	jz win
	cp 90  ; 'Z'
	jz loss
	jp end

opp_paper:
	inp
	nop
	nop
	inp
	cp 88  ; 'X'
	jz loss
	cp 89  ; 'Y'
	jz tie
	cp 90  ; 'Z'
	jz win
	jp end

opp_scissor:
	inp
	nop
	nop
	inp
	cp 88  ; 'X'
	jz win
	cp 89  ; 'Y'
	jz loss
	cp 90  ; 'Z'
	jz tie
	jp end

tie:
	sub 87
	add 3
	out a
	jp update_total

win:
	sub 87
	add 6
	out a
	jp update_total

loss:
	sub 87
	out a
	jp update_total

update_total:
	add c
	ld c,a
	ld a,0
	adc b
	ld b,a
	jp begin

end:
	out b
	jsr delay
	out c
	jsr delay
	jp end

delay:
	ld a,100
loop:
	dec
	jnz loop
	ret
