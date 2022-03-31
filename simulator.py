"""
Simulator for the SAP-1 8-bit breadboard computer.
"""
import sys
import curses
from time import time, sleep

import microcode
import interface
from assembler import assemble


class State:  # Classes are namespaces
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
        t_step_reset = False
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
    clock_speed = 1.0  # Hz
    last_clock_time = 0 # Keep track of when the next clock was last stepped

    # Other stuff
    alu = 0
    microinstruction_counter = 0

    def step(self):
        """Perform a single step (half a clock-cycle)."""
        # When system is halted, do nothing
        if self.control.halt:
            return

        # Flip clock signal
        self.clock = not self.clock
        self.last_clock_time = time()

        # Set control lines based on current microinstruction.
        # This is done on the down-flank of the clock.
        if not self.clock:
            # Build microcode ROM address
            self.rom_address = (self.register.instruction & 0x0f) << 3
            self.rom_address += self.microinstruction_counter
            if self.flag.carry:
                self.rom_address += 1 << 7
            if self.flag.zero:
                self.rom_address += 1 << 8

            microinstruction = self.microcode[self.rom_address]

            self.control.halt = microinstruction & microcode.HLT
            self.control.memory_address_in = microinstruction & microcode.MI
            self.control.memory_in = microinstruction & microcode.RI
            self.control.memory_out = microinstruction & microcode.RO
            self.control.t_step_reset = microinstruction & microcode.TR
            self.control.instruction_in = microinstruction & microcode.II
            self.control.a_in = microinstruction & microcode.AI
            self.control.a_out = microinstruction & microcode.AO
            self.control.alu_out = microinstruction & microcode.EO
            self.control.alu_subtract = microinstruction & microcode.SU
            self.control.b_in = microinstruction & microcode.BI
            self.control.output_in = microinstruction & microcode.OI
            self.control.program_counter_enable = microinstruction & microcode.CE
            self.control.program_counter_out = microinstruction & microcode.CO
            self.control.program_counter_jump = microinstruction & microcode.J
            self.control.flags_in = microinstruction & microcode.FI

        # Write to the bus
        if self.control.a_out:
            self.bus = self.register.a
        if self.control.alu_out:
            self.bus = self.alu
        if self.control.program_counter_out:
            self.bus = self.register.program_counter
        if self.control.memory_out:
            self.bus = self.memory[self.register.memory_address]

        # Read from the bus
        if self.control.a_in and self.clock:
            self.register.a = self.bus
        if self.control.b_in and self.clock:
            self.register.b = self.bus
        if self.control.instruction_in and self.clock:
            self.register.instruction = self.bus
        if self.control.memory_address_in and self.clock:
            self.register.memory_address = self.bus
        if self.control.program_counter_jump:
            self.register.program_counter = self.bus
        if self.control.memory_in and self.clock:
            address = self.register.memory_address
            self.memory[address] = self.bus
            human_readable = f'{address:02d}: {self.bus >> 4:04b} {self.bus & 0x0f:04b}'
            self.memory_human_readable[address] = human_readable
        if self.control.output_in and self.clock:
            if self.bus != self.register.output:
                self.register.output = self.bus

        # Do ALU stuff, set flags
        if self.control.alu_subtract:
            self.alu = self.register.a - self.register.b
        else:
            self.alu = self.register.a + self.register.b
        if self.alu > 255:
            if self.control.flags_in:
                self.flag.carry = True
            self.alu = self.alu % 255
        else:
            if self.control.flags_in:
                self.flag.carry = False
        if self.alu < 0:
            self.alu += 255
        if self.control.flags_in:
            self.flag.zero = self.alu == 0

        # Increment counters
        if self.control.program_counter_enable and self.clock:
            self.register.program_counter = (self.register.program_counter + 1) % 255
        if not self.clock:
            self.microinstruction_counter = (self.microinstruction_counter + 1) % 8
            if self.control.t_step_reset:
                self.microinstruction_counter = 0

        return self


def main(stdscr):
    """Main function to start the simulator with its console user interface.

    Parameters
    ----------
    stdscr : curses screen
        The curses screen object as created by curses.wrapper().
    """
    interface.init(stdscr)

    # Create a freshly minted system state
    state = State()

    # Run the program until halt
    while not state.control.halt:
        interface.update(stdscr, state)
        if state.clock_automatic:
            wait_time = (0.5 / state.clock_speed) - (time() - state.last_clock_time)
            if wait_time > 0.1:
                curses.halfdelay(int(10 * wait_time))
                interface.handle_keypresses(stdscr, state)
                state.step()
            else:
                curses.nocbreak()
                if wait_time > 0:
                    sleep(wait_time)
                curses.nocbreak()
                stdscr.nodelay(True)
                interface.handle_keypresses(stdscr, state)
                state.step()
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
