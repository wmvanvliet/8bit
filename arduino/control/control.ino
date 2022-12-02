/**
 * Arduino Nano bootloader for the breadboard computer.
 * Upon power-on, the arduino takes control by setting the chip-enable lines of
 * the EEPROMs high. It then proceeds fill up the RAM with a given program.
 */

// The program to write to memory
byte program[] = {
  0b00010001, // ld b,0
  0b00000000, //
  0b00010010, // ld c,0
  0b00000000, //
  0b00000000, // nop (begin)
  0b00000000, // nop
  0b00000000, // nop
  0b10011101, // inp
  0b10000111, // cp 10
  0b00001010, //
  0b10001101, // jz begin
  0b00000100, //
  0b10000111, // cp 65
  0b01000001, //
  0b10001101, // jz opp_rock
  0b00011010, //
  0b10000111, // cp 66
  0b01000010, //
  0b10001101, // jz opp_paper
  0b00101100, //
  0b10000111, // cp 67
  0b01000011, //
  0b10001101, // jz opp_scissor
  0b00111110, //
  0b10001001, // jp end
  0b01101101, //
  0b10011101, // inp (opp_rock)
  0b00000000, // nop
  0b00000000, // nop
  0b10011101, // inp
  0b10000111, // cp 88
  0b01011000, //
  0b10001101, // jz tie
  0b01010000, //
  0b10000111, // cp 89
  0b01011001, //
  0b10001101, // jz win
  0b01010111, //
  0b10000111, // cp 90
  0b01011010, //
  0b10001101, // jz loss
  0b01011110, //
  0b10001001, // jp end
  0b01101101, //
  0b10011101, // inp (opp_paper)
  0b00000000, // nop
  0b00000000, // nop
  0b10011101, // inp
  0b10000111, // cp 88
  0b01011000, //
  0b10001101, // jz loss
  0b01011110, //
  0b10000111, // cp 89
  0b01011001, //
  0b10001101, // jz tie
  0b01010000, //
  0b10000111, // cp 90
  0b01011010, //
  0b10001101, // jz win
  0b01010111, //
  0b10001001, // jp end
  0b01101101, //
  0b10011101, // inp (opp_scissor)
  0b00000000, // nop
  0b00000000, // nop
  0b10011101, // inp
  0b10000111, // cp 88
  0b01011000, //
  0b10001101, // jz win
  0b01010111, //
  0b10000111, // cp 89
  0b01011001, //
  0b10001101, // jz loss
  0b01011110, //
  0b10000111, // cp 90
  0b01011010, //
  0b10001101, // jz tie
  0b01010000, //
  0b10001001, // jp end
  0b01101101, //
  0b10000101, // sub 87 (tie)
  0b01010111, //
  0b10000011, // add 3
  0b00000011, //
  0b01100000, // out a
  0b10001001, // jp update_total
  0b01100011, //
  0b10000101, // sub 87 (win)
  0b01010111, //
  0b10000011, // add 6
  0b00000110, //
  0b01100000, // out a
  0b10001001, // jp update_total
  0b01100011, //
  0b10000101, // sub 87 (loss)
  0b01010111, //
  0b01100000, // out a
  0b10001001, // jp update_total
  0b01100011, //
  0b00100010, // add c (update_total)
  0b00011000, // ld c,a
  0b00000010, //
  0b00010000, // ld a,0
  0b00000000, //
  0b01101001, // adc b
  0b00011000, // ld b,a
  0b00000001, //
  0b10001001, // jp begin
  0b00000100, //
  0b01100001, // out b (end)
  0b10010100, // jsr delay
  0b01110101, //
  0b01100010, // out c
  0b10010100, // jsr delay
  0b01110101, //
  0b10001001, // jp end
  0b01101101, //
  0b00010000, // ld a,100 (delay)
  0b01100100, //
  0b10011011, // dec (loop)
  0b10010001, // jnz loop
  0b01110111, //
  0b10010101, // ret
};

// The data segment to write to memory
byte data[] = {
  0b00000000, // db 0 (x8)
  0b00000000, //
  0b00000000, //
  0b00000000, //
  0b00000000, //
  0b00000000, //
  0b00000000, //
  0b00000000, //
};

// BUS
#define D0 4
#define D1 5
#define D2 6
#define D3 7
#define D4 8
#define D5 9
#define D6 10
#define D7 11

// Control lines
#define MI 12      // Active high
#define RI 13      // Active high
#define SR 2       // Active low
#define RST A1     // Active high
#define CE A4      // Active low
#define SS A5      // Active high


