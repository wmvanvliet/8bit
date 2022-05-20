from copy import deepcopy
from argparse import ArgumentParser
import struct

HLT = 0b1000000000000000  # Halt clock
MI  = 0b0100000000000000  # Memory address register in
RI  = 0b0010000000000000  # RAM data in
RO  = 0b0001000000000000  # RAM data out
IO  = 0b0000100000000000  # Instruction register out
II  = 0b0000010000000000  # Instruction register in
AI  = 0b0000001000000000  # A register in
AO  = 0b0000000100000000  # A register out
EO  = 0b0000000010000000  # ALU out
SU  = 0b0000000001000000  # ALU subtract
BI  = 0b0000000000100000  # B register in
OI  = 0b0000000000010000  # Output register in
CE  = 0b0000000000001000  # Program counter enable
CO  = 0b0000000000000100  # Program counter out
J   = 0b0000000000000010  # Jump (program counter in)
FI  = 0b0000000000000001  # Flags in

FLAGS_Z0C0 = 0
FLAGS_Z0C1 = 1
FLAGS_Z1C0 = 2
FLAGS_Z1C1 = 3

JC = 0b0111
JZ = 0b1000

UCODE_TEMPLATE = [
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 0000 - NOP
    [MI|CO,  RO|II|CE,  IO|MI,  RO|AI,  0,           0, 0, 0],   # 0001 - LDA
    [MI|CO,  RO|II|CE,  IO|MI,  RO|BI,  EO|AI|FI,    0, 0, 0],   # 0010 - ADD
    [MI|CO,  RO|II|CE,  IO|MI,  RO|BI,  EO|AI|SU|FI, 0, 0, 0],   # 0011 - SUB
    [MI|CO,  RO|II|CE,  IO|MI,  AO|RI,  0,           0, 0, 0],   # 0100 - STA
    [MI|CO,  RO|II|CE,  IO|AI,  0,      0,           0, 0, 0],   # 0101 - LDI
    [MI|CO,  RO|II|CE,  IO|J,   0,      0,           0, 0, 0],   # 0110 - JMP
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 0111 - JC
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 1000 - JZ
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 1001
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 1010
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 1011
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 1100
    [MI|CO,  RO|II|CE,  0,      0,      0,           0, 0, 0],   # 1101
    [MI|CO,  RO|II|CE,  AO|OI,  0,      0,           0, 0, 0],   # 1110 - OUT
    [MI|CO,  RO|II|CE,  HLT,    0,      0,           0, 0, 0],   # 1111 - HLT
]

ucode = [deepcopy(UCODE_TEMPLATE) for _ in range(4)]
ucode[FLAGS_Z0C1][JC][2] = IO|J
ucode[FLAGS_Z1C0][JZ][2] = IO|J
ucode[FLAGS_Z1C1][JC][2] = IO|J
ucode[FLAGS_Z1C1][JZ][2] = IO|J

ucode = [ucode[i][j][k] for i in range(4) for j in range(16) for k in range(8)]

if __name__ == '__main__':
    parser = ArgumentParser(description='Build the microcode ROM contents for the 8bit breadboard computer.')
    parser.add_argument('output_file', type=str, help='File to write the microcode binary to')
    parser.add_argument('-t', '--top', action='store_true', help='Write only the top 8 bytes')
    parser.add_argument('-b', '--bottom', action='store_true', help='Write only the bottom 8 bytes')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display the produced microcode binary')
    args = parser.parse_args()

    with open(args.output_file, 'wb') as f:
        bin_contents = bytes()
        for contents in ucode:
            if args.top:
                bin_contents += struct.pack('<B', contents >> 8)
            elif args.bottom:
                bin_contents += struct.pack('<B', contents & 0xff)
            else:
                bin_contents += struct.pack('<H', contents)
        f.write(bin_contents)

        if args.verbose:
            if args.top or args.bottom:
                for addr in range(0, len(bin_contents), 8):
                    print(f'{addr:04x}: {bin_contents[addr]:02x} {bin_contents[addr + 1]:02x} {bin_contents[addr + 2]:02x} {bin_contents[addr + 3]:02x} {bin_contents[addr + 4]:02x} {bin_contents[addr + 5]:02x} {bin_contents[addr + 6]:02x} {bin_contents[addr + 7]:02x}')
            else:
                for addr in range(0, len(bin_contents), 16):
                    print(f'{addr:04x}: {bin_contents[addr + 1]:02x}{bin_contents[addr]:02x} {bin_contents[addr + 3]:02x}{bin_contents[addr + 2]:02x} {bin_contents[addr + 5]:02x}{bin_contents[addr + 4]:02x} {bin_contents[addr + 7]:02x}{bin_contents[addr + 6]:02x} {bin_contents[addr + 9]:02x}{bin_contents[addr + 8]:02x} {bin_contents[addr + 11]:02x}{bin_contents[addr + 10]:02x} {bin_contents[addr + 13]:02x}{bin_contents[addr + 12]:02x} {bin_contents[addr + 15]:02x}{bin_contents[addr + 14]:02x}')

