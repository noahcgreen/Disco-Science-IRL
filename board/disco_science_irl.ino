/*
disco_science_irl.ino
Disco Science IRL for Adafruit Flora

This program cycles the onboard NeoPixel through a sequence of colors.
The USB serial connection can be used to set the color sequence. This
is done by sending 3 bytes per color (RGB), followed by the delimiter
0xFF. The delimiter cannot be used as one of the color bytes, and no
more than 7 colors can be set at once.
*/

#include <FastLED.h>

#define NEOPIXEL_PIN 8

// Maximum number of colors that can be stored to cycle through
#define COLORS_LENGTH 7
// Bytes necessary for RGB color buffer
#define COLORS_BUFFER_LENGTH (COLORS_LENGTH * 3)

// Serial connection parameters
#define SERIAL_DELIMITER 255
#define SERIAL_BAUD_RATE 9600

// Note: Color cycle length is dependent on frame duration, i.e.,
// increasing frame duration makes the entire animation slower
#define FRAME_DURATION 10

// Color sequence
CRGB colors[COLORS_LENGTH];
// Number of colors in the above buffer
size_t colors_size;

// Serial buffer
char colors_buffer[COLORS_BUFFER_LENGTH];
// Number of bytes in the above buffer
size_t colors_buffer_size;

// Index of color currently shown
int color_index;

// Cycle step for each color
// Transition to next color occurs when step resets to 0
uint8_t step;

// FastLED buffer
CRGB led;

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);

  FastLED.addLeds<NEOPIXEL, NEOPIXEL_PIN>(&led, 1);
  led = CRGB::Black;
  FastLED.show();

  colors[0] = CRGB::Black;
  colors_size = 1;
  color_index = 0;
  step = 0;
}

void loop() {
  if (Serial.available()) {
    updateColors();
  }

  EVERY_N_MILLISECONDS(FRAME_DURATION) {
    showColors(step++);
  }
}

// Read in new colors from serial
void updateColors() {
  colors_buffer_size = Serial.readBytesUntil(SERIAL_DELIMITER, colors_buffer, COLORS_BUFFER_LENGTH);
  colors_size = colors_buffer_size / 3;

  for (int i = 0; i < colors_size; i++) {
    colors[i].setRGB(colors_buffer[i * 3], colors_buffer[i * 3 + 1], colors_buffer[i * 3 + 2]);
  }

  color_index = 0;
}

// Write colors to board and advance color state
void showColors(uint8_t step) {
  // Cap brightness at 50%
  FastLED.setBrightness(cubicwave8(step) / 2);
  // Write to board
  FastLED.show();

  // Advance color if necessary
  if (step == 255) {
    color_index = (color_index + 1) % colors_size;
    led = colors[color_index];
  }
}
