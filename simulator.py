"""
Simulator for the SAP-1 8-bit breadboard computer.
"""
import curses
from argparse import ArgumentParser
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
    rom_address: int = 0
    memory: list[int] = field(default_factory=list)
    memory_human_readable: list[str] = field(default_factory=list)

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
    output_signed_mode: bool = False

    # Whether to keep track of history
    keep_history: bool = True

    def update(self):
        """Update the state based on the values of the control lines. This does
        not touch the various clocks, so this can be called as often as needed
        to keep every component in sync."""
        self.bus = 0

        # Set control lines based on current microinstruction. Only happens on
        # the down flank of the clock.
        if not self.clock:
            self.update_control_signals()

        # Write to the bus
        if self.is_line_active(microcode.AO):
            self.bus = self.reg_a
        if self.is_line_active(microcode.BO):
            self.bus = self.reg_b
        if self.is_line_active(microcode.EO):
            self.bus = self.alu
        if self.is_line_active(microcode.CO):
            self.bus = self.reg_program_counter
        if self.is_line_active(microcode.RO):
            address = self.reg_memory_address
            if self.is_line_active(microcode.SS):
                address += 1 << 8
            self.bus = self.memory[address]
        if self.is_line_active(microcode.IO):
            self.bus = self.reg_instruction & 0b111

        # Read from the bus
        if self.clock:
            if self.is_line_active(microcode.AI):
                self.reg_a = self.bus
            if self.is_line_active(microcode.BI):
                self.reg_b = self.bus
            if self.is_line_active(microcode.II):
                self.reg_instruction = self.bus
            if self.is_line_active(microcode.MI):
                self.reg_memory_address = self.bus
            if self.is_line_active(microcode.J):
                self.reg_program_counter = self.bus
            if self.is_line_active(microcode.RI):
                address = self.reg_memory_address
                if self.is_line_active(microcode.SS):
                    address += 1 << 8
                self.memory[address] = self.bus
                human_readable = f'{address:02x}: {self.bus:08b}'
                self.memory_human_readable[address] = human_readable
            if self.is_line_active(microcode.OI):
                if self.bus != self.reg_output:
                    self.reg_output = self.bus

        # Transfer ALU flag outputs to the flags register
        if self.clock and self.is_line_active(microcode.FI):
            self.reg_flags = self.flag_carry + (self.flag_zero << 1)

        # Do ALU stuff, set flag outputs
        if self.is_line_active(microcode.SU):
            # Perform subtraction by computing the 8bit twos-complement
            # representation of register B.
            self.alu = self.reg_a + (self.reg_b ^ 0xff & 0xff) + 1
        else:
            self.alu = self.reg_a + self.reg_b
        self.flag_carry = self.alu > 0xff
        self.alu &= 0xff
        self.flag_zero = self.alu == 0

    def update_control_signals(self):
        """Update the control signals based on the state of the microcode ROM
        module."""
        self.rom_address = self.reg_instruction << 3
        self.rom_address += self.microinstruction_counter
        if self.reg_flags & 0b01:  # Carry flag
            self.rom_address += 1 << 11
        if self.reg_flags & 0b10:  # Zero flag
            self.rom_address += 1 << 12

        self.control_signals = microcode.ucode[self.rom_address]

    def step(self):
        """Perform a single step (half a clock-cycle)."""
        # When system is halted, do nothing
        if self.is_line_active(microcode.HLT):
            return None

        # Before we update the state, keep a copy of the current state so we
        # could revert later if we want.
        if self.keep_history:
            global _previous_states
            _previous_states.append(asdict(self))

        # Flip clock signal
        self.clock = not self.clock

        # Increment program counters
        if self.is_line_active(microcode.CE) and self.clock:
            self.reg_program_counter = (self.reg_program_counter + 1) % 256
        if not self.clock:
            self.microinstruction_counter = (self.microinstruction_counter + 1) % 8
            if self.is_line_active(microcode.SR):
                self.microinstruction_counter = 0
                # Changing the microinstruction counter has an immediate effect
                # on the system state.
                self.update()

        # Update the system state now that the clock has changed
        self.update()

        if self.clock and self.is_line_active(microcode.OI):
            return self.reg_output
        else:
            return None

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

    def is_line_active(self, line):
        if line & 0b111: 
            return (self.control_signals & 0b111) == line
        else:
            return self.control_signals & line


class Simulator:
    def __init__(self, program_code):
        # Variables related to automatic stepping of the clock
        self.clock_automatic = False
        self.clock_speed = 1  # Hz
        self.last_clock_time = 0 # Keep track of when the next clock was last stepped
        self.memory, self.memory_human_readable = assemble(program_code)
        while len(self.memory) < 512:
            self.memory.append(0)
        while len(self.memory_human_readable) < 512:
            self.memory_human_readable.append(f'{len(self.memory_human_readable):02x}: 0')

        # Initialize system state
        self.reset()

    def run_interface(self, stdscr):
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
            if self.state.is_line_active(microcode.HLT):
                self.clock_automatic = False
            interface.update(stdscr, self.state)

    def run_batch(self):
        """Run the simulator in batch mode."""
        self.state.keep_history = False  # Not needed, so turn off for extra speed
        outputs = list()
        while not self.state.is_line_active(microcode.HLT):
            out = self.state.step()
            if out is not None:
                outputs.append(out)
        return outputs

    def step(self):
        """Step the clock while keeping track of time."""
        self.last_clock_time = time()
        return self.state.step()

    def reset(self):
        """Reset the machine."""
        global _previous_states
        _previous_states.clear()
        self.state = State()
        self.state.memory = self.memory
        self.state.memory_human_readable = self.memory_human_readable
        self.state.update()



if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('file', type=str, help='Program to execute')
    parser.add_argument('--no-interface', action='store_true', help="Don't show the interface, but run the program in batch mode")
    args = parser.parse_args()

    with open(args.file) as f:
        simulator = Simulator(f.read())

    if args.no_interface:
        for out in simulator.run_batch():
            print(out)
    else: 
        curses.wrapper(simulator.run_interface)
