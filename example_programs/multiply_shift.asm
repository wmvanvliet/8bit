;
; Multiply two numbers (x and y) using left-shift
;
        ld  b,17         ; We are computing 17 x 15
	ld  c,15
	ld  d,0          ; Product
	ld  e,8          ; Counter

loop:
	ld  a,c          ; Step 1: look at the most-significant bit of c
	add a            ; Left-shift, sets the carry flag if MSB was a 1
	ld  c,a          ; Store c with the MSB removed
	ld  a,d          ; Load intermediate result (the product)
	jnc check_done   ; If the MSB was a 0, skip over the adding part

        add b            ; Add x to the intermediate result
	ld  d,a          ; Left-shift intermediate result
	
check_done:
	ld  a,e          ; Decrease the counter
	sub 1
	jz  end          ; When counter reaches 0 program is done
	ld  e,a          ; Store the decreased counter

	ld  a,d          ; Shift-left on the intermediate result
        add a            ; 
	ld  d,a          ;
	jp  loop         ; Next iteration

end:
	out d
	hlt
