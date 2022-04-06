"""
Simulator for the SAP-1 8-bit breadboard computer.
"""
import sys
import curses
from time import time, sleep
from collections import deque
from dataclasses import dataclass, asdict, field

import microcode
import interface
from assembler import assemble


_previous_states = deque(maxlen=10_000)


@dataclass
class State:  # Classes are namespaces
    bus: int = 0
    memory: list[int] = field(default_factory=lambda: assemble(sys.argv[1])[0])
    memory_human_readable: list[str]  = field(default_factory=lambda: assemble(sys.argv[1])[1])
    rom_address: int = 0

    # Content of the registers
    reg_a: int = 0
    reg_b: int = 0
    reg_instruction: int = 0
    reg_memory_address: int = 0
    reg_program_counter: int = 0
    reg_output: int = 0
    reg_flags: int = 0

    control_signals: int = 0

    # Flag outputs from the ALU
    flag_carry: bool = False
    flag_zero: bool = False

    # Clock
    clock: bool = False

    # Other stuff
    alu: int = 0
    microinstruction_counter: int = 0

    def step(self):
        """Perform a single step (half a clock-cycle)."""
        # When system is halted, do nothing
        if self.control_signals & microcode.HLT:
            return

        # Before we update the state, keep a copy of the current state so we
        # could revert later if we want.
        global _previous_states
        _previous_states.append(asdict(self))

        # Flip clock signal
        self.clock = not self.clock

        # Set control lines based on current microinstruction.
        # This is done on the down-flank of the clock.
        if not self.clock:
            # Build microcode ROM address
            self.rom_address = (self.reg_instruction & 0xf0) >> 1
            self.rom_address = (self.reg_instruction & 0x0f) << 3
            self.rom_address += self.microinstruction_counter
            if self.reg_flags & 0b01:  # Carry flag
                self.rom_address += 1 << 7
            if self.reg_flags & 0b10:  # Zero flag
                self.rom_address += 1 << 8

            self.control_signals = microcode.ucode[self.rom_address]

        # Write to the bus
        if self.control_signals & microcode.AO:
            self.bus = self.reg_a
        if self.control_signals & microcode.EO:
            self.bus = self.alu
        if self.control_signals & microcode.CO:
            self.bus = self.reg_program_counter
        if self.control_signals & microcode.RO:
            self.bus = self.memory[self.reg_memory_address]

        # Read from the bus
        if self.clock:
            if self.control_signals & microcode.AI:
                self.reg_a = self.bus
            if self.control_signals & microcode.BI:
                self.reg_b = self.bus
            if self.control_signals & microcode.II:
                self.reg_instruction = self.bus
            if self.control_signals & microcode.MI:
                self.reg_memory_address = self.bus
            if self.control_signals & microcode.J:
                self.reg_program_counter = self.bus
            if self.control_signals & microcode.RI:
                address = self.reg_memory_address
                self.memory[address] = self.bus
                human_readable = f'{address:02d}: {self.bus >> 4:04b} {self.bus & 0x0f:04b}'
                self.memory_human_readable[address] = human_readable
            if self.control_signals & microcode.OI:
                if self.bus != self.reg_output:
                    self.reg_output = self.bus

        # Transfer ALU flag outputs to the flags register
        if self.clock and (self.control_signals & microcode.FI):
            self.reg_flags = self.flag_carry + (self.flag_zero << 1)

        # Do ALU stuff, set flag outputs
        if self.control_signals & microcode.SU:
            self.alu = self.reg_a - self.reg_b
        else:
            self.alu = self.reg_a + self.reg_b
        if self.alu > 255:
            if self.control_signals:
                self.flag_carry = True
            self.alu = self.alu % 255
        else:
            if self.control_signals:
                self.flag_carry = False
        if self.alu < 0:
            self.alu += 255
        if self.control_signals:
            self.flag_zero = self.alu == 0

        # Increment program counters
        if self.control_signals & microcode.CE and self.clock:
            self.reg_program_counter = (self.reg_program_counter + 1) % 255
        if not self.clock:
            self.microinstruction_counter = (self.microinstruction_counter + 1) % 8
            if self.control_signals & microcode.TR:
                self.microinstruction_counter = 0

        return self

    def _load_serialized_state(self, prev_state):
        for k, v in prev_state.items():
            if k.startswith('_'):
                continue
            setattr(self, k, v)

    def revert(self):
        global _previous_states
        if len(_previous_states) > 0:
            prev_state = _previous_states.pop()
            self._load_serialized_state(prev_state)


class Simulator:
    def __init__(self):
        # Variables related to automatic stepping of the clock
        self.clock_automatic = False
        self.clock_speed = 1  # Hz
        self.last_clock_time = 0 # Keep track of when the next clock was last stepped

        # Initialize system state
        self.reset()

    def run(self, stdscr):
        """Main function to run the simulator with its console user interface.

        Parameters
        ----------
        stdscr : curses screen
            The curses screen object as created by curses.wrapper().
        """
        interface.init(stdscr)

        # Start simulation and UI loop. This loop only terminates when the ESC
        # key is pressed, which is detected inside the handle_keypresses()
        # function.
        while True:
            interface.update(stdscr, self.state)
            if self.clock_automatic:
                wait_time = (0.5 / self.clock_speed) - (time() - self.last_clock_time)
                if wait_time > 0.1:
                    curses.halfdelay(int(10 * wait_time))
                    interface.handle_keypresses(stdscr, self)
                    self.step()
                else:
                    curses.nocbreak()
                    if wait_time > 0:
                        sleep(wait_time)
                    curses.nocbreak()
                    stdscr.nodelay(True)
                    interface.handle_keypresses(stdscr, self)
                    self.step()
            else:
                curses.cbreak()
                interface.handle_keypresses(stdscr, self)

            # When we reach the end of the program, set the clock to manual
            # mode so we don't keep generating useless system states.
            if self.state.control_signals & microcode.HLT:
                self.clock_automatic = False
            interface.update(stdscr, self.state)

    def step(self):
        """Step the clock while keeping track of time."""
        self.last_clock_time = time()
        self.state.step()

    def reset(self):
        """Reset the machine."""
        global _previous_states
        _previous_states.clear()
        self.state = State()
        self.state.control_signals = microcode.ucode[self.state.rom_address]



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python simulator.py PROGRAM_TO_EXECUTE')
        sys.exit(1)
    simulator = Simulator()
    curses.wrapper(simulator.run)
