#define SHIFT_DATA 2
#define SHIFT_CLOCK 3
#define SHIFT_LATCH 4

void setup() {
  pinMode(SHIFT_DATA, OUTPUT);
  pinMode(SHIFT_CLOCK, OUTPUT);
  pinMode(SHIFT_LATCH, OUTPUT);

  for(int i=0; i<65536; i++) {
    shiftOut(SHIFT_DATA, SHIFT_CLOCK, LSBFIRST, i & 255);
    shiftOut(SHIFT_DATA, SHIFT_CLOCK, LSBFIRST, i >> 8);
    digitalWrite(SHIFT_LATCH, LOW);
    digitalWrite(SHIFT_LATCH, HIGH);
    digitalWrite(SHIFT_LATCH, LOW);
    delay(10);
  }
}

void loop() {
}
