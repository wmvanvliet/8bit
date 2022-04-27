;
; Test program that adds two numbers
;
	ld  a, 28        ; a = 28
	ld  b, data1     ; b = 42
	ld  c, b         ; c = b = 42
	ld  data2, 10    ; data2 = 10
	ld  data3, a     ; data3 = a = 28
	ld  data4, data2 ; data4 = data2 = 10
	out a            ; Display the value in register "A" on the 7-segment display.
	out b            ; Display the value in register "B" on the 7-segment display.
	out c            ; Display the value in register "C" on the 7-segment display.
	out data1        ; Display the value at memory adress "data1" on the 7-segment display.
	out data2        ; Display the value at memory adress "data2" on the 7-segment display.
	out data3        ; Display the value at memory adress "data3" on the 7-segment display.
	out data4        ; Display the value at memory adress "data4" on the 7-segment display.
	hlt              ; Halt the clock. This signals the end of the program.

data1:  db 42
data2:  db 10
data3:  db 0
data4:  db 0
