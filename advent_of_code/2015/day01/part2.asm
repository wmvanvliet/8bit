loop:
	ld a,[pos_l]
	inc
	ld [pos_l],a
	ld a,[pos_h]
	adc 0
	ld [pos_h],a
	inp
	cp 40 ; (
	jz up
	cp 41 ; )
	jz down
	hlt

up:
	ld a,[floor]
	inc
	ld [floor],a
	jp loop

down:
	ld a,[floor]
	dec
	jnc end
	ld [floor],a
	jp loop

end:
	out [pos_h]
	out [pos_l]
	hlt

floor:	db 0
pos_h:	db 0  ; upper 8-bits
pos_l:  db 0  ; lower 8-bits
