readline:
	jsr readnum
	ld [side1],[num]

	cp 0
	jz end
	
	jsr readnum
	ld [side2],[num]

	ld b,[side1]
	ld c,[side2]
	jsr multiply
	ld [area1_h],d
	ld [area1_l],e

	jsr readnum
	ld [side3],[num]

	ld b,[side3]
	ld c,[side2]
	jsr multiply
	ld [area2_h],d
	ld [area2_l],e

	ld c,[side1]
	jsr multiply
	ld [area3_h],d
	ld [area3_l],e

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
	ld b,[side1]
	ld c,[side2]
	jsr multiply
	ld [slack_h],d
	ld [slack_l],e
	
	; out [side1]
	; out [side2]
	; out [side3]
	; out [area1_h]
	; out [area1_l]
	; out [area2_h]
	; out [area2_l]
	; out [area3_h]
	; out [area3_l]
	; out [slack_h]
	; out [slack_l]

	ld [total_l],[area1_l]
	ld [total_h],[area1_h]

	ld a,[area2_l]
	add [total_l]
	ld [total_l],a
	ld a,[area2_h]
	adc [total_h]
	ld [total_h],a

	ld a,[area3_l]
	add [total_l]
	ld [total_l],a
	ld a,[area3_h]
	adc [total_h]
	ld [total_h],a

	ld a,[total_l]
	add a
	ld [total_l],a
	ld a,[total_h]
	adc a
	ld [total_h],a

	ld a,[total_l]
	add [slack_l]
	ld [total_l],a
	ld a,[total_h]
	adc [slack_h]
	ld [total_h],a

	; out [total_h]
	; out [total_l]
	; out -1

	ld a,[grand0]
	add [total_l]
	ld [grand0],a
	ld a,[grand1]
	adc [total_h]
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
; Multiply two 8-bit numbers (b and c) using left-shift, producing an 16-bit
; result.
; Inputs:
;   b: first number to multiply
;   c: second number to multiply (gets destroyed)
; Returns:
;   d: upper 8 bits of the result
;   e: lower 8 bits of the result
; Uses:
;   a,c,d,e,h
multiply:
	ld  d,0          ; Product, upper 8 bits
	ld  e,0          ; Product, lower 8 bits
	ld  h,8          ; Counter

multiply.loop:
	ld  a,c          ; Step 1: look at the most-significant bit of c
	add a            ; Left-shift, sets the carry flag if MSB was a 1
	ld  c,a          ; Store c with the MSB removed
	jnc multiply.check_done   ; If the MSB was a 0, skip over the adding part

	ld  a,e          ; Load intermediate result (the product)
        add b            ; Step 2: add b to the intermediate result
	ld  e,a          
	ld  a,d
	adc 0
	ld  d,a
	
multiply.check_done:
	ld  a,h          ; Decrease the counter
	dec
	jz  multiply.ret ; When counter reaches 0 program is done
	ld  h,a          ; Store the decreased counter

	ld  a,e          ; Shift-left on the intermediate result
        add a
	ld  e,a
	ld  a,d
	adc a
	ld  d,a
	jp  multiply.loop

multiply.ret:
	ret

	section .data
num:	  db 0
side1:	  db 0
side2:	  db 0
side3:	  db 0
area1_h:  db 0
area1_l:  db 0
area2_h:  db 0
area2_l:  db 0
area3_h:  db 0
area3_l:  db 0
slack_h:  db 0
slack_l:  db 0
total_h:  db 0
total_l:  db 0
grand3:	  db 0
grand2:	  db 0
grand1:	  db 0
grand0:	  db 0
