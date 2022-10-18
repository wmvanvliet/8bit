"""
Construct the microcode of the machine.
"""
from argparse import ArgumentParser
from copy import deepcopy
import struct

from assembler import opcodes

# Control lines
HLT = 0b1000000000000000  # Halt clock
MI  = 0b0100000000000000  # Memory address register in
RI  = 0b0010000000000000  # RAM data in
II  = 0b0001000000000000  # Instruction register in
J   = 0b0000100000000000  # Jump
AI  = 0b0000010000000000  # A register in
BI  = 0b0000001000000000  # B register in
FI  = 0b0000000100000000  # Flags register in
OI  = 0b0000000010000000  # Output register in
EI  = 0b0000000001000000  # ALU invert B
CE  = 0b0000000000100000  # Program counter enable (inc)
SS  = 0b0000000000010000  # Memory segment select
EC  = 0b0000000000001000  # ALU carry in
RO  = 0b0000000000000001  # RAM out
IO  = 0b0000000000000010  # Instruction register out
CO  = 0b0000000000000011  # Program counter out
AO  = 0b0000000000000100  # A register out
BO  = 0b0000000000000101  # B register out
EO  = 0b0000000000000110  # ALU out
SR  = 0b0000000000000111  # Microstep reset

# Flags
FLAGS_Z0C0 = 0
FLAGS_Z0C1 = 1
FLAGS_Z1C0 = 2
FLAGS_Z1C1 = 3

