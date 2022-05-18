from simulator import Simulator
import microcode


def test_nop():
    assert Simulator('''nop
                        hlt''').run_batch() == []


def test_output():
    assert Simulator('''out 1       ; output direct value
                        ld a,2
                        out a       ; output accumulator
                        ld b,3
                        out b       ; output general purpose register
                        out [four]  ; output memory address
                        hlt
                        section .data
                        four: db 4''').run_batch() == [1, 2, 3, 4]


def test_ld():
    assert Simulator('''ld a,1       ; Load direct value in accumulator
                        out a
                        ld b,2       ; Load direct value in general purpose register
                        out b
                        ld b,3
                        ld a,b       ; Load register into accumulator
                        out a
                        ld a,4
                        ld b,a       ; Load accumulator into register
                        out b
                        ld b,5
                        ld c,b       ; Load register into register
                        out c
                        ld a,[six]   ; Load address into accumulator
                        out a
                        ld b,[seven] ; Load address into register
                        out b
                        hlt
                        section .data
                        six: db 6
                        seven: db 7''').run_batch() == [1, 2, 3, 4, 5, 6, 7]


def test_add():
    assert Simulator('''ld a,0
                        add 1        ; Add direct value
                        out a
                        ld b,1
                        add b        ; Add register
                        out a
                        add [one]    ; Add address
                        out a
                        add a        ; Add accumulator
                        out a
                        hlt
                        section .data
                        one: db 1''').run_batch() == [1, 2, 3, 6]

    # Test flags
    sim = Simulator('''ld a,1
                       add 2
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b00

    sim = Simulator('''ld a,10
                       add 255
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b01

    sim = Simulator('''ld a,0
                       add 0
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b10

    sim = Simulator('''ld a,1
                       add 255
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b11

    sim = Simulator('''ld a,1
                       ld b,2
                       add b
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b00

    sim = Simulator('''ld a,10
                       ld b,255
                       add b
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b01

    sim = Simulator('''ld a,0
                       ld b,0
                       add b
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b10

    sim = Simulator('''ld a,1
                       ld b,255
                       add b
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b11

    sim = Simulator('''ld a,1
                       add [x]
                       hlt
                       section .data
                       x: db 2''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b00

    sim = Simulator('''ld a,10
                       add [x]
                       hlt
                       section .data
                       x: db 255''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b01

    sim = Simulator('''ld a,0
                       add [x]
                       hlt
                       section .data
                       x: db 0''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b10

    sim = Simulator('''ld a,1
                       add [x]
                       hlt
                       section .data
                       x: db 255''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b11


def test_sub():
    assert Simulator('''ld a,2
                        sub 1        ; Subtract direct value
                        out a
                        ld a,3
                        ld b,1
                        sub b        ; Subtract register
                        out a
                        ld a,4
                        sub [one]    ; Subtract address
                        out a
                        sub a        ; Subtract accumulator
                        out a
                        hlt
                        section .data
                        one: db 1''').run_batch() == [1, 2, 3, 0]

    # Test flags
    sim = Simulator('''ld a,1
                       sub 2
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b00

    sim = Simulator('''ld a,2
                       sub 1
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b01

    sim = Simulator('''ld a,1
                       sub 1
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b11

    sim = Simulator('''ld a,0
                       sub 0
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b11


def test_cp():
    # Test flags
    sim = Simulator('''ld a,1
                       cp 2
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b00

    sim = Simulator('''ld a,2
                       cp 1
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b01

    sim = Simulator('''ld a,1
                       cp 1
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b11

    sim = Simulator('''ld a,0
                       cp 0
                       hlt''')
    sim.run_batch()
    assert sim.state.reg_flags == 0b11


def test_jp():
    assert Simulator('''ld a,1
                        jp x        ; Jump to value
                        ld a,2
                        x: out a
                        hlt''').run_batch() == [1]

    assert Simulator('''ld a,1
                        jp [x]      ; Jump to address
                        ld a,2
                        out a
                        hlt
                        section .data
                        x: db 6''').run_batch() == [1]

    assert Simulator('''ld a,1
                        ld b,x
                        jp b        ; Jump to register
                        ld a,2
                        x: out a
                        hlt''').run_batch() == [1]

    assert Simulator('''ld b,1
                        ld a,x
                        jp a        ; Jump to accumulator
                        ld b,2
                        x: out b
                        hlt''').run_batch() == [1]


def test_jc():
    assert Simulator('''ld a,1
                        add 255
                        jc x        ; Jump to value
                        ld a,2
                        x: out a
                        hlt''').run_batch() == [0]


def test_jz():
    assert Simulator('''ld a,10
                        sub 10
                        jz x        ; Jump to value
                        ld a,2
                        x: out a
                        hlt''').run_batch() == [0]


def test_jnc():
    assert Simulator('''ld a,10
                        add 10
                        jnc x        ; Jump to value
                        ld a,2
                        x: out a
                        hlt''').run_batch() == [20]


def test_jnz():
    assert Simulator('''ld a,10
                        sub 9 
                        jnz x        ; Jump to value
                        ld a,2
                        x: out a
                        hlt''').run_batch() == [1]


def test_adc():
    # Add address, no carry
    assert Simulator('''ld a,10
                        adc [x]
                        out a
                        hlt
                        section .data
                        x: db 10''').run_batch() == [20]

    # Add address, with carry
    assert Simulator('''ld a,200
                        add 200    ; sets carry
                        out a
                        ld a,0
                        adc [x]    ; should add 11
                        out a
                        hlt
                        section .data
                        x: db 10''').run_batch() == [144, 11]

    # Add value, no carry
    assert Simulator('''ld a,10
                        adc 10
                        out a
                        hlt''').run_batch() == [20]

    # Add value, with carry
    assert Simulator('''ld a,200
                        add 200    ; sets carry
                        out a
                        ld a,0
                        adc 10     ; should add 11
                        out a
                        hlt''').run_batch() == [144, 11]

    # Add accumulator, no carry
    assert Simulator('''ld a,10
                        adc a
                        out a
                        hlt''').run_batch() == [20]

    # Add accumulator, with carry
    assert Simulator('''ld a,200
                        add 200    ; sets carry
                        out a
                        adc a
                        out a
                        hlt''').run_batch() == [144, 89]

    # Add register, no carry
    assert Simulator('''ld a,10
                        ld b,10
                        adc b
                        out a
                        hlt''').run_batch() == [20]

    # Add register, with carry
    assert Simulator('''ld a,200
                        add 200    ; sets carry
                        out a
                        ld a,0
                        ld b,10
                        adc b
                        out a
                        hlt''').run_batch() == [144, 11]


def test_sbc():
    # Subtract address, no carry
    assert Simulator('''ld a,20
                        sbc [x]
                        out a
                        hlt
                        section .data
                        x: db 10''').run_batch() == [10]

    # Subtract address, with carry
    assert Simulator('''ld a,200
                        sub 400    ; sets carry
                        out a
                        ld a,20
                        sbc [x]    ; should subtract 11
                        out a
                        hlt
                        section .data
                        x: db 10''').run_batch() == [56, 9]

    # Subtract value, no carry
    assert Simulator('''ld a,20
                        sbc 10
                        out a
                        hlt''').run_batch() == [10]

    # Subtract value, with carry
    assert Simulator('''ld a,200
                        sub 400    ; sets carry
                        out a
                        ld a,20
                        sbc 10     ; should subtract 11
                        out a
                        hlt''').run_batch() == [56, 9]

    # Subtract accumulator, no carry
    assert Simulator('''ld a,10
                        sbc a
                        out a
                        hlt''').run_batch() == [0]

    # Subtract accumulator, with carry
    assert Simulator('''ld a,200
                        sub 400    ; sets carry
                        out a
                        sbc a
                        out a
                        hlt''').run_batch() == [56, 255]

    # Subtract register, no carry
    assert Simulator('''ld a,20
                        ld b,10
                        sbc b
                        out a
                        hlt''').run_batch() == [10]

    # Subtract register, with carry
    assert Simulator('''ld a,200
                        sub 400    ; sets carry
                        out a
                        ld a,20
                        ld b,10
                        sbc b
                        out a
                        hlt''').run_batch() == [56, 9]


def test_inc():
    assert Simulator('''ld a,4
                        inc
                        out a
                        hlt''').run_batch() == [5]


def test_dec():
    assert Simulator('''ld a,4
                        dec
                        out a
                        hlt''').run_batch() == [3]


def test_djnz():
    assert Simulator('''      ld a,4
                        loop: out a
                              djnz loop
                              hlt''').run_batch() == [4, 3, 2, 1]


def test_program_test():
    with open('example_programs/test.asm') as f:
        assert Simulator(f.read()).run_batch() == [42]


def test_program_multiply():
    with open('example_programs/multiply.asm') as f:
        assert Simulator(f.read()).run_batch() == [35]


def test_program_multiply_shift():
    with open('example_programs/multiply_shift.asm') as f:
        assert Simulator(f.read()).run_batch() == [255]


def test_program_divide():
    with open('example_programs/divide.asm') as f:
        assert Simulator(f.read()).run_batch() == [7]


def test_program_fibonacci():
    with open('example_programs/fibonacci.asm') as f:
        assert Simulator(f.read()).run_batch() == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]


def test_program_shift():
    with open('example_programs/shift.asm') as f:
        assert Simulator(f.read()).run_batch() == [1, 2, 4, 8, 16, 32, 0]


def test_program_sqrt():
    with open('example_programs/sqrt.asm') as f:
        assert Simulator(f.read()).run_batch() == [4, 8, 7, 7]
