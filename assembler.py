import sys

opcodes = {
    'nop': 0x00,
    'ld':  dict(RA=1 << 3, RV=2 << 3, AR=3 << 3, AV=1, AA=2),
    'add': dict(RA=4 << 3, RV=5 << 3, AR=6 << 3, AV=3),
    'sub': dict(RA=7 << 3, RV=8 << 3, AR=9 << 3, AV=4),
    'cmp': dict(RA=10 << 3, RV=11 << 3, AR=12 << 3, AV=5),
    'sla': dict(R=13 << 3, A=6),
    'jp':  dict(R=14 << 3, A=7, V=(30 << 3) + 0),
    'jc':  dict(R=15 << 3, A=(30 << 3) + 1, V=(30 << 3) + 2),
    'jz':  dict(R=16 << 3, A=(30 << 3) + 3, V=(30 << 3) + 4),
    'out': dict(R=(17 << 3) + 0, A=(30 << 3) + 5, V=(30 << 3) + 6),
    'js':  (30 << 3) + 7,
    'hlt': 0xFF,
}
#num_to_instruction = {v: k for k, v in opcodes.items()}


def parse_param(param):
    """Parse a parameter."""
    param = param.strip()

    # Is the param a register?
    if param in list('abcdefgh'):
        return 'register', param

    # Is the param a memory address?
    if param.startswith('$'):
        try:
            return 'address', int(param[1:])
        except:
            raise ValueError(f'Invalid address: {param}')

    # Try parsing the param as a number
    try:
        return 'value', int(param)
    except:
        pass

    # Try parsing as a label. Perhaps there is an offset specified.
    if '+' in param:
        param, offset = param.split('+', 1)
        try:
            return 'label', param, int(offset), f'{param} + {offset}'
        except:
            raise ValueError(f'Invalid offset value {offset}')
    if '-' in param:
        param, offset = param.split('-', 1)
        try:
            return 'label', param, -int(offset), f'{param} - {offset}'
        except:
            raise ValueError(f'Invalid offset value {offset}')

    # Label without an offset
    return 'label', param, 0, param


