loop:
	out [floor]
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
	ld [floor],a
	jp loop

floor:	db 0
