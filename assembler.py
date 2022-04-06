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
                output.append(('instr', instruction))
            else:
                assert len(params) == 1, f'{instruction} takes a single parameter'
                param = params[0]
                if param.isnumeric():
                    param = int(param)
                    assert 0 <= param <= 255, 'Parameter must be 0-255'

                if instruction != 'db':
                    output.append(('instr', instruction))
                output.append(('param', param))

    # Resolve labels and convert to binary
    bin_output = list()
    for typ, content in output:
        if typ == 'instr':
            bin_line = instruction_to_num[content.lower()]
        elif typ == 'param':
            if type(content) == str:
                content = labels[content.lower()]
            bin_line = content
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