def assemble(fname, verbose=False):
    labels = dict()
    output = list()
    output_readable = list()

    # Jump past the registers
    output.append(('instr', 'js', opcodes['js']))
    output_readable.append(('js', 1))

    # Memory dedicated to registers
    for _ in range(8):
        output.append(('db', 0))
    output_readable.append(('db  0 (x8)', 8))

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

            instruction, *params = line.split(None, 1)
            if len(params) > 0:
                params = params[0].split(',')
            if len(params) > 2:
                raise ValueError('Instructions take at most 2 parameters.')

            instruction = instruction.lower()
            if instruction == 'db':
                if not len(params) == 1:
                    raise ValueError(f'Instruction {instruction} needs a parameter.')
                try:
                    output.append(('db', int(params[0])))
                    output_readable.append((f'db  {int(params[0]):d}', 1))

                except:
                    raise ValueError(f'Invalid value for "db": {params[0]}')
                continue

            if not instruction in opcodes:
                raise ValueError(f'Invalid instruction ({instruction})')
            opcode = opcodes[instruction]

            if type(opcode) == int:
                if len(params) > 0:
                    raise ValueError(f'Instruction {instruction} does not take any parameters.')
                output.append(('instr', instruction, opcode))
                output_readable.append((f'{instruction:3s}', 1))
                continue

            if len(params) == 0:
                raise ValueError(f'Instruction {instruction} needs a parameter.')

            params = [parse_param(p) for p in params]
            if len(params) == 1:
                typ = params[0][0]
                if typ == 'register':
                    register = params[0][1]
                    if 'R' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take a register as a parameter.')
                    output.append(('instr_with_reg', instruction, opcode['R'], register))
                    output_readable.append((f'{instruction:3s} {register}', 1))
                elif typ == 'value':
                    value = params[0][1]
                    if 'V' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take a value as a parameter.')
                    output.append(('instr', instruction, opcode['V']))
                    output.append(('param', value))
                    output_readable.append((f'{instruction:3s} {value:d}', 2))
                elif typ == 'label':
                    label, offset, readable = params[0][1:]
                    if 'A' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take an address as a parameter.')
                    output.append(('instr', instruction, opcode['A']))
                    output.append(('label', label, offset))
                    output_readable.append((f'{instruction:3s} {readable}', 2))
                elif typ == 'address':
                    address = params[0]
                    if 'A' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take an address as a parameter.')
                    output.append(('instr', instruction, opcode['A']))
                    output.append(('param', address))
                    output_readable.append((f'{instruction:3s} ${address:d}', 2))
                continue

            if len(params) == 2:
                typ1 = params[0][0]
                typ2 = params[1][0]
                if typ1 == 'register' and typ2 == 'register':
                    register1 = params[0][1]
                    register2 = params[1][1]
                    if register2 == 'a':
                        register1, register2 = register2, register1
                        order = 'AR'
                    else:
                        order = 'RA'
                    if order not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take two registers as parameters.')
                    output.append(('instr_with_reg', instruction, opcode[order], register1))
                    output.append(('param', 'abcdefgh'.index(register2)))
                    output_readable.append((f'{instruction:3s} {params[0][1]}, {params[1][1]}', 2))
                elif typ1 == 'register' and typ2 == 'address':
                    register = params[0][1]
                    address = params[1][1]
                    if 'RA' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take a register and an address as parameters.')
                    output.append(('instr_with_reg', instruction, opcode['RA'], register))
                    output.append(('param', address))
                    output_readable.append((f'{instruction:3s} {register}, ${address:d}', 2))
                elif typ1 == 'register' and typ2 == 'label':
                    register = params[0][1]
                    label, offset, readable = params[1][1:]
                    if 'RA' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take a register and an address as parameters.')
                    output.append(('instr_with_reg', instruction, opcode['RA'], register))
                    output.append(('label', label, offset))
                    output_readable.append((f'{instruction:3s} {register}, {readable}', 2))
                elif typ1 == 'register' and typ2 == 'value':
                    register = params[0][1]
                    value = params[1][1]
                    if 'RV' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take a register and a value as parameters.')
                    output.append(('instr_with_reg', instruction, opcode['RV'], register))
                    output.append(('param', value))
                    output_readable.append((f'{instruction:3s} {register}, {value:d}', 2))
                elif typ1 == 'address' and typ2 == 'register':
                    address = params[0][1]
                    register = params[1][1]
                    if 'AR' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take an address and a register as parameters.')
                    output.append(('instr_with_reg', instruction, opcode['AR'], register))
                    output.append(('param', address))
                    output_readable.append((f'{instruction:3s} ${address:d} {register}', 2))
                elif typ1 == 'address' and typ2 == 'address':
                    address1 = params[0][1]
                    address2 = params[1][1]
                    if 'AA' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take two addresses as parameters.')
                    output.append(('instr', instruction, opcode['AA']))
                    output.append(('param', address2))
                    output.append(('param', address1))
                    output_readable.append((f'{instruction:3s} ${address1:d} ${address2:d}', 3))
                elif typ1 == 'address' and typ2 == 'label':
                    address = params[0][1]
                    label, offset, readable = params[1][1:]
                    if 'AA' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take two addresses as parameters.')
                    output.append(('instr', instruction, opcode['AA']))
                    output.append(('label', label, offset))
                    output.append(('param', address))
                    output_readable.append((f'{instruction:3s} ${address:d} {readable}', 3))
                elif typ1 == 'address' and typ2 == 'value':
                    address = params[0][1]
                    value = params[1][1]
                    if 'AV' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take an address and a value as parameters.')
                    output.append(('instr_with', instruction, opcode['AV']))
                    output.append(('param', value))
                    output.append(('param', address))
                    output_readable.append((f'{instruction:3s} ${address:d} {value:d}', 3))
                elif typ1 == 'label' and typ2 == 'register':
                    label, offset, readable = params[0][1:]
                    register = params[1][1]
                    if 'AR' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take an address and a register as parameters.')
                    output.append(('instr_with_reg', instruction, opcode['AR'], register))
                    output.append(('label', label, offset))
                    output_readable.append((f'{instruction:3s} {readable} {register}', 2))
                elif typ1 == 'label' and typ2 == 'address':
                    label, offset, readable = params[0][1:]
                    address = params[1][1]
                    if 'AA' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take two addresses as parameters.')
                    output.append(('instr', instruction, opcode['AA']))
                    output.append(('label', label, offset))
                    output.append(('param', address))
                    output_readable.append((f'{instruction:3s} {readable} ${address:d}', 3))
                elif typ1 == 'label' and typ2 == 'label':
                    label1, offset1, readable1 = params[0][1:]
                    label2, offset2, readable2 = params[1][1:]
                    if 'AA' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take two addresses as parameters.')
                    output.append(('instr', instruction, opcode['AA']))
                    output.append(('label', label2, offset2))
                    output.append(('label', label1, offset1))
                    output_readable.append((f'{instruction:3s} {readable1} {readable2}', 3))
                elif typ1 == 'label' and typ2 == 'value':
                    label, offset, readable = params[0][1:]
                    value = params[1][1]
                    if 'AV' not in opcode:
                        raise ValueError(f'Instruction {instruction} does not take an address and a value as parameters.')
                    output.append(('instr', instruction, opcode['AV']))
                    output.append(('param', value))
                    output.append(('label', label, offset))
                    output_readable.append((f'{instruction:3s} {readable} {value:d}', 3))
                continue

    # from pprint import pprint
    # pprint(output)

    # Resolve labels and convert to binary
    bin_output = list()
    for typ, *content in output:
        if typ == 'instr':
            bin_output.append(content[1])
        elif typ == 'instr_with_reg':
            bin_output.append(content[1] + 'abcdefgh'.index(content[2]))
        elif typ == 'param':
            bin_output.append(content[0])
        elif typ == 'label':
            try:
                bin_output.append(labels[content[0]] + content[1])
            except KeyError:
                raise ValueError(f'Unknown label {content[0]}')
        elif typ == 'db':
            bin_output.append(content[0])

    # pprint(bin_output)

    # Create human readable version of the memory contents
    human_readable = list()
    addr_to_label = {v: k for k, v in labels.items()}
    bin_iter = enumerate(bin_output)
    for readable, n_bytes in output_readable:
        addr, binary = next(bin_iter)
        s = f'{addr:3d} {addr:08b}    {binary:08b}    {readable}'
        if label := addr_to_label.get(addr, ''):
            s += f'    ({label})'
        human_readable.append(s)
        for _ in range(n_bytes - 1):
            addr, binary = next(bin_iter)
            s = f'{addr:3d} {addr:08b}    {binary:08b}'
            if label := addr_to_label.get(addr, ''):
                s += f'    ({label})'
            human_readable.append(s)

    if verbose:
        for line in human_readable:
            print(line)

    return bin_output, human_readable


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python assembler.py PROGRAM_TO_ASSEMBLE')
        sys.exit(1)
    assemble(sys.argv[1], verbose=True)
