from argparse import ArgumentParser
import sys
import struct

opcodes = {
    'nop': 0x00,
    'ld':  dict(RA=1 << 3, RV=2 << 3, AR=3 << 3, AV=128, AA=129, RI=15 << 3),
    'add': dict(R=4 << 3, A=130, V=131),
    'sub': dict(R=5 << 3, A=132, V=133),
    'cp':  dict(R=6 << 3, A=134, V=135),
    'jp':  dict(R=7 << 3, A=136, V=137),
    'jc':  dict(R=8 << 3, A=138, V=139),
    'jz':  dict(R=9 << 3, A=140, V=141),
    'jnc': dict(R=10 << 3, A=142, V=143),
    'jnz': dict(R=11 << 3, A=144, V=145),
    'out': dict(R=12 << 3, A=146, V=147),
    'jsr': dict(V=148),
    'ret': 149,
    'adc': dict(R=13 << 3, A=150, V=151),
    'sbc': dict(R=14 << 3, A=152, V=153),
    'inc': 154,
    'dec': 155,
    'djnz': dict(V=156),
    'inp': 157,
    'hlt': 255,
}


def parse_param(param, as_address=False):
    """Parse a parameter."""
    param = param.strip()

    # Indirect addressing
    if param.startswith('[') and param.endswith(']'):
        return parse_param(param[1:-1], as_address=True)

    # Is the param a register?
    if param in list('abcdefgh'):
        return 'register', param

    # Try parsing the param as a number
    try:
        return 'address' if as_address else 'value', int(param)
    except:
        pass

    # Try parsing as a label. Perhaps there is an offset specified.
    if '+' in param:
        param, offset = param.split('+', 1)
        try:
            if as_address:
                return 'label_addr', param, int(offset), f'[{param} + {offset}]'
            else:
                return 'label', param, int(offset), f'{param} + {offset}'
        except:
            raise ValueError(f'Invalid offset value {offset}')
    if '-' in param:
        param, offset = param.split('-', 1)
        try:
            if as_address:
                return 'label_addr', param, -int(offset), f'[{param} - {offset}]'
            else:
                return 'label', param, -int(offset), f'{param} - {offset}'
        except:
            raise ValueError(f'Invalid offset value {offset}')

    # Label without an offset
    return 'label_addr' if as_address else 'label', param, 0, param


