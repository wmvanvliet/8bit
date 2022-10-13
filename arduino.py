import microcode


class Arduino():
    def __init__(self, mem):
        self.mem = mem
        self.step = 0
        self.prev_clock = False
        self.SR = False
        self.write_to_bus = False

    def update(self, state):
        if state.clock == self.prev_clock:
            return

        SR = state.is_line_active(microcode.SR)
        if not state.clock:
            if self.SR:
                self.step = 0
                self.SR = False
            elif SR:
                self.SR = True
            else:
                self.step += 1
        else:
            if self.step == 1 and state.bus == 157:
                print('Input instruction encountered!')
                self.write_to_bus = True
            elif self.write_to_bus:
                state.bus = 42
                self.write_to_bus = False

        print(f'{self.step=} {state.bus=} {SR=} {self.SR=} {state.clock=}')
        self.prev_clock = state.clock
