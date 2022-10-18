;
; Multiply two 8-bit numbers (x and y) using left-shift, producing an 16-bit
; result.
;
        ld  b,55         ; We are computing 55 x 223
	ld  c,223
	ld  d,0          ; Product, upper 8 bits
	ld  e,0          ; Product, lower 8 bits
	ld  h,8          ; Counter

loop:
	ld  a,c          ; Step 1: look at the most-significant bit of c
	add a            ; Left-shift, sets the carry flag if MSB was a 1
	ld  c,a          ; Store c with the MSB removed
	jnc check_done   ; If the MSB was a 0, skip over the adding part

	ld  a,e          ; Load intermediate result (the product)
        add b            ; Step 2: add b to the intermediate result
	ld  e,a          
	ld  a,d
	adc 0
	ld  d,a
	
check_done:
	ld  a,h          ; Decrease the counter
	dec
	jz  end          ; When counter reaches 0 program is done
	ld  h,a          ; Store the decreased counter

	ld  a,e          ; Shift-left on the intermediate result
        add a            ; 
	ld  e,a          ;
	ld  a,d
	adc a
	ld  d,a          ;
	jp  loop         ; Next iteration

end:
	out d
	out e
	hlt
