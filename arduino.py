import microcode


class Arduino():
    def __init__(self, mem=b''):
        self.mem = iter(mem)
        self.step = 0
        self.prev_clock = False
        self.SR = False
        self.write_to_bus = False
        self.value_to_write = 0

    def read(self, state):
        if state.clock == self.prev_clock:
            return

        SR = state.is_line_active(microcode.SR)
        if not state.clock:
            if self.SR:
                self.step = 0
                self.SR = False
            else:
                self.step += 1
                if SR:
                    self.SR = True

            if self.write_to_bus and (self.step > 2 or self.step == 0):
                self.write_to_bus = False
        else:
            if self.step == 1 and state.bus == 157:
                self.write_to_bus = True
                try:
                    self.value_to_write = next(self.mem)
                except StopIteration:
                    self.value_to_write = 0

        # print(f'{self.step=} {state.bus=} {SR=} {self.SR=} {state.clock=}')
        self.prev_clock = state.clock

    def write(self, state):
        if self.write_to_bus:
            state.bus = self.value_to_write
