
schematic = """
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ●●●●●●●●  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Clock:  ●                      ┃──┃┃┃┃┃┃┃┃──┃ Program counter: ●●●● (dec)  ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Mem. Addr.: ●●●● (dec)         ┃──┃┃┃┃┃┃┃┃──┃ "A" Register: ●●●●●●●● (dec) ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━━━━━━━━━━━┓ ┏━━━━━━━━━━┓
   ┃        RAM: ●●●●●●●● (dec)     ┃──┃┃┃┃┃┃┃┃──┃ ALU: ●●●●●●●● (dec) ┃ ┃Flags: ●● ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━┛ ┃       ZC ┃
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃                          ┗━━━━━━━━━━┛
   ┃ Instr. Reg: ●●●●●●●● (dec)     ┃──┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃             (asm)              ┃  ┃┃┃┃┃┃┃┃──┃ "B" Register: ●●●●●●●● (dec) ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┃┃┃┃┃┃┃┃  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃┃┃┃┃┃┃┃  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Micro Step: ●●● (dec)          ┃─┐┃┃┃┃┃┃┃┃──┃       Output: dec            ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Memory contents                ┃ │          ┃ Control: ●●●●●●●●●●●●●●●●    ┃
   ┠────────────────────────────────┨ └──────────┃          HMRRIIAAΣSBOCCJF    ┃
   ┃ 00                             ┃            ┃          LIIOOIIOOUIIEO I    ┃
   ┃ 01                             ┃            ┃          T                   ┃
   ┃ 02                             ┃            ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┃ 03                             ┃
   ┃ 04                             ┃
   ┃ 05                             ┃
   ┃ 06                             ┃            ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ 07                             ┃            ┃ Keyboard commands            ┃
   ┃ 08                             ┃            ┠──────────────────────────────┨
   ┃ 09                             ┃            ┃ Space: start/stop clock      ┃
   ┃ 10                             ┃            ┃     →: step clock            ┃
   ┃ 11                             ┃            ┃     ↑: increase clock speed  ┃
   ┃ 12                             ┃            ┃     ↓: decrease clock speed  ┃
   ┃ 13                             ┃            ┃     h: halt system           ┃
   ┃ 14                             ┃            ┃   ESC: quit                  ┃
   ┃ 15                             ┃            ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
""" 
 
import curses
import sys

import microcode
from simulator import step
from assembler import disassemble


def init(stdscr):
    """Perform initialization of the console user interface.

    Parameters
    ----------
    stdscr : curses screen
        The curses screen object as created by curses.wrapper().
    """
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
            stdscr.addstr(row, col + n, f' ({num:03d})', curses.color_pair(1))

    # Bus
    draw_leds(1, 39, num=state.bus, n=8, color=5, dec=False)

    # Clock
    draw_leds(2, 13, num=state.clock, n=1, color=4, dec=False)

    # Program counter
    draw_leds(2, 68, num=state.register.program_counter, n=4, color=3)

    # Memory address
    draw_leds(5, 17, num=state.register.memory_address, n=4, color=5)

    # "A" register
    draw_leds(5, 65, num=state.register.a, n=8, color=2)

    # RAM
    draw_leds(8, 17, num=state.memory[state.register.memory_address], n=8, color=2)

    # ALU
    draw_leds(8, 56, num=state.alu, n=8, color=2)

    # Flags register
    flags = 0
    if state.flag.carry:
        flags += 0b01
    if state.flag.zero:
        flags += 0b10
    draw_leds(8, 81, num=flags, n=2, color=3, dec=False)

    # Instruction register
    draw_leds(11, 17, num=state.register.instruction >> 4, n=4, color=5)
    draw_leds(11, 21, num=state.register.instruction & 0x0f, n=4, color=4)
    # Print the assembler instruction (clear the line first)
    stdscr.addstr(12, 17, '         ', curses.color_pair(1))
    stdscr.addstr(12, 17, f'({disassemble(state.register.instruction)})', curses.color_pair(1))

    # "B" register
    draw_leds(12, 65, num=state.register.b, n=8, color=2)

    # Output register
    stdscr.addstr(15, 65, f'{state.register.output:04d}', curses.color_pair(2))

    # Microinstruction step
    draw_leds(15, 17, num=state.microinstruction_counter, n=3, color=5)

    # Control lines
    control_lines = 0
    if state.control.halt:
        control_lines += microcode.HLT
    if state.control.memory_address_in:
        control_lines += microcode.MI 
    if state.control.memory_in:
        control_lines += microcode.RI 
    if state.control.memory_out:
        control_lines += microcode.RO 
    if state.control.instruction_out:
        control_lines += microcode.IO 
    if state.control.instruction_in:
        control_lines += microcode.II 
    if state.control.a_in:
        control_lines += microcode.AI 
    if state.control.a_out:
        control_lines += microcode.AO 
    if state.control.alu_out:
        control_lines += microcode.EO 
    if state.control.alu_subtract:
        control_lines += microcode.SU 
    if state.control.b_in:
        control_lines += microcode.BI 
    if state.control.output_in:
        control_lines += microcode.OI 
    if state.control.program_counter_enable:
        control_lines += microcode.CE 
    if state.control.program_counter_out:
        control_lines += microcode.CO 
    if state.control.program_counter_jump:
        control_lines += microcode.J  
    if state.control.flags_in:
        control_lines += microcode.FI 
    draw_leds(18, 60, num=control_lines, n=16, color=4, dec=False)

    # Memory contents
    for address, contents in enumerate(state.memory_human_readable):
        color = curses.color_pair(1)
        if address == state.register.program_counter:
            color = curses.color_pair(3)
        if address == state.register.memory_address:
            color = curses.color_pair(5)

        # Blank the line before drawing memory contents
        stdscr.addstr(20 + address, 4, '                               ', color)
        stdscr.addstr(20 + address, 5, contents, color)

    # Halt message
    if state.control.halt:
        stdscr.move(38, 0)
        stdscr.clrtoeol()
        stdscr.addstr(38, 0, 'System halted. Press any key to quit simulator.', curses.color_pair(1))

    # Do the actual drawing to the screen
    stdscr.refresh()


def print_message(stdscr, msg):
    stdscr.move(38, 0)
    stdscr.clrtoeol()
    stdscr.addstr(38, 0, msg, curses.color_pair(1))


def handle_keypresses(stdscr, state):
    """Handle user keypresses.

    Parameters
    ----------
    stdscr : curses screen
        The curses screen object as created by curses.wrapper().
    """
    try:
        c = stdscr.getch()
        if c == ord(' '):
            state.clock_automatic = not state.clock_automatic
            if state.clock_automatic:
                print_message(stdscr, 'Started clock.')
            else:
                print_message(stdscr, 'Stopped clock.')
        elif c == curses.KEY_RIGHT:
            print_message(stdscr, 'Stepping clock.')
            step(state)
        elif c == curses.KEY_UP:
            state.clock_speed += 1
            print_message(stdscr, f'Increased clock to {state.clock_speed} Hz.')
        elif c == curses.KEY_DOWN:
            state.clock_speed -= 1
            if state.clock_speed < 0:
                state.clock_speed = 0
            print_message(stdscr, f'Decreased clock to {state.clock_speed} Hz.')
        elif c == ord('h') or c == ord('q'):
            state.control.halt = True
        elif c == 27:
            sys.exit(0)
    except curses.error as e:
        # No key pressed
        stdscr.move(38, 0)
        stdscr.clrtoeol()
        stdscr.addstr(38, 0, str(e))
