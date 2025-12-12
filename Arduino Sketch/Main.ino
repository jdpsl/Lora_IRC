/*
 * LoRa IRC Bridge - Arduino Sketch
 *
 * This sketch bridges LoRa radio communication with a serial connection
 * to a Python script that forwards messages to/from IRC.
 *
 * Hardware Requirements:
 * - Arduino (Uno, Mega, Nano, etc.)
 * - LoRa Module (SX1276/SX1278 based, e.g., RFM95/96/97/98)
 *
 * Wiring (for SPI-based LoRa modules):
 * - VCC -> 3.3V
 * - GND -> GND
 * - SCK -> Pin 13 (or SCK)
 * - MISO -> Pin 12 (or MISO)
 * - MOSI -> Pin 11 (or MOSI)
 * - NSS -> Pin 10 (configurable)
 * - RST -> Pin 9 (configurable)
 * - DIO0 -> Pin 2 (configurable)
 *
 * Required Library:
 * - LoRa by Sandeep Mistry
 *   Install via Arduino Library Manager: Sketch -> Include Library -> Manage Libraries -> Search "LoRa"
 */

#include <SPI.h>
#include <LoRa.h>

// LoRa module pin configuration
#define SS_PIN 10      // NSS/CS pin
#define RST_PIN 9      // Reset pin
#define DIO0_PIN 2     // DIO0 pin (for receive interrupt)

// LoRa frequency configuration
// Uncomment the appropriate frequency for your region:
#define LORA_FREQUENCY 915E6   // 915 MHz (North America)
// #define LORA_FREQUENCY 868E6   // 868 MHz (Europe)
// #define LORA_FREQUENCY 433E6   // 433 MHz (Asia)

// LoRa transmission parameters
#define LORA_TX_POWER 20       // Transmission power in dBm (2-20)
#define LORA_SPREADING_FACTOR 7 // Spreading factor (6-12, higher = longer range but slower)
#define LORA_SIGNAL_BANDWIDTH 125E3 // Bandwidth in Hz (7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3)
#define LORA_CODING_RATE 5     // Coding rate denominator (5-8, higher = more error correction)

// Serial configuration
#define SERIAL_BAUD 9600
#define MAX_MESSAGE_LENGTH 255

// Buffer for incoming serial data
String serialBuffer = "";

// LED pin for status indication (built-in LED on most Arduinos)
#define LED_PIN LED_BUILTIN

void setup() {
  // Initialize serial communication
  Serial.begin(SERIAL_BAUD);
  while (!Serial);  // Wait for serial port to connect (for native USB boards)

  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("LoRa IRC Bridge - Arduino");
  Serial.println("Initializing LoRa module...");

  // Initialize LoRa module
  LoRa.setPins(SS_PIN, RST_PIN, DIO0_PIN);

  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("ERROR: LoRa initialization failed!");
    Serial.println("Check your wiring and module connection.");
    while (1) {
      // Blink LED rapidly to indicate error
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
      delay(100);
    }
  }

  // Configure LoRa parameters
  LoRa.setTxPower(LORA_TX_POWER);
  LoRa.setSpreadingFactor(LORA_SPREADING_FACTOR);
  LoRa.setSignalBandwidth(LORA_SIGNAL_BANDWIDTH);
  LoRa.setCodingRate4(LORA_CODING_RATE);

  // Enable CRC for error detection
  LoRa.enableCrc();

  Serial.println("LoRa module initialized successfully!");
  Serial.print("Frequency: ");
  Serial.print(LORA_FREQUENCY / 1E6);
  Serial.println(" MHz");
  Serial.print("TX Power: ");
  Serial.print(LORA_TX_POWER);
  Serial.println(" dBm");
  Serial.print("Spreading Factor: ");
  Serial.println(LORA_SPREADING_FACTOR);
  Serial.println("Ready to bridge messages!");

  // Blink LED to indicate successful initialization
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}

void loop() {
  // Check for incoming LoRa packets
  handleLoRaReceive();

  // Check for incoming serial data from Python script
  handleSerialReceive();
}

// Handle incoming LoRa packets
void handleLoRaReceive() {
  int packetSize = LoRa.parsePacket();

  if (packetSize) {
    // Blink LED to indicate reception
    digitalWrite(LED_PIN, HIGH);

    // Read packet
    String message = "";
    while (LoRa.available()) {
      message += (char)LoRa.read();
    }

    // Get RSSI (Received Signal Strength Indicator)
    int rssi = LoRa.packetRssi();

    // Get SNR (Signal to Noise Ratio)
    float snr = LoRa.packetSnr();

    // Forward message to serial (Python script)
    if (message.length() > 0) {
      Serial.println(message);

      // Optional: Print signal quality info for debugging
      // Serial.print("  [RSSI: ");
      // Serial.print(rssi);
      // Serial.print(" dBm, SNR: ");
      // Serial.print(snr);
      // Serial.println(" dB]");
    }

    digitalWrite(LED_PIN, LOW);
  }
}

// Handle incoming serial data from Python script
void handleSerialReceive() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();

    // Check for newline (message delimiter)
    if (inChar == '\n') {
      if (serialBuffer.length() > 0) {
        // Transmit message via LoRa
        transmitLoRa(serialBuffer);
        serialBuffer = "";
      }
    } else {
      // Add character to buffer
      serialBuffer += inChar;

      // Prevent buffer overflow
      if (serialBuffer.length() >= MAX_MESSAGE_LENGTH) {
        transmitLoRa(serialBuffer);
        serialBuffer = "";
      }
    }
  }
}

// Transmit message via LoRa
void transmitLoRa(String message) {
  // Blink LED rapidly during transmission
  digitalWrite(LED_PIN, HIGH);

  // Begin LoRa packet
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();

  // Optional: Print confirmation for debugging
  // Serial.print("Transmitted: ");
  // Serial.println(message);

  delay(50);  // Brief delay to allow transmission to complete
  digitalWrite(LED_PIN, LOW);
}
