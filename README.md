# crapbot

https://github.com/juanmed/nano_gpio/blob/master/gpio1.py

# To install GPIO lib for jetson
https://github.com/NVIDIA/jetson-gpio

# To install periphery

`sudo pip install python-periphery`

#ARDUINO CODE
void setup() {
  // start serial port at 9600 bps:
  Serial.begin(9600);
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  while (!Serial) {
    ; // wait for serial port to connect.
  }

}

void loop() {
  char buffer[16];
  // if we get a command, turn the LED on or off:
  if (Serial.available() > 0) {
    int size = Serial.readBytesUntil('\n', buffer, 12);
    if (buffer[0] == 'Y') {
      digitalWrite(LED_BUILTIN, HIGH);
    }
    if (buffer[0] == 'N') {
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
}
#END ARDUINO CODE