def assemble(program_code, verbose=False):
    labels_text = dict()
    labels_data = dict()
    output_text = list()
    output_data = list()
    output_text_readable = list()
    output_data_readable = list()

    labels = labels_text
    output = output_text
    output_readable = output_text_readable

    output_data_readable.append(('db 0 (x8)', 8))

    # Parse text
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

        instruction, *params = line.split(None, 1)
        if len(params) > 0:
            params = params[0].split(',')
        if len(params) > 2:
            error('Instructions take at most 2 parameters.')

        instruction = instruction.lower()
        if instruction == 'db':
            if not len(params) == 1:
                error(f'Instruction {instruction} needs a parameter.')
            try:
                output.append(('db', int(params[0])))
                output_readable.append((f'db {int(params[0]):d}', 1))

            except:
                error(f'Invalid value for "db": {params[0]}')
            continue
        elif instruction == 'section':
            if not len(params) == 1:
                error(f'Instruction {instruction} needs a parameter.')
            if params[0] == '.text':
                labels = labels_text
                output = output_text
                output_readable = output_text_readable
            elif params[0] == '.data':
                labels = labels_data
                output = output_data
                output_readable = output_data_readable
            else:
                error('Section name must be either .text or .data')
            continue

        if not instruction in opcodes:
            error(f'Invalid instruction ({instruction})')
        opcode = opcodes[instruction]

        if type(opcode) == int:
            if len(params) > 0:
                error(f'Instruction {instruction} does not take any parameters.')
            output.append(('instr', instruction, opcode))
            output_readable.append((f'{instruction:3s}', 1))
            continue

        if len(params) == 0:
            error(f'Instruction {instruction} needs a parameter.')

        params = [parse_param(p) for p in params]
        if len(params) == 1:
            typ = params[0][0]
            if typ == 'register':
                register = params[0][1]
                if 'R' not in opcode:
                    error(f'Instruction {instruction} does not take a register as a parameter.')
                output.append(('instr_with_reg', instruction, opcode['R'], register))
                output_readable.append((f'{instruction} {register}', 1))
            elif typ == 'value':
                value = params[0][1]
                if 'V' not in opcode:
                    error(f'Instruction {instruction} does not take a value as a parameter.')
                output.append(('instr', instruction, opcode['V']))
                output.append(('param', value))
                output_readable.append((f'{instruction} {value:d}', 2))
            elif typ == 'label':
                label, offset, readable = params[0][1:]
                if 'V' not in opcode:
                    error(f'Instruction {instruction} does not take a value as a parameter.')
                output.append(('instr', instruction, opcode['V']))
                output.append(('label', label, offset))
                output_readable.append((f'{instruction} {readable}', 2))
            elif typ == 'address':
                address = params[0]
                if 'A' not in opcode:
                    error(f'Instruction {instruction} does not take an address as a parameter.')
                output.append(('instr', instruction, opcode['A']))
                output.append(('param', address))
                output_readable.append((f'{instruction} ${address:d}', 2))
            elif typ == 'label_addr':
                label, offset, readable = params[0][1:]
                if 'A' not in opcode:
                    error(f'Instruction {instruction} does not take an address as a parameter.')
                output.append(('instr', instruction, opcode['A']))
                output.append(('label', label, offset))
                output_readable.append((f'{instruction} {readable}', 2))
            else:
                error(f'Invalid parameter for instruction {instruction}.')
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
                    error(f'Instruction {instruction} does not take two registers as parameters.')
                output.append(('instr_with_reg', instruction, opcode[order], register1))
                output.append(('param', 'abcdefgh'.index(register2)))
                output_readable.append((f'{instruction} {params[0][1]},{params[1][1]}', 2))
            elif typ1 == 'register' and typ2 == 'address':
                register = params[0][1]
                address = params[1][1]
                if 'RA' not in opcode:
                    error(f'Instruction {instruction} does not take a register and an address as parameters.')
                output.append(('instr_with_reg', instruction, opcode['RA'], register))
                output.append(('param', address))
                output_readable.append((f'{instruction} {register},${address:d}', 2))
            elif typ1 == 'register' and typ2 == 'label':
                register = params[0][1]
                label, offset, readable = params[1][1:]
                if 'RV' not in opcode:
                    error(f'Instruction {instruction} does not take a register and a value as parameters.')
                output.append(('instr_with_reg', instruction, opcode['RV'], register))
                output.append(('label', label, offset))
                output_readable.append((f'{instruction} {register},{readable}', 2))
            elif typ1 == 'register' and typ2 == 'label_addr':
                register = params[0][1]
                label, offset, readable = params[1][1:]
                if 'RA' not in opcode:
                    error(f'Instruction {instruction} does not take a register and an address as parameters.')
                output.append(('instr_with_reg', instruction, opcode['RA'], register))
                output.append(('label', label, offset))
                output_readable.append((f'{instruction} {register},{readable}', 2))
            elif typ1 == 'register' and typ2 == 'value':
                register = params[0][1]
                value = params[1][1]
                if 'RV' not in opcode:
                    error(f'Instruction {instruction} does not take a register and a value as parameters.')
                output.append(('instr_with_reg', instruction, opcode['RV'], register))
                output.append(('param', value))
                output_readable.append((f'{instruction} {register},{value:d}', 2))
            elif typ1 == 'address' and typ2 == 'register':
                address = params[0][1]
                register = params[1][1]
                if 'AR' not in opcode:
                    error(f'Instruction {instruction} does not take an address and a register as parameters.')
                output.append(('instr_with_reg', instruction, opcode['AR'], register))
                output.append(('param', address))
                output_readable.append((f'{instruction} ${address:d},{register}', 2))
            elif typ1 == 'address' and typ2 == 'address':
                address1 = params[0][1]
                address2 = params[1][1]
                if 'AA' not in opcode:
                    error(f'Instruction {instruction} does not take two addresses as parameters.')
                output.append(('instr', instruction, opcode['AA']))
                output.append(('param', address2))
                output.append(('param', address1))
                output_readable.append((f'{instruction} ${address1:d},${address2:d}', 3))
            elif typ1 == 'address' and typ2 == 'label':
                address = params[0][1]
                label, offset, readable = params[1][1:]
                if 'AV' not in opcode:
                    error(f'Instruction {instruction} does not take an address and a value as parameters.')
                output.append(('instr', instruction, opcode['AV']))
                output.append(('label', label, offset))
                output.append(('param', address))
                output_readable.append((f'{instruction} ${address:d},{readable}', 3))
            elif typ1 == 'address' and typ2 == 'label_addr':
                address = params[0][1]
                label, offset, readable = params[1][1:]
                if 'AA' not in opcode:
                    error(f'Instruction {instruction} does not take two addresses as parameters.')
                output.append(('instr', instruction, opcode['AA']))
                output.append(('label', label, offset))
                output.append(('param', address))
                output_readable.append((f'{instruction} ${address:d},{readable}', 3))
            elif typ1 == 'address' and typ2 == 'value':
                address = params[0][1]
                value = params[1][1]
                if 'AV' not in opcode:
                    error(f'Instruction {instruction} does not take an address and a value as parameters.')
                output.append(('instr_with', instruction, opcode['AV']))
                output.append(('param', value))
                output.append(('param', address))
                output_readable.append((f'{instruction} ${address:d},{value:d}', 3))
            elif typ1 == 'label_addr' and typ2 == 'register':
                label, offset, readable = params[0][1:]
                register = params[1][1]
                if 'AR' not in opcode:
                    error(f'Instruction {instruction} does not take an address and a register as parameters.')
                output.append(('instr_with_reg', instruction, opcode['AR'], register))
                output.append(('label', label, offset))
                output_readable.append((f'{instruction} {readable},{register}', 2))
            elif typ1 == 'label_addr' and typ2 == 'address':
                label, offset, readable = params[0][1:]
                address = params[1][1]
                if 'AA' not in opcode:
                    error(f'Instruction {instruction} does not take two addresses as parameters.')
                output.append(('instr', instruction, opcode['AA']))
                output.append(('label', label, offset))
                output.append(('param', address))
                output_readable.append((f'{instruction} {readable},${address:d}', 3))
            elif typ1 == 'label_addr' and typ2 == 'label':
                label1, offset1, readable1 = params[0][1:]
                label2, offset2, readable2 = params[1][1:]
                if 'AV' not in opcode:
                    error(f'Instruction {instruction} does not take an address and a value as parameters.')
                output.append(('instr', instruction, opcode['AV']))
                output.append(('label', label2, offset2))
                output.append(('label', label1, offset1))
                output_readable.append((f'{instruction} {readable1},{readable2}', 3))
            elif typ1 == 'label_addr' and typ2 == 'label_addr':
                label1, offset1, readable1 = params[0][1:]
                label2, offset2, readable2 = params[1][1:]
                if 'AA' not in opcode:
                    error(f'Instruction {instruction} does not take two addresses as parameters.')
                output.append(('instr', instruction, opcode['AA']))
                output.append(('label', label2, offset2))
                output.append(('label', label1, offset1))
                output_readable.append((f'{instruction} {readable1},{readable2}', 3))
            elif typ1 == 'label_addr' and typ2 == 'value':
                label, offset, readable = params[0][1:]
                value = params[1][1]
                if 'AV' not in opcode:
                    error(f'Instruction {instruction} does not take an address and a value as parameters.')
                output.append(('instr', instruction, opcode['AV']))
                output.append(('param', value))
                output.append(('label', label, offset))
                output_readable.append((f'{instruction} {readable},{value:d}', 3))
            else:
                error(f'Invalid parameters for instruction {instruction}.')
            continue

    # Resolve labels and convert to binary
    output_bin_text = list()
    for typ, *content in output_text:
        if typ == 'instr':
            output_bin_text.append(content[1])
        elif typ == 'instr_with_reg':
            output_bin_text.append(content[1] + 'abcdefgh'.index(content[2]))
        elif typ == 'param':
            output_bin_text.append(content[0])
        elif typ == 'label':
            label_name = content[0].lower()
            if label_name in labels_text:
                output_bin_text.append(labels_text[label_name] + content[1])
            elif label_name in labels_data:
                output_bin_text.append(labels_data[label_name] + content[1] + 8)
            else:
                raise KeyError(f'Unknown label {label_name}')
        elif typ == 'db':
            output_bin_text.append(content[0])

    output_bin_data = [0] * 8
    for typ, *content in output_data:
        if typ == 'db':
            output_bin_data.append(content[0])
        else:
            raise ValueError('Only db pseudo-instructions are allowed in the .data section.')

    # Create human readable version of the memory contents
    human_readable_text = list()
    addr_to_label = {v: k for k, v in labels_text.items()}
    bin_iter = enumerate(output_bin_text)
    for readable, n_bytes in output_text_readable:
        addr, binary = next(bin_iter)
        s = f'{addr:02x}: {binary:08b} {readable}'
        if label := addr_to_label.get(addr, ''):
            s += f' ({label})'
        human_readable_text.append(s)
        for _ in range(n_bytes - 1):
            addr, binary = next(bin_iter)
            s = f'{addr:02x}: {binary:08b}'
            if label := addr_to_label.get(addr, ''):
                s += f' ({label})'
            human_readable_text.append(s)

    human_readable_data = list()
    addr_to_label = {v + 8: k for k, v in labels_data.items()}
    bin_iter = enumerate(output_bin_data)
    for readable, n_bytes in output_data_readable:
        addr, binary = next(bin_iter)
        s = f'{addr:02x}: {binary:08b} {readable}'
        if label := addr_to_label.get(addr, ''):
            s += f' ({label})'
        human_readable_data.append(s)
        for _ in range(n_bytes - 1):
            addr, binary = next(bin_iter)
            s = f'{addr:02x}: {binary:08b}'
            if label := addr_to_label.get(addr, ''):
                s += f' ({label})'
            human_readable_data.append(s)

    output_bin = list(output_bin_text)
    while len(output_bin) < 256:
        output_bin.append(0)
    output_bin += output_bin_data

    if verbose:
        print('------TEXT------')
        for line in human_readable_text:
            print(line)
        print('\n------DATA------')
        for line in human_readable_data:
            print(line)

    return output_bin, human_readable_text


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
