;
; Test shifting instruction
;
	ld  a,1
	out a  ; 1
	add a
	out a  ; 2
	add a
	out a  ; 4
	add a
	out a  ; 8
	add a
	out a  ; 16
	add a
	out a  ; 32
	add a
	add a  ; 128
	add a  ; 0 + carry
	out a
	hlt
