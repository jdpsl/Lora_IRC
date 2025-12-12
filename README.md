```
██╗      ██████╗ ██████╗  █████╗     ██╗      ██╗██████╗  ██████╗
██║     ██╔═══██╗██╔══██╗██╔══██╗    ╚██╗     ██║██╔══██╗██╔════╝
██║     ██║   ██║██████╔╝███████║     ╚██╗    ██║██████╔╝██║
██║     ██║   ██║██╔══██╗██╔══██║     ██╔╝    ██║██╔══██╗██║
███████╗╚██████╔╝██║  ██║██║  ██║    ██╔╝     ██║██║  ██║╚██████╗
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝      ╚═╝╚═╝  ╚═╝ ╚═════╝
```

A bidirectional bridge connecting LoRa (Long Range) radio modules with IRC (Internet Relay Chat) channels. This enables long-range wireless mesh communication across cities, allowing LoRa users and IRC users to communicate seamlessly.

Deploy bots in multiple cities to create a distributed, wide-area communication network that extends beyond LoRa's typical range through internet-connected relay points.

## Features

- **Bidirectional messaging** between LoRa radio and IRC
- **SSL/TLS support** for secure IRC connections
- **SASL authentication** for modern IRC servers
- **NickServ authentication** for legacy IRC networks
- **JSON configuration** for easy setup
- **Multithreaded design** ensures IRC PINGs are answered even during LoRa operations
- **Error handling and graceful shutdown**

## Requirements

### Hardware
- Arduino board (Uno, Mega, Nano, or compatible)
- LoRa module (SX1276/SX1278 based, e.g., RFM95/96/97/98)
- USB cable for Arduino connection

### Software
- Python 3.6+
- Arduino IDE (for uploading sketch to Arduino)
- Required Python packages:
  - `pyserial`
- Required Arduino libraries:
  - `LoRa` by Sandeep Mistry (install via Library Manager)

## Installation

### 1. Hardware Setup

Wire your LoRa module to the Arduino:
- **VCC** → 3.3V (IMPORTANT: Most LoRa modules are 3.3V only!)
- **GND** → GND
- **SCK** → Pin 13 (or SCK)
- **MISO** → Pin 12 (or MISO)
- **MOSI** → Pin 11 (or MOSI)
- **NSS/CS** → Pin 10
- **RST** → Pin 9
- **DIO0** → Pin 2

### 2. Arduino Setup

1. Install the Arduino IDE from https://www.arduino.cc/

2. Install the LoRa library:
   - Open Arduino IDE → Sketch → Include Library → Manage Libraries
   - Search for "LoRa" by Sandeep Mistry
   - Click Install

3. Open `Arduino Sketch/Main.ino` in Arduino IDE

4. Configure the frequency for your region (line 36):
   - 915 MHz for North America (default)
   - 868 MHz for Europe
   - 433 MHz for Asia

5. Upload the sketch to your Arduino

### 3. Python Setup

1. Clone the repository:
```bash
git clone https://github.com/jdpsl/Lora_IRC.git
cd Lora_IRC
```

2. Install Python dependencies:
```bash
pip install pyserial
```

3. Configure your settings:
```bash
cp config.example.json config.json
# Edit config.json with your IRC server and serial port settings
```

4. Find your Arduino's serial port:
```bash
# Linux/Mac
ls /dev/tty*

# Windows: Check Device Manager or Arduino IDE Tools → Port
```

5. Update `config.json` with your Arduino's serial port (e.g., `/dev/ttyUSB0`)

## Configuration

Edit `config.json` to set up your IRC server and serial port:

```json
{
  "irc": {
    "server": "irc.libera.chat",
    "port": 6697,
    "channel": "#lora",
    "nickname": "LoraBot",
    "use_ssl": true,
    "nickserv": {
      "enabled": false,
      "password": "your_password_here"
    },
    "sasl": {
      "enabled": false,
      "username": "LoraBot",
      "password": "your_sasl_password"
    }
  },
  "serial": {
    "port": "/dev/ttyUSB0",
    "baud_rate": 9600
  }
}
```

**Configuration Options:**
- `use_ssl`: Set to `true` for encrypted connections (recommended)
- `nickserv.enabled`: Enable if your IRC network uses NickServ authentication
- `sasl.enabled`: Enable for servers supporting SASL (modern standard)
- `serial.port`: Your Arduino's serial port (check with `ls /dev/tty*`)

## Usage

1. Connect your Arduino with the uploaded sketch

2. Run the Python bridge:
```bash
python loraIRC.py
```

3. You should see:
   - Arduino LED blinks 3 times on successful LoRa initialization
   - Python script connects to IRC server
   - Messages start flowing between LoRa and IRC

4. LED Indicators:
   - **3 blinks on startup**: LoRa initialized successfully
   - **Rapid blinking**: LoRa initialization failed (check wiring)
   - **Brief blink**: Receiving LoRa message
   - **Brief blink**: Transmitting LoRa message

5. Press `Ctrl+C` to gracefully shut down

## How It Works

- Messages received from LoRa radio are formatted as `<Lora User>: message` and sent to IRC
- Messages from IRC users are formatted as `<IRC Username>: message` and sent to LoRa
- The bot runs two independent threads:
  - One monitors the serial port for LoRa messages
  - One monitors IRC for messages and responds to server PINGs
- This ensures the bot stays connected to IRC even while waiting for LoRa data

## Project Status

**Python Bridge:** ✓ Complete and functional
**Arduino Sketch:** ✓ Complete and functional

Both components are ready for deployment!

## Hardware Notes

- **IMPORTANT**: Most LoRa modules operate at 3.3V. Connecting them to 5V will damage the module!
- Use a logic level converter if your Arduino is 5V and doesn't have 3.3V-tolerant pins
- Range depends on:
  - Antenna quality (use a proper antenna tuned to your frequency)
  - Environment (line-of-sight is best)
  - LoRa parameters (higher spreading factor = longer range but slower speed)
- Typical range: 2-10 km in urban areas, up to 20+ km in rural areas

## Troubleshooting

**Arduino sketch won't compile:**
- Make sure you have the "LoRa" library by Sandeep Mistry installed
- Check that your Arduino IDE is up to date

**LoRa initialization fails (rapid LED blinking):**
- Check wiring, especially power (3.3V) and SPI connections
- Verify pin definitions match your wiring
- Some modules require DIO1 to be connected; check your module's datasheet

**Python script can't connect to serial port:**
- Check the serial port name in `config.json`
- On Linux, you may need to add your user to the `dialout` group: `sudo usermod -a -G dialout $USER`
- Make sure no other program (like Arduino IDE Serial Monitor) has the port open

**Messages not flowing:**
- Check that Arduino is powered and running (LED should have blinked 3 times)
- Verify serial baud rate matches (9600) in both Arduino and Python
- Test LoRa connection with a second Arduino running the same sketch

## Contributing

Contributions are welcome! I would love to see these deployed in multiple locations. Please feel free to:
- Report issues
- Submit pull requests
- Share your deployment experiences
- Suggest improvements

