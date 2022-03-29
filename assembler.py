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


def assemble(fname, verbose=False):
    labels = dict()
    output = list()

    # Parse file
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith(';'):
                continue
            if line.endswith(':'):
                labels[line[:-1].lower()] = len(output)
                continue

            instruction, *params = line.split(' ')
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
            bin_line = instruction_to_num[instruction] << 4
        if len(line) == 2:
            param = line[1]
            if type(param) == str:
                param = labels[param]
            bin_line += param
        bin_output.append(bin_line)

    if verbose:
        for addr, (o, b) in enumerate(zip(output, bin_output)):
            i = ' '.join([str(x) for x in o])
            print(f"{addr:04b}:  {b >> 4:04b} {b & 0x0f:04b}  {i}")

    return bin_output

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python assembler.py PROGRAM_TO_ASSEMBLE')
        sys.exit(1)
    assemble(sys.argv[1], verbose=True)