UCODE_TEMPLATE = [
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 00000111 - NOP
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|AI,       SR,             0,         0       ],  # 00001000 - LD_RA_A
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       IO|MI,          BO|SS|RI,  SR      ],  # 00001001 -      _B
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       IO|MI,          BO|SS|RI,  SR      ],  # 00001010 -      _C
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       IO|MI,          BO|SS|RI,  SR      ],  # 00001011 -      _D
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       IO|MI,          BO|SS|RI,  SR      ],  # 00001100 -      _E
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       IO|MI,          BO|SS|RI,  SR      ],  # 00001101 -      _F
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       IO|MI,          BO|SS|RI,  SR      ],  # 00001110 -      _G
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       IO|MI,          BO|SS|RI,  SR      ],  # 00001111 -      _H
    [MI|CO,  RO|II|CE,  MI|CO,     AI|RO|CE,       SR,             0,              0,         0       ],  # 00010000 - LD_RV_A
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       IO|MI,          BO|SS|RI,       SR,        0       ],  # 00010001 -      _B
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       IO|MI,          BO|SS|RI,       SR,        0       ],  # 00010010 -      _C
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       IO|MI,          BO|SS|RI,       SR,        0       ],  # 00010011 -      _D
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       IO|MI,          BO|SS|RI,       SR,        0       ],  # 00010100 -      _E
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       IO|MI,          BO|SS|RI,       SR,        0       ],  # 00010101 -      _F
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       IO|MI,          BO|SS|RI,       SR,        0       ],  # 00010110 -      _G
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       IO|MI,          BO|SS|RI,       SR,        0       ],  # 00010111 -      _H
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       AO|SS|RI,       SR,             0,         0       ],  # 00011000 - LD_AR_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       MI|CO,          MI|RO|CE,       BO|RI|SS,  SR,     ],  # 00011001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       MI|CO,          MI|RO|CE,       BO|RI|SS,  SR,     ],  # 00011010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       MI|CO,          MI|RO|CE,       BO|RI|SS,  SR,     ],  # 00011011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       MI|CO,          MI|RO|CE,       BO|RI|SS,  SR,     ],  # 00011100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       MI|CO,          MI|RO|CE,       BO|RI|SS,  SR,     ],  # 00011101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       MI|CO,          MI|RO|CE,       BO|RI|SS,  SR,     ],  # 00011110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       MI|CO,          MI|RO|CE,       BO|RI|SS,  SR,     ],  # 00011111 -      _H
    [MI|CO,  RO|II|CE,  AO|BI,     EO|AI|FI,       SR,             0,              0,         0       ],  # 00100000 - ADD_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 00100001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 00100001 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 00100001 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 00100001 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 00100001 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 00100001 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 00100001 -      _H
    [MI|CO,  RO|II|CE,  AO|BI,     EO|AI|EI|EC|FI, SR,             0,              0,         0       ],  # 00101000 - SUB_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 00101001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 00101010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 00101011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 00101100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 00101101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 00101110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 00101111 -      _H
    [MI|CO,  RO|II|CE,  AO|BI,     EI|EC|FI,       SR,             0,              0,         0       ],  # 00110000 - CP_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EI|EC|FI,       SR,             0,         0,      ],  # 00110001 -     _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EI|EC|FI,       SR,             0,         0,      ],  # 00110010 -     _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EI|EC|FI,       SR,             0,         0,      ],  # 00110011 -     _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EI|EC|FI,       SR,             0,         0,      ],  # 00110100 -     _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EI|EC|FI,       SR,             0,         0,      ],  # 00110101 -     _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EI|EC|FI,       SR,             0,         0,      ],  # 00110110 -     _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EI|EC|FI,       SR,             0,         0,      ],  # 00110111 -     _H
    [MI|CO,  RO|II|CE,  AO|J,      SR,             0,              0,              0,         0       ],  # 00111000 - JP_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 00111001 -     _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 00111010 -     _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 00111011 -     _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 00111100 -     _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 00111101 -     _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 00111110 -     _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 00111111 -     _H
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000000 - JP_C_R_A
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000001 -       _B
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000010 -       _C
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000011 -       _D
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000100 -       _E
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000101 -       _F
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000110 -       _G
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01000111 -       _H
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001000 - JP_Z_R_A
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001001 -       _B
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001010 -       _C
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001011 -       _D
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001100 -       _E
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001101 -       _F
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001110 -       _G
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0       ],  # 01001111 -       _H
    [MI|CO,  RO|II|CE,  AO|J,      SR,             0,              0,              0,         0       ],  # 01010000 - JP_NC_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01010001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01010010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01010011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01010100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01010101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01010110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01010111 -      _H
    [MI|CO,  RO|II|CE,  AO|J,      SR,             0,              0,              0,         0       ],  # 01011000 - JP_NZ_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01011001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01011010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01011011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01011100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01011101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01011110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|J,        SR,             0,              0,         0       ],  # 01011111 -      _H
    [MI|CO,  RO|II|CE,  AO|OI,     SR,             0,              0,              0,         0       ],  # 01100000 - OUT_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|OI,       SR,             0,              0,         0,      ],  # 01100001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|OI,       SR,             0,              0,         0,      ],  # 01100010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|OI,       SR,             0,              0,         0,      ],  # 01100011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|OI,       SR,             0,              0,         0,      ],  # 01100100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|OI,       SR,             0,              0,         0,      ],  # 01100101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|OI,       SR,             0,              0,         0,      ],  # 01100110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|OI,       SR,             0,              0,         0,      ],  # 01100111 -      _H
    [MI|CO,  RO|II|CE,  AO|BI,     EO|AI|FI,       SR,             0,              0,         0       ],  # 01101000 - ADC_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 01101001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 01101010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 01101011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 01101100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 01101101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 01101110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|FI,       SR,             0,         0,      ],  # 01101111 -      _H
    [MI|CO,  RO|II|CE,  AO|BI,     EO|AI|EI|EC|FI, SR,             0,              0,         0       ],  # 01110000 - SBC_R_A
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 01110001 -      _B
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 01110010 -      _C
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 01110011 -      _D
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 01110100 -      _E
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 01110101 -      _F
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 01110110 -      _G
    [MI|CO,  RO|II|CE,  IO|MI,     SS|RO|BI,       EO|AI|EI|EC|FI, SR,             0,         0,      ],  # 01110111 -      _H
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 01111111 - NOP
    [MI|CO,  RO|II|CE,  MI|CO,     BI|RO|CE,       MI|CO,          MI|RO|CE,       SS|BO|RI,  SR      ],  # 10000000 - LD_AV
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       MI|CO,          MI|RO|CE,  SS|BO|RI],  # 10000001 - LD_AA
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       EO|AI|FI,       SR,        0       ],  # 10000010 - ADD_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,       EO|AI|FI,       SR,             0,         0       ],  # 10000011 - ADD_V
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       EO|AI|EI|EC|FI, SR,        0       ],  # 10000100 - SUB_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,       EO|AI|EI|EC|FI, SR,             0,         0       ],  # 10000101 - SUB_V
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       EI|EC|FI,       SR,        0       ],  # 10000110 - CP_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,       EI|EC|FI,       SR,             0,         0       ],  # 10000111 - CP_V
    [MI|CO,  RO|II|CE,  MI|CO,     RO|MI,          SS|RO|J,        SR,             0,         0       ],  # 10001000 - JP_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|J,           SR,             0,              0,         0,      ],  # 10001001 - JP_V
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0,      ],  # 10001010 - JP_C_A
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0,      ],  # 10001011 - JP_C_V
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0,      ],  # 10001100 - JP_Z_A
    [MI|CO,  RO|II|CE,  CE,        SR,             0,              0,              0,         0,      ],  # 10001101 - JP_Z_V
    [MI|CO,  RO|II|CE,  MI|CO,     RO|MI,          RO|J,           SR,             SR,        0       ],  # 10011110 - JP_NC_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|J,           SR,             SR,             0,         0,      ],  # 10011111 - JP_NC_V
    [MI|CO,  RO|II|CE,  MI|CO,     RO|MI,          RO|J,           SR,             SR,        0       ],  # 10010000 - JP_NZ_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|J,           SR,             SR,             0,         0,      ],  # 10010001 - JP_NZ_V
    [MI|CO,  RO|II|CE,  MI|CO,     RO|MI|CE,       SS|RO|OI,       SR,             0,         0       ],  # 10010010 - OUT_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|OI|CE,       SR,             0,              0,         0       ],  # 10010011 - OUT_V
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,       MI,             SS|CO|RI,       BO|J,      SR      ],  # 10010100 - JSR_V
    [MI|CO,  RO|II|CE,  MI,        SS|RO|J,        SR,             0,              0,         0       ],  # 10010101 - RET
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       EO|AI|FI,       SR,        0       ],  # 10010110 - ADC_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,       EO|AI|FI,       SR,             0,         0       ],  # 10010111 - ADC_V
    [MI|CO,  RO|II|CE,  MI|CO,     MI|RO|CE,       SS|RO|BI,       EO|AI|EI|EC|FI, SR,        0       ],  # 10011000 - SBC_A
    [MI|CO,  RO|II|CE,  MI|CO,     RO|BI|CE,       EO|AI|EI|EC|FI, SR,             0,         0       ],  # 10011001 - SBC_V
    [MI|CO,  RO|II|CE,  BI,        EO|AI|EC|FI,    SR,             0,              0,         0       ],  # 10011010 - INC
    [MI|CO,  RO|II|CE,  BI,        EO|AI|EI|FI,    SR,             0,              0,         0       ],  # 10011011 - DEC
    [MI|CO,  RO|II|CE,  BI,        EO|AI|EI|FI,    MI|CO,          RO|J,           SR,        0       ],  # 10011100 - DJZ_V
    [MI|CO,  RO|II|CE,  AI,        SR,             0,              0,              0,         0       ],  # 10011101 - INP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10011110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10011111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10100111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10101111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10110111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 10111111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11000111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11001111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11010111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11011111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11100111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11101111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110110 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11110111 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11111000 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11111001 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11111010 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11111011 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11111100 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11111101 - NOP
    [MI|CO,  RO|II|CE,  SR,        0,              0,              0,              0,         0       ],  # 11111110 - NOP
    [MI|CO,  RO|II|CE,  HLT,       SR,             0,              0,              0,         0       ],  # 11111111 - HLT
]

