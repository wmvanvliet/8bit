import serial


class Bios:
    def __init__(self, port):
        self.con = serial.Serial(port, 57600, timeout=1)

    def get_next_message(self):
        while True:
            return self.con.readline().decode('ascii').strip()

    def send(self, val):
        self.con.write(val)

    def close(self):
        self.con.close()
