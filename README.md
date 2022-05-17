8bit breadboard computer simulator (extended memory)
====================================================

This is an assembler + simulator/emulator of [Ben Eater's 8bit breadboard computer](https://www.youtube.com/playlist?list=PLowKtXNTBypGqImE405J2565dvjafglHU) with Marijn's modifications added to it:

 - RAM upgraded to 256 bytes
 - Output control lines multiplexed using a 3->8 decoder
   - Register B out control line available
   - TR control line available that immediately resets the microstep counter
 - Microcode ROM address latched to only change on down-flank of clock
 - Vastly extended instruction set

For Ben Eater's original architecture, see the [main branch](https://github.com/wmvanvliet/8bit/tree/main) of this repo.

<img alt="Screenshot of the simulator in action" src="screenshot.jpg" width="600">


Installation
------------
Either clone the respository, or [download the code](https://github.com/wmvanvliet/8bit/archive/refs/heads/main.zip). On windows, you'll also need the [`windows-curses`](https://pypi.org/project/windows-curses/) package to display the user interface (on other platforms, `curses` is included in the standard lib).

Usage
-----
Write your test program in assembler and run it through the simulator.
```
python simulator.py example_programs/test.asm
```

If you want a closer look at the assembler output:
```
python assembler.py example_programs/test.asm
```


Programming the computer using assembly language
------------------------------------------------

This simulator reads its memory contents from a text file with the `.asm` extension. The file should contain programming code written in assembler.

Supported assembler instructions:

```
nop        No operation
ld  #,##   Load memory contents of ## into #
add #      Add # to the accumulator, set flags
sub #      Subtract # from the accumulator, set flags
adc #      Add # as well as the carry flag to the accumulator, set flags
sbc #      Subtract # as well as the carry flag from the accumulator, set flags
jp  #      Jump to memory location #
jc  #      Jump to memory location # if the carry flag is set
jz  #      Jump to memory location # if the zero flag is set
jnc #      Jump to memory location # if the carry flag is not set
jnz #      Jump to memory location # if the zero flag is not set
out #      Output # on the 7-segment display
hlt        Halt the CPU, end of program
```

Where `#` can be the accumulator `a`, any of the virtual registers `b`, `c`, `d`, `e`, `f`, `g`, `h`, a direct value (e.g. `42`) or a memory contents of a label (e.g. `[my_label]`).

The assembler also supports comments using the `;` character, writing raw values with `db` and labels. Here is an example assembler program that uses some features of the assembler:
```asm
;
; Test program that adds two numbers
;
	ld a,[x]  ; Load the memory contents at the (x) label into the accumulator
	add [y]   ; Add the memory contents at the (y) label to the value the accumulator
	out a     ; Display the value in the accumulator on the 7-segment display.
	hlt       ; Halt the clock. This signals the end of the program.

x:         ; Label that marks memory location (x)
	db 28  ; Write the literatal value "28" at this memory location.
y:         ; Label that marks memory location (y)
	db 14  ; Write the literal value "14" at this memory location.
``` 

More example programs can be found in the `example_programs/` folder of this repository.
