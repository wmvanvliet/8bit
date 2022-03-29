"""
Simulator for the SAP-1 8-bit breadboard computer.
"""
import sys
import microcode
from assembler import assemble


class state:
    bus = 0
    memory = assemble(sys.argv[1])
    microcode = microcode.ucode

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
        zero = True

    # Other stuff
    alu = 0
    microinstruction_counter = 0
    clock = False

def step():
    # Set control lines based on current microinstruction
    if not state.clock:
        # Build microcode ROM address
        rom_address = (state.register.instruction & 0xf0) >> 1
        rom_address += state.microinstruction_counter
        if state.flag.carry:
            rom_address += 1 << 7
        if state.flag.zero:
            rom_address += 1 << 8

        microinstruction = state.microcode[rom_address]
        #print(f'EXECUTING: {state.register.instruction >> 4:04b} {state.register.instruction & 0x0f:04b}     {microinstruction >> 8:08b} {microinstruction & 0xff:08b}')

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
        state.memory[state.register.memory_address] = state.bus
    if state.control.output_in and state.clock:
        if state.bus != state.register.output:
            state.register.output = state.bus
            print('OUTPUT:', state.register.output)

    # Do ALU stuff, set flags
    if state.control.alu_subtract:
        state.alu = state.register.a - state.register.b
    else:
        state.alu = state.register.a + state.register.b
    if state.alu > 255:
        state.flag.carry = True
        state.alu = state.alu % 255
    else:
        state.flag.carry = False
    if state.alu < 0:
        state.alu += 255
    state.flag.zero = state.alu == 0

    # Increment counters
    if state.control.program_counter_enable and state.clock:
        state.register.program_counter = (state.register.program_counter + 1) % 255
    if not state.clock:
        state.microinstruction_counter = (state.microinstruction_counter + 1) % 5

    # Flip clock signal
    state.clock = not state.clock


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python simulator.py PROGRAM_TO_EXECUTE')
        sys.exit(1)

    while not state.control.halt:
        step()
