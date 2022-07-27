8bit breadboard computer simulator (extended memory)
====================================================

This is an assembler + simulator/emulator of [Ben Eater's 8bit breadboard computer](https://www.youtube.com/playlist?list=PLowKtXNTBypGqImE405J2565dvjafglHU) with its RAM upgraded to 256 bytes following the instructions by [/u/MironV](https://www.reddit.com/r/beneater/comments/h8y28k).
The program is meant to be run on the command line, providing a text interface that uses unicode characters for drawing boxes and LEDs.

Use this program to:
 - Write programs in assembly and run/debug them in the comfort of a laptop or desktop machine.
 - Assemble a program into a binary listing that is ready to be programmed on the real machine using the DIP switches.
 - Generate the microcode EEPROM binary contents ready to be written to an actual EEPROM chip.
 - Make modifications to the microcode (for example, you can add more instructions) and see the result in the stimulator.
 - Experiment with modifications to the simulated hardware before commiting to build it on the breadboards.

<img alt="Screenshot of the simulator in action" src="screenshot.jpg" width="600">

It has been tested on Windows and Linux, and is assumed to work just fine on other operating systems as long as they support the [curses](https://docs.python.org/3/howto/curses.html) module in the Python standard library.
The simulation is [subcycle-accurate](https://emulation.gametechwiki.com/index.php/Emulation_accuracy#Subcycle_accuracy), meaning that the registers, control lines, RAM and 7-segment display are simulated during both the down-going and up-going flank of the clock.
Making modifications to the code to match your specific breadboard build is meant to be easy.
The code is short and to the point: there are only 4 short python files.


For Ben Eater's original architecture, see the [main branch](https://github.com/wmvanvliet/8bit/tree/main) of this repo.



Installation
------------
Either clone the respository, or [download the code](https://github.com/wmvanvliet/8bit/archive/refs/heads/main.zip). Run the `simulator.py` script using [Python](https://python.org) (version 3.5 or higher). On windows, you'll also need the [`windows-curses`](https://pypi.org/project/windows-curses/) package to display the user interface (on other platforms, `curses` is included in the standard lib).

Usage
-----
Write your test program in assembler and run it through the simulator:
```
python simulator.py example_programs/test.asm
```

Run your program without the interface, producing just the values sent to the 7-segment display:
```
python simulator.py --no-interface example_programs/test.asm
```

Assemble your program into a binary listing that you can program on the real machine using the DIP switches:
```
python assembler.py example_programs/test.asm
```

Write the microcode EEPROM contents to a binary file that you can use with EEPROM programmers:
```
python microcode.py binary_blob_for_EEPROM.bin
```

Load the microcode EEPROM contents from a binary file into the simulator, and run a test program:
```
python simulator.py --microcode binary_blob_for_EEPROM.bin example_programs/test.asm
```

Run the `simulator.py`, `microcode.py` and `assembler.py` scripts using the `--help` option to find out about even more functionality.


Programming the computer using assembly language
------------------------------------------------

This simulator reads its memory contents from a text file with the `.asm` extension. The file should contain programming code written in assembler.

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

The assembler also supports comments using the `;` character, writing raw values with `db` and labels. Here is an example assembler program that uses all the features of the assembler:
```asm
;
; Test program that adds two numbers
;
	lda a  ; Load the memory contents at the (a) label into register "A".
	add b  ; Add the memory contents at the (b) label to the value in register "A".
	out    ; Display the value in register "A" on the 7-segment display.
	hlt    ; Halt the clock. This signals the end of the program.

a:         ; Label that marks memory location (a)
	db 28  ; Write the literatal value "28" at this memory location.
b:         ; Label that marks memory location (b)
	db 14  ; Write the literal value "14" at this memory location.
``` 

More example programs can be found in the `example_programs/` folder of this repository.
