"""
Simulator for the SAP-1 8-bit breadboard computer.
"""
from argparse import ArgumentParser
import sys
from time import time, sleep
from collections import deque
from dataclasses import dataclass, asdict, field

import microcode
from assembler import assemble


_previous_states = deque(maxlen=10_000)


@dataclass
class State:  # Classes are namespaces
    bus: int = 0
    memory: list[int] = field(default_factory=lambda: [0] * 16)
    memory_human_readable: list[str]  = field(default_factory=lambda: [''] * 16)
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
    output_signed_mode: bool = False

    def update(self):
        """Update the state based on the values of the control lines. This does
        not touch the various clocks, so this can be called as often as needed
        to keep every component in sync."""

        # Set control lines based on current microinstruction.
        self.update_control_signals()

        # Write to the bus
        if self.control_signals & microcode.AO:
            self.bus = self.reg_a
        if self.control_signals & microcode.EO:
            self.bus = self.alu
        if self.control_signals & microcode.IO:
            self.bus = self.reg_instruction & 0x0f
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
            # Perform subtraction by computing the 8bit twos-complement
            # representation of register B.
            self.alu = self.reg_a + (self.reg_b ^ 0xff & 0xff) + 1
        else:
            self.alu = self.reg_a + self.reg_b
        self.flag_carry = self.alu > 0xff
        self.alu &= 0xff
        self.flag_zero = self.alu == 0

        # Changes of instruction and flags registers affect the control lines
        self.update_control_signals()
    
    def update_control_signals(self):
        """Update the control signals based on the state of the microcode ROM
        module."""
        self.rom_address = (self.reg_instruction & 0xf0) >> 1
        self.rom_address += self.microinstruction_counter
        if self.reg_flags & 0b01:  # Carry flag
            self.rom_address += 1 << 7
        if self.reg_flags & 0b10:  # Zero flag
            self.rom_address += 1 << 8

        self.control_signals = microcode.ucode[self.rom_address]

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

        # Increment program counters
        if self.control_signals & microcode.CE and self.clock:
            self.reg_program_counter = (self.reg_program_counter + 1) % 16
        if not self.clock:
            self.microinstruction_counter = (self.microinstruction_counter + 1) % 5

        # Update the system state now that the clock has changed
        self.update()

        # Return the value written to the output module (if any)
        if self.clock and (self.control_signals & microcode.OI):
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


class Simulator:
    """Class representing the entire machine.

    Parameters
    ----------
    memory : list of int
        For each memory address (there should be a maximum of 16), the contents
        (an 8 bit number, so from 0-255) of the RAM at that address. Generally,
        you want to use the assembler to generate the RAM contens based on
        assembler code.
    memory_human_readable : list of str
        For each memory address, a human readable version of the contents of
        the RAM at that address. For example, it could be the line of assembler
        code that generated the opcode. By default (``None``), this is set to
        a binary representation of the memory.
    """
    def __init__(self, memory, memory_human_readable=None):
        self._init_memory = memory
        if memory_human_readable is None:
            self._init_memory_human_readable = [
                f'{addr + 1:02d} {content >> 4:04b} {content & 0xf:04b}'
                for addr, content in enumerate(memory)]
        else:
            self._init_memory_human_readable = memory_human_readable

        # Variables related to automatic stepping of the clock
        self.clock_automatic = False
        self.clock_speed = 1  # Hz
        self.last_clock_time = 0 # Keep track of when the next clock was last stepped

        # Initialize system state
        self.reset()

    def run_batch(self):
        """Run the simulator in batch mode until the HLT instruction is reached.

        Returns
        -------
        outputs : list of int
            The result of any OUT instructions encountered along the way.
        """
        self.state.keep_history = False  # Not needed, so turn off for extra speed
        outputs = list()
        while not self.state.control_signals & microcode.HLT:
            out = self.state.step()
            if out is not None:
                outputs.append(out)
        return outputs

    def step(self):
        """Step the clock while keeping track of time."""
        self.last_clock_time = time()
        self.state.step()

    def reset(self):
        """Reset the machine."""
        global _previous_states
        _previous_states.clear()
        self.state = State(
            memory=self._init_memory,
            memory_human_readable=self._init_memory_human_readable)
        self.state.update()


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('file', type=str, help='Program to execute')
    parser.add_argument('--no-interface', action='store_true',
                        help="Don't show the interface, but run the program in batch mode")
    parser.add_argument('-b', '--bin', action='store_true',
                        help='Specify that the program file is already assembled binary.')
    args = parser.parse_args()

    if args.bin:
        with open(args.file, 'rb') as f:
            simulator = Simulator(memory=f.read())
    else:
        with open(args.file) as f:
            simulator = Simulator(*assemble(f.read()))

    if args.no_interface:
        for out in simulator.run_batch():
            print(out)
    else:
        import curses
        import interface
        curses.wrapper(interface.run_interface, simulator)
