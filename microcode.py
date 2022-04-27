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
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00000000 - NOP
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,  MI|CO,     RO|MI|CE,     RI|BO,     TR   ],  # 00000001 - LD_AV
    [MI|CO,  RO|II|CE,  MI|CO,     RO|MI|CE,  RO|BI,     MI|CO,        RO|MI|CE,  MI|BO],  # 00000010 - LD_AA
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,  MI|CO,     RO|MI|CE,     RO|AI,     EO|MI],  # 00000011 - ADD_AV
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,  MI|CO,     RO|MI|CE,     RO|AI|SU,  EO|MI],  # 00000100 - SUB_AV
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00000101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00000110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00000111 - NOP
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  AO|RI,     TR,           0,         0    ],  # 00001000 - LD_RA_A
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|BI,     IO|MI,        BO|RI,     TR   ],  # 00001001 -      _B
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|BI,     IO|MI,        BO|RI,     TR   ],  # 00001010 -      _C
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|BI,     IO|MI,        BO|RI,     TR   ],  # 00001011 -      _D
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|BI,     IO|MI,        BO|RI,     TR   ],  # 00001100 -      _E
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|BI,     IO|MI,        BO|RI,     TR   ],  # 00001101 -      _F
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|BI,     IO|MI,        BO|RI,     TR   ],  # 00001110 -      _G
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|BI,     IO|MI,        BO|RI,     TR   ],  # 00001111 -      _H
    [MI|CO,  RO|II|CE,  MI|CO,     AI|RO|CE,  TR,        0,            0,         0    ],  # 00010000 - LD_RV_A
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,  IO|MI,     BO|RI,        TR,        0    ],  # 00010001 -      _B
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,  IO|MI,     BO|RI,        TR,        0    ],  # 00010010 -      _C
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,  IO|MI,     BO|RI,        TR,        0    ],  # 00010011 -      _D
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,  IO|MI,     BO|RI,        TR,        0    ],  # 00010100 -      _E
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,  IO|MI,     BO|RI,        TR,        0    ],  # 00010101 -      _F
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,  IO|MI,     BO|RI,        TR,        0    ],  # 00010110 -      _G
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,  IO|MI,     BO|RI,        TR,        0    ],  # 00010111 -      _H
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  AO|RI,     TR,           0,         0    ],  # 00011000 - LD_AR_A
    [MI|CO,  RO|II|CE,  IO|MI,     RO|BI,     MI|CO,     MI|RO|CE,     BO|RI,     TR,  ],  # 00011001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     RO|BI,     MI|CO,     MI|RO|CE,     BO|RI,     TR,  ],  # 00011010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     RO|BI,     MI|CO,     MI|RO|CE,     BO|RI,     TR,  ],  # 00011011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     RO|BI,     MI|CO,     MI|RO|CE,     BO|RI,     TR,  ],  # 00011100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     RO|BI,     MI|CO,     MI|RO|CE,     BO|RI,     TR,  ],  # 00011101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     RO|BI,     MI|CO,     MI|RO|CE,     BO|RI,     TR,  ],  # 00011110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     RO|BI,     MI|CO,     MI|RO|CE,     BO|RI,     TR,  ],  # 00011111 -      _H
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00100111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00101111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00110111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 00111111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01000111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01001111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01010111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01011111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01100111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01101111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01110111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 01111111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10000111 - NOP
    [MI|CO,  RO|II|CE,  AO|OI,     TR,        0,         0,            0,         0    ],  # 10001000 - OUT_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     RO|OI,     TR,        0,            0,         0,   ],  # 10001001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     RO|OI,     TR,        0,            0,         0,   ],  # 10001010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     RO|OI,     TR,        0,            0,         0,   ],  # 10001011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     RO|OI,     TR,        0,            0,         0,   ],  # 10001100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     RO|OI,     TR,        0,            0,         0,   ],  # 10001101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     RO|OI,     TR,        0,            0,         0,   ],  # 10001110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     RO|OI,     TR,        0,            0,         0,   ],  # 10001111 -      _H
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10010111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10011111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10100111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10101111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10110111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 10111111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11000111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11001111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11010111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11011111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11100111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101110 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11101111 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11110000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11110001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11110010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11110011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11110100 - NOP
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,  RO|OI,     TR,           0,         0    ],  # 11110101 - OUT_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|OI|CE,  TR,        0,            0,         0    ],  # 11110110 - OUT_V
    [MI|CO,  RO|II|CE,  IO|J,      CE,        CE,        TR,           0,         0    ],  # 11110111 - JS
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11111000 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11111001 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11111010 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11111011 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11111100 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11111101 - NOP
    [MI|CO,  RO|II|CE,  TR,        0,         0,         0,            0,         0    ],  # 11111110 - NOP
    [MI|CO,  RO|II|CE,  HLT,       TR,        0,         0,            0,         0    ],  # 11111111 - HLT
]

ucode = [deepcopy(UCODE_TEMPLATE) for _ in range(4)]
#ucode[FLAGS_Z0C1][JC][2] = MI|CO
#ucode[FLAGS_Z1C0][JZ][2] = MI|CO
#ucode[FLAGS_Z1C1][JC][2] = MI|CO
#ucode[FLAGS_Z1C1][JZ][2] = MI|CO
#ucode[FLAGS_Z0C1][JC][3] = RO|J
#ucode[FLAGS_Z1C0][JZ][3] = RO|J
#ucode[FLAGS_Z1C1][JC][3] = RO|J
#ucode[FLAGS_Z1C1][JZ][3] = RO|J

ucode = [ucode[i][j][k] for i in range(4) for j in range(256) for k in range(8)]

if __name__ == '__main__':
    for addr, contents in enumerate(ucode):
        print(f'{addr:03d}: {contents:016b}')
