import sys

opcodes = {
    'nop': 0x00,
    'hlt': 0xFF,
    'ld':  dict(RA=1 << 3, RV=2 << 3, RR=3 << 3, AR=4 << 3, AV=1, AA=2),
    'add': dict(RA=5 << 3, RV=6 << 3, RR=7 << 3, AR=8 << 3, AV=3, AA=4),
    'sub': dict(RA=9 << 3, RV=10 << 3, RR=11 << 3, AR=12 << 3, AV=5, AA=6),
    'cmp': dict(RA=10 << 3, RV=11 << 3, RR=12 << 3, AR=13 << 3, AV=29 << 3 + 0),
    'sla': dict(R=14 << 3, A=29 << 3 + 1),
    'jp':  dict(R=15 << 3, A=29 << 3 + 2, V=29 << 3 + 3),
    'jc':  dict(R=18 << 3, A=29 << 3 + 4, V=29 << 3 + 5),
    'jz':  dict(R=19 << 3, A=29 << 3 + 6, V=29 << 3 + 7),
    'jr':  dict(R=20 << 3, A=30 << 3 + 0, V=30 << 3 + 1),
    'jrc':  dict(R=21 << 3, A=30 << 3 + 2, V=30 << 3 + 3),
    'jrz':  dict(R=22 << 3, A=30 << 3 + 4, V=30 << 3 + 5),
    'out': dict(R=23 << 3, A=31 << 3 + 0),
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


def assemble(fname, verbose=False):
    labels = dict()
    output = list()

    # Parse file
    with open(fname) as f:
        for line in f:
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

            instruction, *param = line.split(None, 1)
            instruction = instruction.lower()
            if instruction in ['nop', 'out', 'hlt']:
                assert len(param) == 0, f'{instruction} takes no parameters'
                output.append(('instr', instruction))
            else:
                assert len(param) > 0, f'{instruction} takes a single parameter'
                if instruction != 'db':
                    output.append(('instr', instruction))
                output.append(('param', param[0]))

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
    if len(sys.argv) < 2:
        print('python assembler.py PROGRAM_TO_ASSEMBLE')
        sys.exit(1)
    assemble(sys.argv[1], verbose=True)
