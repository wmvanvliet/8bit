readline:
	jsr readnum
	ld [side1],[num]

	cp 0
	jz end
	
	jsr readnum
	ld [side2],[num]

	jsr readnum
	ld [side3],[num]

	ld a,[side1]
	cp [side2]
	jnc side2_lt_side1
	ld [side1],[side2]
	ld [side2],a
side2_lt_side1:
	ld a,[side3]
	cp [side2]
	jc side3_lt_side2
	ld [side3],[side2]
	ld [side2],a
side3_lt_side2:
	ld a,[side1]
	add [side2]
	add a
	ld [ribbon],a

	ld b,0
	ld c,[side1]
	ld d,[side2]
	jsr multiply
	ld b,e
	ld c,f
	ld d,[side3]
	jsr multiply
	ld [vol_h],e
	ld [vol_l],f

	out [side1]
	out [side2]
	out [side3]
	out [ribbon]
	out [vol_h]
	out [vol_l]

	ld a,[vol_l]
	add [ribbon]
	ld [vol_l],a
	ld a,[vol_h]
	adc 0
	ld [vol_h],a

	out [vol_h]
	out [vol_l]
	out -1

	ld a,[grand0]
	add [vol_l]
	ld [grand0],a
	ld a,[grand1]
	adc [vol_h]
	ld [grand1],a
	ld a,[grand2]
	adc 0
	ld [grand2],a
	ld a,[grand3]
	adc 0
	ld [grand3],a

	jp readline
end:
	out [grand3]
	out [grand2]
	out [grand1]
	out [grand0]
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

;
; Multiply an 16-bit number (b and c) with an 8-bit number (d) using
; left-shift, producing an 16-bit result (e and f).
; Inputs:
;   b: upper 8-bits of the first number to multiply
;   c: lower 8-bits of the first number to multiply
;   d: second number to multiply (gets destroyed)
; Returns:
;   e: upper 8 bits of the result
;   f: lower 8 bits of the result
; Uses:
;   a,d,e,f,h
multiply:
	ld  e,0          ; Product, upper 8 bits
	ld  f,0          ; Product, lower 8 bits
	ld  h,8          ; Counter

multiply.loop:
	ld  a,d          ; Step 1: look at the most-significant bit of d
	add a            ; Left-shift, sets the carry flag if MSB was a 1
	ld  d,a          ; Store d with the MSB removed
	jnc multiply.check_done   ; If the MSB was a 0, skip over the adding part

	ld  a,f          ; Load intermediate result (the product)
        add c            ; Step 2: add b and c to the intermediate result
	ld  f,a          
	ld  a,e
	adc b
	ld  e,a
	
multiply.check_done:
	ld  a,h          ; Decrease the counter
	dec
	jz  multiply.ret ; When counter reaches 0 program is done
	ld  h,a          ; Store the decreased counter

	ld  a,f          ; Shift-left on the intermediate result
        add a
	ld  f,a
	ld  a,e
	adc a
	ld  e,a
	jp  multiply.loop

multiply.ret:
	ret

	section .data
num:	  db 0
side1:	  db 0
side2:	  db 0
side3:	  db 0
vol_h:    db 0
vol_l:    db 0
ribbon:   db 0
grand3:	  db 0
grand2:	  db 0
grand1:	  db 0
grand0:	  db 0
