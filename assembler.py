import sys

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
    'cmp': 11,
    'inc': 12,
    'dec': 13,
    'out': 14,
    'hlt': 15,
}
num_to_instruction = {v: k for k, v in instruction_to_num.items()}


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

            instruction, *params = line.split()
            instruction = instruction.lower()
            if instruction in ['nop', 'out', 'hlt']:
                assert len(params) == 0, f'{instruction} takes no parameters'
                output.append((instruction,))
            else:
                assert len(params) == 1, f'{instruction} takes a single parameter'
                param = params[0]
                if param.isnumeric():
                    param = int(param)
                    assert 0 <= param <= 255, 'Parameter must be 0-255'

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
    if len(sys.argv) < 2:
        print('python assembler.py PROGRAM_TO_ASSEMBLE')
        sys.exit(1)
    assemble(sys.argv[1], verbose=True)
