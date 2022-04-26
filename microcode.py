from copy import deepcopy

HLT = 0b100000000000000000  # Halt clock
MI  = 0b010000000000000000  # Memory address register in
RI  = 0b001000000000000000  # RAM data in
II  = 0b000100000000000000  # Instruction register in
J   = 0b000010000000000000  # Jump
AI  = 0b000001000000000000  # A register in
BI  = 0b000000100000000000  # B register in
OI  = 0b000000010000000000  # Output register in
FI  = 0b000000001000000000  # Flags register in
CE  = 0b000000000100000000  # Program counter enable (inc)
SU  = 0b000000000010000000  # ALU Subtract
RO  = 0b000000000001000000  # RAM out
IO  = 0b000000000000100000  # Instruction register out
CO  = 0b000000000000010000  # Program counter out
AO  = 0b000000000000001000  # A register out
EO  = 0b000000000000000100  # ALU out
BO  = 0b000000000000000010  # B register out
TR  = 0b000000000000000001  # Time reset

FLAGS_Z0C0 = 0
FLAGS_Z0C1 = 1
FLAGS_Z1C0 = 2
FLAGS_Z1C1 = 3

JC = 0b0111
JZ = 0b1000

UCODE_TEMPLATE = [
    [MI|CO,  RO|II|CE,  TR,     0,         0,      0,            0,  0],   # 0000 - NOP
    [MI|CO,  RO|II|CE,  MI|CO,  MI|RO|CE,  RO|AI,  TR,           TR, 0],   # 0001 - LDA
    [MI|CO,  RO|II|CE,  MI|CO,  MI|RO|CE,  RO|BI,  EO|AI|FI,     TR, 0],   # 0010 - ADD
    [MI|CO,  RO|II|CE,  MI|CO,  MI|RO|CE,  RO|BI,  EO|AI|SU|FI,  TR, 0],   # 0011 - SUB
    [MI|CO,  RO|II|CE,  MI|CO,  MI|RO|CE,  AO|RI,  TR,           0,  0],   # 0100 - STA
    [MI|CO,  RO|II|CE,  MI|CO,  RO|AI|CE,  TR,     0,            0,  0],   # 0101 - LDI
    [MI|CO,  RO|II|CE,  MI|CO,  RO|J,      TR,     0,            0,  0],   # 0110 - JMP
    [MI|CO,  RO|II|CE,  CE,     TR,        TR,     0,            0,  0],   # 0111 - JC
    [MI|CO,  RO|II|CE,  CE,     TR,        TR,     0,            0,  0],   # 1000 - JZ
    [MI|CO,  RO|II|CE,  TR,     0,         0,      0,            0,  0],   # 1001
    [MI|CO,  RO|II|CE,  TR,     0,         0,      0,            0,  0],   # 1010
    [MI|CO,  RO|II|CE,  TR,     0,         0,      0,            0,  0],   # 1011
    [MI|CO,  RO|II|CE,  TR,     0,         0,      0,            0,  0],   # 1100
    [MI|CO,  RO|II|CE,  TR,     0,         0,      0,            0,  0],   # 1101
    [MI|CO,  RO|II|CE,  AO|OI,  TR,        0,      0,            0,  0],   # 1110 - OUT
    [MI|CO,  RO|II|CE,  HLT,    TR,        0,      0,            0,  0],   # 1111 - HLT
]

ucode = [deepcopy(UCODE_TEMPLATE) for _ in range(4)]
ucode[FLAGS_Z0C1][JC][2] = MI|CO
ucode[FLAGS_Z1C0][JZ][2] = MI|CO
ucode[FLAGS_Z1C1][JC][2] = MI|CO
ucode[FLAGS_Z1C1][JZ][2] = MI|CO
ucode[FLAGS_Z0C1][JC][3] = RO|J
ucode[FLAGS_Z1C0][JZ][3] = RO|J
ucode[FLAGS_Z1C1][JC][3] = RO|J
ucode[FLAGS_Z1C1][JZ][3] = RO|J

ucode = [ucode[i][j][k] for i in range(4) for j in range(16) for k in range(8)]

if __name__ == '__main__':
    for addr, contents in enumerate(ucode):
        print(f'{addr:03d}: {contents:016b}')
