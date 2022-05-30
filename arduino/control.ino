/**
 * Arduino Nano bootloader for the breadboard computer.
 * Upon power-on, the arduino takes control by setting the chip-enable lines of
 * the EEPROMs high. It then proceeds fill up the RAM with a given program.
 */

// The program to write to memory
/*
byte program[] = {
  0b01010001,  // 0000  ldi 1 (start)
  0b01001110,  // 0001  sta x
  0b01010000,  // 0010  ldi 0
  0b01001111,  // 0011  sta y (loop)
  0b11100000,  // 0100  out
  0b00011110,  // 0101  lda x
  0b00101111,  // 0110  add y
  0b01001110,  // 0111  sta x
  0b11100000,  // 1000  out
  0b00011111,  // 1001  lda y
  0b00101110,  // 1010  add x
  0b01110000,  // 1011  jc start
  0b01100011,  // 1100  jmp loop
  0b11110000,  // 1101  hlt (end)
  0b00000000,  // 1110  db 0 (x)
  0b00000000   // 1111  db 0 (y)
};
*/

byte program[] = {
  0b01010000,  // ldi 0
  0b00100100,  // add x (loop)
  0b11100000,  // out
  0b01100001,  // jmp loop
  0b00000100   // db 4 (x)
};

// BUS
#define D0 2
#define D1 3
#define D2 4
#define D3 5
#define D4 6
#define D5 7
#define D6 8
#define D7 9

// Control lines
#define MI 10      // Active high
#define RI 11      // Active high
#define RO 12      // Active high
#define RST A1     // Active high
#define SR A2      // Active low
#define CE A5      // Active low

// Clock input. Connected to the inverse clock signal, because it was closer on
// the breadboard.
#define CLK_INV A0 // Inverse clock signal

// Clock flanks
#define UP 0       // LOW -> HIGH
#define DOWN 1     // HIGH -> LOW

/**
 * Entry-point that is run upon power-on.
 */
void setup() {
  Serial.begin(57600);
  pinMode(LED_BUILTIN, OUTPUT);
    
  takeControl();
  writeProgramToRam(program, sizeof(program) / sizeof(byte));
  releaseControl();
}

/**
 * After setup() completes, this function is called in an infinite loop.
 */
void loop() {
  // Do nothing
}

/**
 * Take control of the system by bringing the EEPROM chip-enable line high,
 * connecting to the bus, and connecting some control lines.
 */
void takeControl() {
  // Disable the EEPROMs and the microstep counter
  pinMode(CE, OUTPUT);
  digitalWrite(CE, HIGH);
  pinMode(SR, OUTPUT);
  digitalWrite(SR, LOW);

  // Connect to the bus
  for(int i=D0; i<=D7; i++) {
    digitalWrite(i, LOW);
    pinMode(i, OUTPUT);
  }

  // Connect control lines.
  pinMode(MI, OUTPUT);
  pinMode(RI, OUTPUT);
  pinMode(RO, OUTPUT);
  digitalWrite(MI, LOW);
  digitalWrite(RI, LOW);
  digitalWrite(RO, LOW);

  // Keep the master reset line disconnected
  digitalWrite(RST, LOW);
  pinMode(RST, INPUT);

  // Start listening to the clock
  pinMode(CLK_INV, INPUT);
}

/**
 * Release control of the system by disconnecting from the bus, hitting the
 * master reset and then bringing the EEPROM chip-enable line low.
 */
void releaseControl() {
  // Disconnect from the bus
  for(int i=D0; i<=D7; i++) {
    digitalWrite(i, LOW);
    pinMode(i, INPUT);
  }

  // Disconnect control lines
  digitalWrite(MI, LOW);
  digitalWrite(RI, LOW);
  digitalWrite(RO, LOW);
  pinMode(MI, INPUT);
  pinMode(RI, INPUT);

  // Hit the master reset
  pinMode(RST, OUTPUT);
  digitalWrite(RST, HIGH);
  delay(5);
  digitalWrite(RST, LOW);
  pinMode(RST, INPUT);

  waitOnClock(LOW);

  // Activate microstep counter and hand over control to the EEPROMs
  digitalWrite(SR, HIGH);
  digitalWrite(CE, LOW);
}

/**
 * Write the program into RAM memory.
 */
void writeProgramToRam(byte program[], int programLength) {
  // Start with everything disabled. We need to wait on the clock to start
  // doing things.
  digitalWrite(MI, LOW);
  digitalWrite(RI, LOW);

  // Only start writing when clock is low
  waitOnClock(LOW);

  // Start writing to the bus and setting control lines to move data into the
  // memory address and RAM. We set the control lines and bus when the clock is
  // low. When the clock transitions to high, the registers will read from the
  // bus.
  Serial.println(programLength);
  for(byte address=0; address<programLength; address++) {
    // Write address
    writeToBus(address);
    digitalWrite(MI, HIGH);
    digitalWrite(RI, LOW);
    waitOnClockFlank(DOWN); // Keep values until next clock pulse

    // Write to RAM
    writeToBus(program[address]);
    digitalWrite(MI, LOW);
    digitalWrite(RI, HIGH);
    waitOnClockFlank(DOWN); // Keep values until next clock pulse
  }

  // Stop doing things
  digitalWrite(MI, LOW);
  digitalWrite(RI, LOW);
}

/**
 * Wait until the clock is low.
 *   state: Desired state of the clock, either HIGH or LOW
 */
void waitOnClock(int state) {
  // We are reading the *inverse* of the clock,
  // hence == and not != as you would expect.
  while(digitalRead(CLK_INV) == state) {}
}

/**
 * Wait until the clock transitions state.
 *   flank: Whether to wait for the UP flank or DOWN flank.
 */
void waitOnClockFlank(int flank) {
  if(flank == UP) {
    waitOnClock(LOW);
    waitOnClock(HIGH);
  } else {
    waitOnClock(HIGH);
    waitOnClock(LOW);
  }
}

/**
 * Put an 8-bit value onto the bus.
 */
void writeToBus(int val) {
  Serial.println(val);
  for(int i=0; i<8; i++) {
    // Write the i'th bit of val to the correct line of the bus
    digitalWrite(D0 + i, (val >> i) & 1);
  }
}
