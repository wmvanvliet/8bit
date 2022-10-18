readline:
	jsr readnum
	ld a,[num]
	cp 0
	jz end
	ld [side1],[num]
	out [side1] 
	jsr readnum
	ld [side2],[num]
	out [side2]
	jsr readnum
	ld [side3],[num]
	out [side3]
	ld a,[side1]
	add [side2]
	out -1
	jp readline
end:
	hlt

;
; Read an ASCII number from streaming input
; Returns:
;   [num]: the number
;   a: the next input read from the stream
; Uses:
;   a,b,h
readnum:
        ld [num],0
readnum.loop:
	inp
	cp 58
	jc readnum.ret
	cp 48
	jnc readnum.ret
	sub 48
	ld b,a
readnum.parse:
	ld a,[num]
	add a
	ld h,a
	add a
	add a
	add h
	ld [num],a

	ld a,b
	add [num]
	ld [num],a
	jp readnum.loop
readnum.ret:
	ret

	section .data
num:	db 0
side1:  db 0
side2:  db 0
side3:  db 0
area1:  db 0
area2:  db 0
area3:  db 0
