
schematic = """
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ●●●●●●●●  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Clock:  ●                      ┠──┃┃┃┃┃┃┃┃──┨ Progr. count: ●●●●●●●● (dec) ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Mem. Addr.: ●●●●●●●● (dec)     ┠──┃┃┃┃┃┃┃┃──┨ "A" Register: ●●●●●●●● (dec) ┃
   ┗━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━┛
   ┏━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━┷━━━━━━━━━┓ ┏━━━━━━━━━━┓
   ┃        RAM: ●●●●●●●● (dec)     ┠──┃┃┃┃┃┃┃┃──┨ ALU: ●●●●●●●● (dec) ┠─┨Flags: ●● ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━┛ ┃       ZC ┃
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃                          ┗━━━━━━━━━━┛
   ┃ Instr. Reg: ●●●●●●●● (dec)     ┠──┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃                (ins)           ┃  ┃┃┃┃┃┃┃┃──┨ "B" Register: ●●●●●●●● (dec) ┃
   ┗━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┏━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Micro Step: ●●●● (dec)         ┃  ┃┃┃┃┃┃┃┃──┨ Output: -dec (unsigned)      ┃
   ┃ ROM addr.: ●●●●●●●●●●●● (dec)  ┠─┐┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Memory contents                ┃ │          ┃ Control: ●●●●●●●●●●●●●●●●●●●● ┃
   ┠────────────────────────────────┨ │          ┃          HMRIJABFOSCS RICABΣM ┃
   ┃ 00                             ┃ └──────────┨          LIII IIIIUES OOOOOOR ┃
   ┃ 01                             ┃            ┃          T                    ┃
   ┃ 02                             ┃            ┃           input       output  ┃
   ┃ 03                             ┃            ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┃ 04                             ┃            ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ 05                             ┃            ┃ Keyboard commands            ┃            
   ┃ 06                             ┃            ┠──────────────────────────────┨            
   ┃ 07                             ┃            ┃ Space: start/stop clock      ┃            
   ┃ 08                             ┃            ┃     →: step clock            ┃            
   ┃ 09                             ┃            ┃     ←: step clock backwards  ┃
   ┃ 10                             ┃            ┃     ↑: increase clock speed  ┃
   ┃ 11                             ┃            ┃     ↓: decrease clock speed  ┃
   ┃ 12                             ┃            ┃     o: toggle output mode    ┃
   ┃ 13                             ┃            ┃     r: reset system          ┃
   ┃ 14                             ┃            ┃ Enter: run until next instr. ┃
   ┃ 15                             ┃            ┃   ESC: quit                  ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛            ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

import curses
import sys

import microcode
#from assembler import num_to_instruction


def init(stdscr):
    """Perform initialization of the console user interface.

    Parameters
    ----------
    stdscr : curses screen
        The curses screen object as created by curses.wrapper().
    """
    # Check minimal screen size
    if curses.LINES < 38 or curses.COLS < 84:
        raise RuntimeError('Your terminal window should be at least 38x84.')

    # Setup the colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Hide the cursor
    curses.curs_set(0)

    # Clear the screen and draw the schematic as defined at the top of this
    # file as a background. We will draw stuff on top of this later in the
    # update() function.
    stdscr.clear()
    stdscr.addstr(0, 0, schematic, curses.color_pair(1))


def update(stdscr, state):
    """Update the console user interface.

    Parameters
    ----------
    stdscr : curses screen
        The curses screen object as created by curses.wrapper().
    state : state
        The state of the machine as defined in simulator.py.
    """
    def draw_leds(row, col, num, color=2, n=8, dec=True):
        """Draw a row of LEDs displaying a number.

        The number is hown in binary and optionally also in decimal.

        Parameters
        ----------
        row : int
            The row on the screen to draw the LEDs on.
        col : int
            The column on the screen to draw the LEDs on.
        num : int
            The number to display using the LEDs
        color : int
            The color-pair to draw the LEDs in when active. See the color-pairs
            defined in the init() function above.
        n : int
            The number of LEDs to use to display the number. Defaults to 8.
        dec : bool
            Whether to also display the number in decimal. Defaults to True.
        """
        for i in range(n):
            led_color = color if (num >> i) & 1 else 1
            stdscr.addstr(row, col + n - 1 - i, '●', curses.color_pair(led_color))
        if dec:
            if n <= 8:
                stdscr.addstr(row, col + n, f' ({num:03d})', curses.color_pair(1))
            else:
                stdscr.addstr(row, col + n, f' ({num:04d})', curses.color_pair(1))

    # Bus
    draw_leds(1, 39, num=state.bus, n=8, color=5, dec=False)

    # Clock
    draw_leds(2, 13, num=state.clock, n=1, color=4, dec=False)

    # Program counter
    draw_leds(2, 65, num=state.reg_program_counter, n=8, color=3)

    # Memory address
    draw_leds(5, 17, num=state.reg_memory_address, n=8, color=5)

    # "A" register
    draw_leds(5, 65, num=state.reg_a, n=8, color=2)

    # RAM
    address = state.reg_memory_address
    if state.is_line_active(microcode.SS):
        address += 1 << 8
        print_message(stdscr, f'{address:d} {state.memory[address]}')
    draw_leds(8, 17, num=state.memory[address], n=8, color=2)

    # ALU
    draw_leds(8, 56, num=state.alu, n=8, color=2)

    # Flags register
    draw_leds(8, 81, num=state.reg_flags, n=2, color=3, dec=False)

    # Instruction register
    draw_leds(11, 17, num=state.reg_instruction, n=8, color=5)
    #stdscr.addstr(12, 20, f'({num_to_instruction[state.reg_instruction]:>3s})', curses.color_pair(1))

    # "B" register
    draw_leds(12, 65, num=state.reg_b, n=8, color=2)

    # Output register
    if state.output_signed_mode:
        # Convert 8bit twos-complement number to a Python signed integer
        out = state.reg_output
        if out & 0x80:
            out = (out ^ 0xff) - 1
        stdscr.addstr(15, 59, f'{out:04d} (signed)  ', curses.color_pair(2))
    else:
        stdscr.addstr(15, 59, f'{state.reg_output:04d} (unsigned)', curses.color_pair(2))

    # Microinstruction step
    draw_leds(15, 17, num=state.microinstruction_counter, n=4, color=5)
    draw_leds(16, 16, num=state.rom_address, n=12, color=5)

    # Control lines
    print(f'{state.control_signals:016b}')
    control_signals = (state.control_signals & 0b1111111111111000) << 4
    control_signals += (1 << 7) >> (state.control_signals & 0b111)
    print(f'{control_signals:020b}')
    draw_leds(19, 60, control_signals, n=20, color=4, dec=False)

    # Memory contents
    offset = state.reg_program_counter // 16 * 16
    for address, contents in enumerate(state.memory_human_readable[offset:offset + 16], offset):
        color = curses.color_pair(1)
        if address == state.reg_program_counter:
            color = curses.color_pair(3)
        if address == state.reg_memory_address:
            color = curses.color_pair(5)

        # Blank the line before drawing memory contents
        stdscr.addstr(21 + address - offset, 4, '                               ', color)
        stdscr.addstr(21 + address - offset, 5, contents, color)
    # Blank any remaining empty lines in the memory contents display
    for i in range(22 + address - offset, 37):
        stdscr.addstr(i, 4, '                               ', color)

    # Halt message
    if state.is_line_active(microcode.HLT):
        print_message(stdscr, 'System halted.')

    # Do the actual drawing to the screen
    stdscr.refresh()


def print_message(stdscr, msg):
    stdscr.move(39, 0)
    stdscr.clrtoeol()
    stdscr.addstr(39, 0, msg, curses.color_pair(1))
    stdscr.refresh()


def handle_keypresses(stdscr, simulator):
    """Handle user keypresses.

    Parameters
    ----------
    simulator : Simulator
        The simulator objet running the show.
    """
    try:
        c = stdscr.getch()
        if c == ord(' '):
            simulator.clock_automatic = not simulator.clock_automatic
            if simulator.clock_automatic:
                print_message(stdscr, 'Started clock.')
            else:
                print_message(stdscr, 'Stopped clock.')
        elif c == curses.KEY_RIGHT:
            print_message(stdscr, 'Stepping clock.')
            simulator.step()
        elif c == curses.KEY_LEFT:
            print_message(stdscr, 'Stepping clock backwards.')
            simulator.state.revert()
        elif c == curses.KEY_UP:
            simulator.clock_speed *= 2
            print_message(stdscr, f'Increased clock to {simulator.clock_speed} Hz.')
        elif c == curses.KEY_DOWN:
            simulator.clock_speed /= 2
            if simulator.clock_speed < 0:
                simulator.clock_speed = 0
            print_message(stdscr, f'Decreased clock to {simulator.clock_speed} Hz.')
        elif c == ord('\n'):
            simulator.step()
            while (simulator.state.microinstruction_counter > 0 or not simulator.state.clock) and not simulator.state.is_line_active(microcode.HLT):
                simulator.step()
            print_message(stdscr, 'Stepping clock until we reach next instruction.')
        elif c == ord('o'):
            simulator.state.output_signed_mode = not simulator.state.output_signed_mode
            update(stdscr, simulator.state)
        elif c == ord('r'):
            simulator.reset()
        elif c == 27 or c == ord('q') or c == 3:
            sys.exit(0)
    except curses.error as e:
        # No key pressed
        stdscr.move(38, 0)
        stdscr.clrtoeol()
        stdscr.addstr(38, 0, str(e))
