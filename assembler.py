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


def parse_param(param, labels):
    """Parse a parameter given a list of tokens."""
    parsed_tokens = list()

    for token in param.split():
        try:  # try parsing token as a number
            parsed_token = int(token, 0)
        except ValueError:  # not a number
            if token == '+' or token == '-':
                parsed_token = token  # we'll resolve this later
            elif token.lower() in labels:
                parsed_token = labels[token.lower()]
            else:
                raise ValueError('Unknown label "{token}"')
        parsed_tokens.append(parsed_token)

    # Resolve + and -
    if (len(parsed_tokens) - 1) % 2 != 0:
        raise ValueError(f'Cannot parse "{param}"')
    value = parsed_tokens[0]
    for op, v in zip(parsed_tokens[1::2], parsed_tokens[2::2]):
        if op == '+':
            value += v
        elif op == '-':
            value -= v
        else:
            raise ValueError(f'Cannot parse "{param}"')
    return value


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
        if instruction in ['nop', 'out', 'hlt']:
            if len(params) > 0:
                error(f'{instruction} takes no parameters')
            output.append(('instr', instruction))
        else:
            if len(params) != 1:
                error(f'{instruction} takes a single parameter')
            if instruction != 'db':
                output.append(('instr', instruction))
            output.append(('param', params[0]))

    # Resolve labels and convert to binary
    bin_output = list()
    for typ, content in output:
        if typ == 'instr':
            bin_line = opcodes[content]
        elif typ == 'param':
            bin_line = parse_param(content, labels)
        bin_output.append(bin_line)

    # Create human readable version of the memory contents
    human_readable = list()
    addr_to_label = {v: k for k, v in labels.items()}
    for addr, ((typ, content), bin_content) in enumerate(zip(output, bin_output)):
        label = addr_to_label.get(addr, '')
        if label:
            label = f'({label})'
        human_readable.append(f"{addr:02x}: {bin_content:08b} {content} {label}")

    if verbose:
        for line in human_readable:
            print(line)

    return bin_output, human_readable


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