// Clock input. Connected to the inverse clock signal, because it was closer on
// the breadboard.
#define CLK_INV 3 // Inverse clock signal

// Clock flanks
#define UP 0       // LOW -> HIGH
#define DOWN 1     // HIGH -> LOW

int clock = LOW;
bool new_clock_state = false;
bool microstep_reset = false;
int microstep = 0;

void clock_changed() {
  new_clock_state = true;
  clock = !digitalRead(CLK_INV);

  if(clock == LOW) {
    if(microstep_reset) {
      microstep = 0;
      microstep_reset = false;
    } else {
      microstep ++;
    }
    if(digitalRead(SR) == LOW) {
      microstep_reset = true;
    }
  }
}

/**
 * Entry-point that is run upon power-on.
 */
void setup() {
  Serial.begin(115200);
  takeControl();
  writeProgramToRam();
  Serial.println("WELCOME");
  attachInterrupt(digitalPinToInterrupt(CLK_INV), clock_changed, CHANGE);
  releaseControl();
}

/**
 * After setup() completes, this function is called in an infinite loop.
 */
bool input_requested = false;
bool input_being_written = false;
bool ready_for_new_input = true;
int next_input = -1;
void loop() {
  if(digitalRead(RST)) {
    Serial.println("RESET");
    microstep = 0;
  }

  if(ready_for_new_input && Serial.available()) {
    next_input = Serial.read();
    ready_for_new_input = false;
    Serial.println(next_input);    
  }

  if(!new_clock_state) {
    return;
  }

  if(microstep == 1 && clock == HIGH) {
    int instruction = readFromBus();
    if(instruction == 157) { // INP
      input_requested = true;
    }
  }
  else if(microstep == 2 && input_requested) {
      // Connect to the bus
      for(int i=D0; i<=D7; i++) {
        pinMode(i, OUTPUT);
      }
      // int val = Serial.read();
      //Serial.println("Writing to bus.");
      writeToBus(next_input);
      input_being_written = true;
      input_requested = false;
  } else if(microstep != 2 && input_being_written) {
    //Serial.println("Stop writing to bus.");
    // Disconnect from the bus
    for(int i=D0; i<=D7; i++) {
      pinMode(i, INPUT);
    }
    input_being_written = false;
    ready_for_new_input = true;
    next_input = -1;
  }
 
  new_clock_state = false;
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
  pinMode(SS, OUTPUT);
  digitalWrite(MI, LOW);
  digitalWrite(RI, LOW);
  digitalWrite(SS, LOW);

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
  digitalWrite(SS, LOW);
  pinMode(MI, INPUT);
  pinMode(RI, INPUT);
  pinMode(SS, INPUT);
  pinMode(SR, INPUT);

  // Hit the master reset
  pinMode(RST, OUTPUT);
  digitalWrite(RST, HIGH);
  //delay(5);
  digitalWrite(RST, LOW);
  pinMode(RST, INPUT);
  
  waitOnClock(LOW);

  // Hand over control to the EEPROMs
  digitalWrite(CE, LOW);
  microstep_reset = true;
}

/**
 * Write the program into RAM memory.
 */
void writeProgramToRam() {
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
  digitalWrite(SS, LOW);
  int nBytesToWrite = sizeof(program);
  for(byte address=0; address<nBytesToWrite; address++) {
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

  digitalWrite(SS, HIGH);
  nBytesToWrite = sizeof(data);
  for(byte address=0; address<nBytesToWrite; address++) {
    // Write address
    writeToBus(address);
    digitalWrite(MI, HIGH);
    digitalWrite(RI, LOW);
    waitOnClockFlank(DOWN); // Keep values until next clock pulse

    // Write to RAM
    writeToBus(data[address]);
    digitalWrite(MI, LOW);
    digitalWrite(RI, HIGH);
    waitOnClockFlank(DOWN); // Keep values until next clock pulse
  }

  // Stop doing things
  digitalWrite(SS, LOW);
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
  for(int i=0; i<8; i++) {
    // Write the i'th bit of val to the correct line of the bus
    digitalWrite(D0 + i, (val >> i) & 1);
  }
}

/**
 * Read an 8-bit value from the bus.
 */
int readFromBus() {
  int val = 0;
  for(int i=7; i>=0; i--) {
    // Read the i'th bit of val from the correct line of the bus
    val += digitalRead(D0 + i) << i;
  }
  return val;
}