ucode = [deepcopy(UCODE_TEMPLATE) for _ in range(4)]

for i, c in enumerate([AO|J, SR]):  # JP_X_R_A
    ucode[FLAGS_Z0C1][opcodes['jc']['R']][2 + i] = c
    ucode[FLAGS_Z1C0][opcodes['jz']['R']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jc']['R']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jz']['R']][2 + i] = c
for i, c in enumerate([IO|MI, SS|RO|J, SR]):  # JP_X_R_X
    for j in range(1, 8):
        ucode[FLAGS_Z0C1][opcodes['jc']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C0][opcodes['jz']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C1][opcodes['jc']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C1][opcodes['jz']['R'] + j][2 + i] = c
for i, c in enumerate([MI|CO, RO|MI, SS|RO|J, SR]):  # JP_X_A
    ucode[FLAGS_Z0C1][opcodes['jc']['A']][2 + i] = c
    ucode[FLAGS_Z1C0][opcodes['jz']['A']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jc']['A']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jz']['A']][2 + i] = c
for i, c in enumerate([MI|CO, RO|J, SR]):  # JP_X_V
    ucode[FLAGS_Z0C1][opcodes['jc']['V']][2 + i] = c
    ucode[FLAGS_Z1C0][opcodes['jz']['V']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jc']['V']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jz']['V']][2 + i] = c
