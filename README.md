8bit breadboard computer simulator
==================================

<img src="screenshot.jpg" alt="Screenshot of the simulator in action>

Write your test program in assembler and run it through the simulator.
```
python simulator.py test.asm
```


If you want a closer look at the assembler output:
```
python assembler.py test.asm
```


Supported assembler instructions:

```
nop     No operation
lda #   Load memory contents at # into register A
add #   Add memory contents at # to register A
sub #   Subtract memory contents at # from register A
sta #   Store contents of register A at memory location #
ldi #   Load the value # into register A
jmp #   Jump to memory location #
jc #    Jump to memory location # if the carry flag is set
jz #    Jump to memory location # if the zero flag is set
out     Output contents of register A
hlt     Halt the CPU, end of program
```

The assembler also supports writing raw values with `db` and labels:
```asm
;
; Test program that adds two numbers
;
	lda a
	add b
	out
	hlt

a:
	db 28
b:
	db 14
``` 
