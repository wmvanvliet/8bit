import serial
import sys

with open(sys.argv[1], 'rb') as f:
    contents = f.read()
print(f'Sending {sys.argv[1]} of length {len(contents)}')

with serial.Serial('COM5', 115200, write_timeout=2, timeout=2) as con:
    while True:
        msg = con.readline().decode('ascii').strip()
        print('< ' + msg, flush=True)
        if msg == 'WELCOME':
            break

    for i, val in enumerate(contents):
        con.write(bytes([val]))
        print(f'{i}> {val} ({chr(val) if val != 10 else "newline"})', flush=True)
        while True:
            resp = con.readline().decode('ascii').strip()
            if len(resp) > 0:
                print(f'< {resp}', flush=True)
                break
