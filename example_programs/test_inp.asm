;
; Test program that reads two numbers from streaming input and adds them
;
	inp     ; Load first number into accumulator
	ld b,a  ; Store it in register b
	inp     ; Load second number into accumulator
	add b   ; Add numbers together
	out a   ; Output on the display
	hlt
