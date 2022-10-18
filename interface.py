#encoding: utf-8
schematic = """
                                       Bus: dec
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
   ┃ Micro Step: ●●● (dec)          ┃  ┃┃┃┃┃┃┃┃──┨ Output: -dec (unsigned)      ┃
   ┃ EEPROM: ●●●●●●●●●●●●● (dec)    ┠─┐┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Memory contents                ┃ │          ┃ Control: ●●●●●●●●●●●●●●●●●●●● ┃
   ┠────────────────────────────────┨ │          ┃          HMRIJABFOΣCRICABΣSΣS ┃
   ┃ 00                             ┃ └──────────┨          LIII IIIIIEOOOOOOSCR ┃
   ┃ 01                             ┃            ┃          T                    ┃
   ┃ 02                             ┃            ┃           input       output  ┃
   ┃ 03                             ┃            ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┃ 04                             ┃            ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ 05                             ┃            ┃ Keyboard commands             ┃
   ┃ 06                             ┃            ┠───────────────────────────────┨
   ┃ 07                             ┃            ┃ Space: start/stop clock       ┃
   ┃ 08                             ┃            ┃     →: step clock             ┃
   ┃ 09                             ┃            ┃     ←: step clock backwards   ┃
   ┃ 10                             ┃            ┃     ↑: increase clock speed   ┃
   ┃ 11                             ┃            ┃     ↓: decrease clock speed   ┃
   ┃ 12                             ┃            ┃     o: toggle output mode     ┃
   ┃ 13                             ┃            ┃     r: reset system           ┃
   ┃ 14                             ┃            ┃ Enter: run until next instr.  ┃
   ┃ 15                             ┃            ┃   ESC: quit                   ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛            ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

import curses
import sys
from time import time, sleep

import microcode


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
    draw_leds(2, 39, num=state.bus, n=8, color=5, dec=False)
    stdscr.addstr(1, 44, f'{state.bus:03d}', curses.color_pair(1))

    # Clock
    draw_leds(3, 13, num=state.clock, n=1, color=4, dec=False)

    # Program counter
    draw_leds(3, 65, num=state.reg_program_counter, n=8, color=3)

    # Memory address
    draw_leds(6, 17, num=state.reg_memory_address, n=8, color=5)

    # "A" register
    draw_leds(6, 65, num=state.reg_a, n=8, color=2)

    # RAM
    address = state.reg_memory_address
    if state.is_line_active(microcode.SS):
        address += 1 << 8
    draw_leds(9, 17, num=state.memory[address], n=8, color=2)

    # ALU
    draw_leds(9, 56, num=state.alu, n=8, color=2)

    # Flags register
    draw_leds(9, 81, num=state.reg_flags, n=2, color=3, dec=False)

    # Instruction register
    draw_leds(12, 17, num=state.reg_instruction, n=8, color=4)

    # "B" register
    draw_leds(13, 65, num=state.reg_b, n=8, color=2)

    # Output register
    if state.output_signed_mode:
        # Convert 8bit twos-complement number to a Python signed integer
        out = state.reg_output
        if out & 0x80:
            out = (out ^ 0xff) - 1
        stdscr.addstr(16, 59, f'{out:04d} (signed)  ', curses.color_pair(2))
    else:
        stdscr.addstr(16, 59, f'{state.reg_output:04d} (unsigned)', curses.color_pair(2))

    # Microinstruction step
    draw_leds(16, 17, num=state.microinstruction_counter, n=3, color=3)

    # Microcode EEPROM address
    draw_leds(17, 16, num=state.rom_address, n=13, color=5)

    # Control lines
    control_signals = int(state.is_line_active(microcode.HLT)) << 19
    control_signals += int(state.is_line_active(microcode.MI)) << 18
    control_signals += int(state.is_line_active(microcode.RI)) << 17
    control_signals += int(state.is_line_active(microcode.II)) << 16
    control_signals += int(state.is_line_active(microcode.J)) << 15
    control_signals += int(state.is_line_active(microcode.AI)) << 14
    control_signals += int(state.is_line_active(microcode.BI)) << 13
    control_signals += int(state.is_line_active(microcode.FI)) << 12
    control_signals += int(state.is_line_active(microcode.OI)) << 11
    control_signals += int(state.is_line_active(microcode.EI)) << 10
    control_signals += int(state.is_line_active(microcode.CE)) << 9
    control_signals += int(state.is_line_active(microcode.RO)) << 8
    control_signals += int(state.is_line_active(microcode.IO)) << 7
    control_signals += int(state.is_line_active(microcode.CO)) << 6
    control_signals += int(state.is_line_active(microcode.AO)) << 5
    control_signals += int(state.is_line_active(microcode.BO)) << 4
    control_signals += int(state.is_line_active(microcode.EO)) << 3
    control_signals += int(state.is_line_active(microcode.SS)) << 2
    control_signals += int(state.is_line_active(microcode.EC)) << 1
    control_signals += int(state.is_line_active(microcode.SR)) << 0
    draw_leds(20, 60, control_signals, n=20, color=5, dec=False)

    # Memory contents
    offset = state.reg_program_counter // 16 * 16
    for address, contents in enumerate(state.memory_human_readable[offset:offset + 16], offset):
        color = curses.color_pair(1)
        if address == state.reg_program_counter:
            color = curses.color_pair(3)
        if address == state.reg_memory_address:
            color = curses.color_pair(5)

        # Blank the line before drawing memory contents
        stdscr.addstr(22 + address - offset, 4, '                               ', color)
        stdscr.addstr(22 + address - offset, 5, contents, color)
    # Blank any remaining empty lines in the memory contents display
    for i in range(23 + address - offset, 37):
        stdscr.addstr(i, 4, '                               ', color)

    # Halt message
    if state.is_line_active(microcode.HLT):
        print_message(stdscr, 'System halted.')

    # Do the actual drawing to the screen
    stdscr.refresh()


def print_message(stdscr, msg):
    stdscr.move(40, 0)
    stdscr.clrtoeol()
    stdscr.addstr(40, 0, msg, curses.color_pair(1))
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
            if simulator.clock_type == 'manual':
                simulator.clock_type = 'automatic'
                print_message(stdscr, 'Started clock.')
            elif simulator.clock_type == 'automatic':
                simulator.clock_type = 'manual'
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
            print_message(stdscr, 'Simulator reset.')
        elif c == 27 or c == ord('q') or c == 3:
            sys.exit(0)
    except curses.error as e:
        # No key pressed
        stdscr.move(38, 0)
        stdscr.clrtoeol()
        stdscr.addstr(38, 0, str(e))


def run_interface(stdscr, simulator, bios=None):
    """Main function to run the simulator with its console user interface.

    Parameters
    ----------
    stdscr : curses screen
        The curses screen object as created by curses.wrapper().
    simulator : Simulator
        The 8-bit breadboard CPU simulator.
    bios : Bios
        Serial communication to the actual hardware
    """
    init(stdscr)

    # Start simulation and UI loop. This loop only terminates when the ESC
    # key is pressed, which is detected inside the handle_keypresses()
    # function.
    while True:
        update(stdscr, simulator.state)
        if simulator.clock_type == 'automatic':
            wait_time = (0.5 / simulator.clock_speed) - (time() - simulator.last_clock_time)
            if wait_time > 0.1:
                curses.halfdelay(int(10 * wait_time))
                handle_keypresses(stdscr, simulator)
                simulator.step()
            else:
                curses.nocbreak()
                if wait_time > 0:
                    sleep(wait_time)
                curses.nocbreak()
                stdscr.nodelay(True)
                handle_keypresses(stdscr, simulator)
                simulator.step()
        elif simulator.clock_type == 'manual':
            curses.cbreak()
            handle_keypresses(stdscr, simulator)
        elif simulator.clock_type == 'external':
            msg = bios.get_next_message()
            if msg == 'WELCOME':
                print_message(stdscr, 'Arduino on breadboards says hi.')
            elif msg == 'RESET':
                print_message(stdscr, msg)
                simulator.reset()
            elif msg == 'UP' or msg == 'DOWN':
                simulator.step(clock=msg == 'UP')
                # bus_val = int(bios.get_next_message())
                # if bus_val != simulator.state.bus:
                #     print_message(stdscr, f'Invalid bus state detected! {bus_val} != {simulator.state.bus}')
                # else:
                #     print_message(stdscr, f'{bus_val=}')

            curses.nocbreak()
            stdscr.nodelay(True)
            handle_keypresses(stdscr, simulator)

        # When we reach the end of the program, set the clock to manual
        # mode so we don't keep generating useless system states.
        if simulator.state.is_line_active(microcode.HLT):
            simulator.clock_type = 'manual'
        update(stdscr, simulator.state)
