;
; Multiply two numbers (x and y) using left-shift
;
loop:	lda y            ; Step 1: look at the most-significant bit of y
	add y            ; Left-shift y, sets the carry flag if MSB was a 1
	sta y            ; Store y with the MSB removed
	lda prod         ; Load intermediate result (the product)
	jc add_x         ; If the MSB was a 1, add x to the intermediate result
	jmp check_done   ; Else skip over the adding part
add_x:	add x            ; Add x to the intermediate result
	sta prod         ; Left-shift intermediate result
	
check_done:
	lda count        ; Decrease the counter
	sub one
	jz end           ; When counter reaches 0 program is done
	sta count        ; Store the decreased counter

shift_result:
	lda prod         ; Shift-left on the intemediate result
        add prod         ; 
	sta prod         ;
	jmp loop         ; Next iteration

end:
	lda prod
	out
	hlt

x:	db 17            ; We are computing 17 x 15
y:	db 15            ;
prod:	db 0             ; The (intermediate) result is stored here
count:  db 8             ; Counter
one:    db 1             ; A literal one
