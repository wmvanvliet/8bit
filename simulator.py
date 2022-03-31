"""
Simulator for the SAP-1 8-bit breadboard computer.
"""
import sys
import curses
from time import time, sleep

import microcode
import interface
from assembler import assemble


def reset():
    """Create a new system state with everything reset.

    Returns
    -------
    state : state
        The system state.
    """
    class state:  # Classes are namespaces
        bus = 0
        memory, memory_human_readable = assemble(sys.argv[1])
        microcode = microcode.ucode
        rom_address = 0

        # Content of the registers
        class register:
            a = 0
            b = 0
            instruction = 0
            memory_address = 0
            program_counter = 0
            output = 0

        # Control signals
        class control:
            halt = False
            a_out = False
            a_in = False
            b_in = False
            instruction_in = False
            instruction_out = False
            memory_address_in = False
            program_counter_jump = False
            program_counter_enable = False
            program_counter_out = False
            output_in = False
            alu_subtract = False
            alu_out = False
            memory_in = False
            memory_out = False
            flags_in = False

        # Flags
        class flag:
            carry = False
            zero = False

        # Clock
        clock = True
        clock_automatic = False
        clock_speed = 5.0  # Hz
        last_clock_time = 0 # Keep track of when the next clock was last stepped

        # Other stuff
        alu = 0
        microinstruction_counter = 0


    return state


def step(state):
    """Perform a single step (half a clock-cycle).

    The system state is modified in-place.

    Parameters
    ----------
    state : state
        The current system state.

    Returns
    -------
    state : state
        The new system state.
    """
    # When system is halted, do nothing
    if state.control.halt:
        return state

    # Flip clock signal
    state.clock = not state.clock
    state.last_clock_time = time()

    # Set control lines based on current microinstruction
    if not state.clock:
        # Build microcode ROM address
        state.rom_address = (state.register.instruction & 0xf0) >> 1
        state.rom_address += state.microinstruction_counter
        if state.flag.carry:
            state.rom_address += 1 << 7
        if state.flag.zero:
            state.rom_address += 1 << 8

        microinstruction = state.microcode[state.rom_address]

        state.control.halt = microinstruction & microcode.HLT
        state.control.memory_address_in = microinstruction & microcode.MI
        state.control.memory_in = microinstruction & microcode.RI
        state.control.memory_out = microinstruction & microcode.RO
        state.control.instruction_out = microinstruction & microcode.IO
        state.control.instruction_in = microinstruction & microcode.II
        state.control.a_in = microinstruction & microcode.AI
        state.control.a_out = microinstruction & microcode.AO
        state.control.alu_out = microinstruction & microcode.EO
        state.control.alu_subtract = microinstruction & microcode.SU
        state.control.b_in = microinstruction & microcode.BI
        state.control.output_in = microinstruction & microcode.OI
        state.control.program_counter_enable = microinstruction & microcode.CE
        state.control.program_counter_out = microinstruction & microcode.CO
        state.control.program_counter_jump = microinstruction & microcode.J
        state.control.flags_in = microinstruction & microcode.FI

    # Write to the bus
    if state.control.a_out:
        state.bus = state.register.a
    if state.control.alu_out:
        state.bus = state.alu
    if state.control.instruction_out:
        state.bus = state.register.instruction & 0x0f
    if state.control.program_counter_out:
        state.bus = state.register.program_counter
    if state.control.memory_out:
        state.bus = state.memory[state.register.memory_address]

    # Read from the bus
    if state.control.a_in and state.clock:
        state.register.a = state.bus
    if state.control.b_in and state.clock:
        state.register.b = state.bus
    if state.control.instruction_in and state.clock:
        state.register.instruction = state.bus
    if state.control.memory_address_in and state.clock:
        state.register.memory_address = state.bus
    if state.control.program_counter_jump:
        state.register.program_counter = state.bus
    if state.control.memory_in and state.clock:
        address = state.register.memory_address
        state.memory[address] = state.bus
        human_readable = f'{address:02d}: {state.bus >> 4:04b} {state.bus & 0x0f:04b}'
        state.memory_human_readable[address] = human_readable
    if state.control.output_in and state.clock:
        if state.bus != state.register.output:
            state.register.output = state.bus

    # Do ALU stuff, set flags
    if state.control.alu_subtract:
        state.alu = state.register.a - state.register.b
    else:
        state.alu = state.register.a + state.register.b
    if state.alu > 255:
        if state.control.flags_in:
            state.flag.carry = True
        state.alu = state.alu % 255
    else:
        if state.control.flags_in:
            state.flag.carry = False
    if state.alu < 0:
        state.alu += 255
    if state.control.flags_in:
        state.flag.zero = state.alu == 0

    # Increment counters
    if state.control.program_counter_enable and state.clock:
        state.register.program_counter = (state.register.program_counter + 1) % 255
    if not state.clock:
        state.microinstruction_counter = (state.microinstruction_counter + 1) % 5

    return state


def main(stdscr):
    """Main function to start the simulator with its console user interface.

    Parameters
    ----------
    stdscr : curses screen
        The curses screen object as created by curses.wrapper().
    """
    interface.init(stdscr)

    # Create a freshly minted system state
    state = reset()

    # Run the program until halt
    while not state.control.halt:
        interface.update(stdscr, state)
        if state.clock_automatic:
            wait_time = (1 / state.clock_speed) - (time() - state.last_clock_time)
            if wait_time > 0.1:
                curses.halfdelay(int(10 * wait_time))
                interface.handle_keypresses(stdscr, state)
                step(state)
            else:
                curses.nocbreak()
                if wait_time > 0:
                    sleep(wait_time)
                curses.nocbreak()
                stdscr.nodelay(True)
                interface.handle_keypresses(stdscr, state)
                step(state)
        else:
            curses.cbreak()
            interface.handle_keypresses(stdscr, state)
        interface.update(stdscr, state)

    # Press any key to exit the simulation
    interface.update(stdscr, state)
    curses.nocbreak()
    curses.cbreak()
    stdscr.nodelay(False)
    stdscr.getkey()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python simulator.py PROGRAM_TO_EXECUTE')
        sys.exit(1)
    curses.wrapper(main)