for i, c in enumerate([CE, SR, 0, 0, 0, 0]):  # No jump
    for j in range(8):
        ucode[FLAGS_Z0C1][opcodes['jnc']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C0][opcodes['jnz']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C1][opcodes['jnc']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C1][opcodes['jnz']['R'] + j][2 + i] = c
    ucode[FLAGS_Z0C1][opcodes['jnc']['A']][2 + i] = c
    ucode[FLAGS_Z1C0][opcodes['jnz']['A']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jnc']['A']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jnz']['A']][2 + i] = c
    ucode[FLAGS_Z0C1][opcodes['jnc']['V']][2 + i] = c
    ucode[FLAGS_Z1C0][opcodes['jnz']['V']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jnc']['V']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['jnz']['V']][2 + i] = c
for i, c in enumerate([EO|AI|EC|FI, SR]):  # ADC_R_A
    ucode[FLAGS_Z0C1][opcodes['adc']['R']][3 + i] = c
    ucode[FLAGS_Z1C1][opcodes['adc']['R']][3 + i] = c
for i, c in enumerate([IO|MI, SS|RO|BI, EO|AI|EC|FI, SR]):  # ADC_R_X
    for j in range(1, 8):
        ucode[FLAGS_Z0C1][opcodes['adc']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C1][opcodes['adc']['R'] + j][2 + i] = c
for i, c in enumerate([MI|CO, MI|RO|CE, SS|RO|BI, EO|AI|EC|FI, SR]):  # ADC_A
    ucode[FLAGS_Z0C1][opcodes['adc']['A']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['adc']['A']][2 + i] = c
for i, c in enumerate([MI|CO, RO|BI|CE, EO|AI|EC|FI, SR]):  # ADC_V
    ucode[FLAGS_Z0C1][opcodes['adc']['V']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['adc']['V']][2 + i] = c
for i, c in enumerate([EO|AI|EI|FI, SR]):  # SBC_R_A
    ucode[FLAGS_Z0C1][opcodes['sbc']['R']][3 + i] = c
    ucode[FLAGS_Z1C1][opcodes['sbc']['R']][3 + i] = c
for i, c in enumerate([IO|MI, SS|RO|BI, EO|AI|EI|FI, SR]):  # SBC_R_X
    for j in range(1, 8):
        ucode[FLAGS_Z0C1][opcodes['sbc']['R'] + j][2 + i] = c
        ucode[FLAGS_Z1C1][opcodes['sbc']['R'] + j][2 + i] = c
for i, c in enumerate([MI|CO, MI|RO|CE, SS|RO|BI, EO|AI|EI|FI, SR]):  # SBC_A
    ucode[FLAGS_Z0C1][opcodes['sbc']['A']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['sbc']['A']][2 + i] = c
for i, c in enumerate([MI|CO, RO|BI|CE, EO|AI|EI|FI, SR]):  # SBC_V
    ucode[FLAGS_Z0C1][opcodes['sbc']['V']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['sbc']['V']][2 + i] = c
for i, c in enumerate([BI, EO|AI|EI|FI, MI|CO, RO|J, SR]):  # DJZ_V
    ucode[FLAGS_Z0C1][opcodes['djnz']['V']][2 + i] = c
for i, c in enumerate([BI, EO|AI|EI|FI, CE, SR]):  # No jump
    ucode[FLAGS_Z1C0][opcodes['djnz']['V']][2 + i] = c
    ucode[FLAGS_Z1C1][opcodes['djnz']['V']][2 + i] = c

ucode = [ucode[i][j][k] for i in range(4) for j in range(256) for k in range(8)]

EEPROM_MSB = bytes([c >> 8 for c in ucode])
EEPROM_LSB = bytes([c & 0xff for c in ucode])

EEPROM = bytes()
for c in ucode:
    EEPROM += struct.pack('>H', c)

if __name__ == '__main__':
    parser = ArgumentParser(description='Build the microcode ROM contents for the 8bit breadboard computer.')
    parser.add_argument('output_file', type=str, help='File to write the microcode binary to')
    parser.add_argument('-u', '--upper', action='store_true', help='Write the most-significant 8 bits')
    parser.add_argument('-l', '--lower', action='store_true', help='Write the least-significant 8 bits')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display the produced microcode binary')
    args = parser.parse_args()

    with open(args.output_file, 'wb') as f:
        if args.upper:
            f.write(EEPROM_MSB)
        elif args.lower:
            f.write(EEPROM_LSB)
        else:
            f.write(EEPROM)

    if args.verbose:
        if args.upper:
            for addr in range(0, len(EEPROM_MSB), 8):
                print(f'{addr:04x}: {EEPROM_MSB[addr]:02x} {EEPROM_MSB[addr + 1]:02x} {EEPROM_MSB[addr + 2]:02x} {EEPROM_MSB[addr + 3]:02x} {EEPROM_MSB[addr + 4]:02x} {EEPROM_MSB[addr + 5]:02x} {EEPROM_MSB[addr + 6]:02x} {EEPROM_MSB[addr + 7]:02x}')
        elif args.lower:
            for addr in range(0, len(EEPROM_LSB), 8):
                print(f'{addr:04x}: {EEPROM_LSB[addr]:02x} {EEPROM_LSB[addr + 1]:02x} {EEPROM_LSB[addr + 2]:02x} {EEPROM_LSB[addr + 3]:02x} {EEPROM_LSB[addr + 4]:02x} {EEPROM_LSB[addr + 5]:02x} {EEPROM_LSB[addr + 6]:02x} {EEPROM_LSB[addr + 7]:02x}')
        else:
            for addr in range(0, len(EEPROM), 2):
                if addr % 16 == 0:
                    print(f'\n{addr:04x}:', end='')
                print(f' {EEPROM[addr]:02x}{EEPROM[addr + 1]:02x}', end='')
            print(end='\n')
