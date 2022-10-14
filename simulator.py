"""
Simulator for the SAP-1 8-bit breadboard computer.
"""
from argparse import ArgumentParser
from time import time
from collections import deque
from dataclasses import dataclass, asdict, field

import microcode
from assembler import assemble
from arduino import Arduino


# To enable steping the clock backwards, we keep track of previous state
# whenever we advance the clock.
_previous_states = deque(maxlen=10_000)


@dataclass
class State:
    """Object representing the state of the machine."""
    bus: int = 0
    memory: list[int] = field(default_factory=lambda: [0] * 512)
    memory_human_readable: list[str]  = field(default_factory=lambda: [''] * 512)
    EEPROM_MSB : list[int] = field(default_factory=lambda: microcode.EEPROM_MSB)
    EEPROM_LSB : list[int] = field(default_factory=lambda: microcode.EEPROM_LSB)
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

    # The arduino board that does the bootloading and handles streaming input
    arduino: Arduino = None

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
        self.arduino.write(self)

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
        self.arduino.read(self)

        # Transfer ALU flag outputs to the flags register
        if self.clock and (self.control_signals & microcode.FI):
            self.reg_flags = self.flag_carry + (self.flag_zero << 1)

        # Do ALU stuff, set flag outputs
        self.alu = self.reg_a
        if self.is_line_active(microcode.EI):
            # Invert register B before inputting it into the adder
            # Perform subtraction by computing the 8bit twos-complement
            # representation of register B.
            self.alu += self.reg_b ^ 0xff & 0xff
        else:
            self.alu += self.reg_b
        if self.is_line_active(microcode.EC):
            self.alu += 1
        self.flag_carry = self.alu > 0xff
        self.alu &= 0xff
        self.flag_zero = self.alu == 0

    def update_control_signals(self):
        """Update the control signals based on the microcode EEPROMs.

        The control word is formed by combining two EEPROMs. Together they form
        the LSB and MSB of the 16-bit control word.
        """
        self.rom_address = self.reg_instruction << 3
        self.rom_address += self.microinstruction_counter
        if self.reg_flags & 0b01:  # Carry flag
            self.rom_address += 1 << 11
        if self.reg_flags & 0b10:  # Zero flag
            self.rom_address += 1 << 12

        # Combine the two EEPROMs
        self.control_signals = (
            (self.EEPROM_MSB[self.rom_address] << 8) +
            (self.EEPROM_LSB[self.rom_address] & 0xff)
        )

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
            return (self.control_signals & line) != 0


class Simulator:
    """Class representing the entire machine.

    Parameters
    ----------
    memory : list of int
        For each memory address (there should be a maximum of 16), the contents
        (an 8 bit number, so from 0-255) of the RAM at that address. Generally,
        you want to use the assembler to generate the RAM contens based on
        assembler code.
    memory_human_readable : list of str | None
        For each memory address, a human readable version of the contents of
        the RAM at that address. For example, it could be the line of assembler
        code that generated the opcode. By default (``None``), this is set to
        a binary representation of the memory.
    input_data : bytes
        Data buffer to read from whenever an INP instruction is encountered.
    EEPROM_MSB : list of int | bytes | None
        The binary contents of the EEPROMs uses to control the most-significant
        8 bites of the control word. By default (``None``) the microcode
        defined in ``microcode.py`` is used.
    EEPROM_LSB : list of int | bytes | None
        The binary contents of the EEPROMs uses to control the
        least-significant 8 bites of the control word. By default (``None``)
        the microcode defined in ``microcode.py`` is used.
    """
    def __init__(self, memory, memory_human_readable=None, input_data=b'',
                 EEPROM_MSB=None, EEPROM_LSB=None):
        self._init_memory = memory
        if memory_human_readable is None:
            self._init_memory_human_readable = [
                f'{addr + 1:02d} {content >> 4:04b} {content & 0xf:04b}'
                for addr, content in enumerate(memory)]
        else:
            self._init_memory_human_readable = memory_human_readable

        self.input_data = input_data

        if EEPROM_MSB is None:
            self.EEPROM_MSB= microcode.EEPROM_MSB
        else:
            self.EEPROM_MSB = EEPROM_MSB
        if EEPROM_LSB is None:
            self.EEPROM_LSB= microcode.EEPROM_LSB
        else:
            self.EEPROM_LSB = EEPROM_LSB

        # Variables related to automatic stepping of the clock
        self.clock_automatic = False
        self.clock_speed = 1  # Hz
        self.last_clock_time = 0 # Keep track of when the next clock was last stepped
        while len(self._init_memory) < 512:
            self._init_memory.append(0)
        while len(self._init_memory_human_readable) < 512:
            self._init_memory_human_readable.append(
                f'{len(self._init_memory_human_readable):02x}: 0')

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
        return self.state.step()

    def reset(self):
        """Reset the machine."""
        global _previous_states
        _previous_states.clear()
        self.state = State(
            memory=self._init_memory,
            memory_human_readable=self._init_memory_human_readable,
            EEPROM_MSB=self.EEPROM_MSB,
            EEPROM_LSB=self.EEPROM_LSB,
            arduino=Arduino(self.input_data),
        )
        self.state.update()


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('program_file', type=str, help='Program to execute, written in assembly language.')
    parser.add_argument('-n', '--no-interface', action='store_true',
                        help="Don't show the interface, but run the program in batch mode.")
    parser.add_argument('-m', '--microcode', type=str, nargs='*', metavar='bin_file(s)',
                        help='EEPROM content to use as microcode (as a binary memory dump). Either as a single file containing 16-bit numbers, or as two files containing respectively the most-significant 8 bits and least-significant 8 bits.')
    parser.add_argument('-b', '--bin', action='store_true',
                        help='Specify that the program file is in binary rather than assembly language.')
    parser.add_argument('-i', '--input', type=str, default=None,
                        help='Specify an input file to read from when an INP instruction is encountered.')
    args = parser.parse_args()

    if args.microcode is None:
        EEPROM_MSB = None
        EEPROM_LSB = None
    elif len(args.microcode) == 1:
        with open(args.microcode[0], 'rb') as f:
            EEPROM = f.read()
            EEPROM_MSB = EEPROM[::2]
            EEPROM_LSB = EEPROM[1::2]
    elif len(args.microcode) == 2:
        with open(args.microcode[0], 'rb') as f:
            EEPROM_MSB = f.read()
        with open(args.microcode[1], 'rb') as f:
            EEPROM_LSB = f.read()
    else:
        raise ValueError('The --microcode argument takes either one or two files as parameter.')

    if args.input:
        with open(args.input, 'rb') as f:
            input_data = f.read()
    else:
        input_data = b''

    if args.bin:
        with open(args.program_file, 'rb') as f:
            simulator = Simulator(memory=list(f.read()), input_data=input_data,
                                  EEPROM_MSB=EEPROM_MSB, EEPROM_LSB=EEPROM_LSB)
    else:
        with open(args.program_file) as f:
            simulator = Simulator(*assemble(f.read()), input_data=input_data,
                                  EEPROM_MSB=EEPROM_MSB, EEPROM_LSB=EEPROM_LSB)

    if args.no_interface:
        for out in simulator.run_batch():
            print(out)
    else:
        import curses
        import interface
        curses.wrapper(interface.run_interface, simulator)
