from argparse import ArgumentParser
import sys
import struct

opcodes = {
    'nop': 0,
    'lda': 1,
    'add': 2,
    'sub': 3,
    'sta': 4,
    'ldi': 5,
    'jmp': 6,
    'jc': 7,
    'jz': 8,
    'out': 14,
    'hlt': 15,
}
num_to_instruction = {v: k for k, v in opcodes.items()}


def assemble(program_code, verbose=False):
    # Keep track of the memory addresses at which labels are defined
    labels = dict()


    # Step 1: Parse file, producing a list of tokens. Each token represents one
    # byte in memory. These tokens will be translated into binary code during
    # the next step.
    tokens = list()

    for line_nr, line in enumerate(program_code.split('\n')):
        def error(msg):
            print(f'L{line_nr + 1}: {line}')
            print(msg)
            sys.exit(1)

        # Deal with comments
        if ';' in line:
            line, _ = line.split(';', 1)
        
        # Deal with labels:
        if ':' in line:
            label, line = line.split(':', 1)
            labels[label.strip().lower()] = len(tokens)

        line = line.strip()
        if len(line) == 0:
            continue

        instruction, *params = line.split()
        instruction = instruction.lower()
        if instruction in ['nop', 'out', 'hlt']:
            if len(params) > 0:
                error(f'{instruction} takes no parameters')
            tokens.append((instruction,))
        else:
            if len(params) != 1:
                error(f'{instruction} takes a single parameter')
            param = params[0]
            if param.isnumeric():
                param = int(param)
                if not (0 <= param <= 255):
                    error('Parameter must be 0-255')

            tokens.append((instruction, param))

    # Convert each token to a binary number
    bin_output = list()
    for token in tokens:
        instruction = token[0]

        # The "db" pseudo-instruction places the parameter in memory
        if instruction == 'db':
            bin_output.append(token[1])
            continue

        # Get the opcode for the instruction and place it into the upper 4 bits
        # of the memory.
        bin_line = opcodes[instruction] << 4

        # If the instruction has a parameter, place it into the lower 4 bits of
        # the memory.
        if len(token) == 2:
            param = token[1]
            # Parameter could be a label, in which case, translate it into the
            # memory address it refers to.
            if type(param) == str:
                param = labels[param]
            # Place parameter value into the lower 4 bits
            bin_line += param
        bin_output.append(bin_line)

    # Create human readable version of the memory contents
    human_readable = list()
    addr_to_label = {v: k for k, v in labels.items()}
    for addr, (t, b) in enumerate(zip(tokens, bin_output)):
        i = ' '.join([str(x) for x in t])
        label = addr_to_label.get(addr, '')
        if label:
            label = f'({label})'
        human_readable.append(f"{addr:02d}: {b >> 4:04b} {b & 0x0f:04b}  {i} {label}")

    if verbose:
        for line in human_readable:
            print(line)

    return bin_output, human_readable


def disassemble(bin_code):
    """Disassemble a given number into a human readable assembler instruction.

    Parameters
    ----------
    bin_code : int
        The number to disassemble.

    Returns
    -------
    asm : str
        The human readable assembler instruction.
    """
    instruction = num_to_instruction[bin_code >> 4]
    if instruction in ['nop', 'out', 'hlt']:
        # Instruction doesn't take a parameter
        return instruction
    else:
        # Instruction along with its parameter
        return f'{instruction} {bin_code & 0x0f:d}'


if __name__ == '__main__':
    parser = ArgumentParser(description='Assembler for the 8-bit breadboard computer. By default, just prints the assembled version of the code.')
    parser.add_argument('file', type=str, help='Assembly code file to assemble.')
    parser.add_argument('-o', '--output-file', type=str, default=None, help='Write the compiled program to a file.')
    args = parser.parse_args()

    with open(args.file) as f:
        bin_output, _ = assemble(f.read(), verbose=True)

    if args.output_file:
        with open(args.output_file, 'wb') as f:
            for line in bin_output:
                print(f'{line} {line:02x}')
                f.write(struct.pack('<B', line))
