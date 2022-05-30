from argparse import ArgumentParser
import sys
import struct

instruction_to_num = {
    'nop': 0,
    'lda': 1,
    'add': 2,
    'sub': 3,
    'sta': 4,
    'ldi': 5,
    'jmp': 6,
    'jc': 7,
    'jz': 8,
    'jnc': 9,
    'jzc': 10,
    'shl': 11,
    'inc': 12,
    'dec': 13,
    'out': 14,
    'hlt': 15,
}
num_to_instruction = {v: k for k, v in instruction_to_num.items()}


def assemble(program_code, verbose=False):
    labels = dict()
    output = list()

    # Parse file
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
            labels[label.strip().lower()] = len(output)

        line = line.strip()
        if len(line) == 0:
            continue

        instruction, *params = line.split()
        instruction = instruction.lower()
        if instruction in ['nop', 'out', 'hlt', 'shl']:
            if len(params) > 0:
                error(f'{instruction} takes no parameters')
            output.append((instruction,))
        else:
            if len(params) != 1:
                error(f'{instruction} takes a single parameter')
            param = params[0]
            if param.isnumeric():
                param = int(param)
                if not (0 <= param <= 255):
                    error('Parameter must be 0-255')

            output.append((instruction,param))

    # Resolve labels and convert to binary
    bin_output = list()
    for line in output:
        instruction = line[0]
        if instruction == 'db':
            bin_line = 0
        else:
            bin_line = instruction_to_num[instruction.lower()] << 4
        if len(line) == 2:
            param = line[1]
            if type(param) == str:
                param = labels[param.lower()]
            bin_line += param
        bin_output.append(bin_line)

    # Create human readable version of the memory contents
    human_readable = list()
    addr_to_label = {v: k for k, v in labels.items()}
    for addr, (o, b) in enumerate(zip(output, bin_output)):
        i = ' '.join([str(x) for x in o])
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
