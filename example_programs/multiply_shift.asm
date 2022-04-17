;
; Multiply two numbers (x and y) using left-shift
;
loop:	lda y            ; Step 1: look at the most-significant bit of y
	add y            ; Left-shift y, sets the carry flag if MSB was a 1
	sta y            ; Store y with the MSB removed
	lda prod         ; Load intermediate result (the product)
	jc add_x         ; If the MSB was a 1, add x to the intermediate result
	jmp shift_result ; Else skip over the adding part
add_x:	add x            ; Add x to the intermediate result
	out              ; Output our intermediate result
	
shift_result:
	sta prod         ; Left-shift intermediate result
        add prod         ; 
	sta prod         ;
	jmp loop         ; Next iteration

x:	db 17            ; We are computing 17 x 15
y:	db 15            ;
prod:	db 0             ; The (intermediate) result is stored here
