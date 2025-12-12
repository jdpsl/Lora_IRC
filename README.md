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

- Python 3.6+
- Arduino with LoRa module
- Required Python packages:
  - `pyserial`

## Installation

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

1. Upload the Arduino sketch to your LoRa-equipped Arduino (Arduino sketch coming soon)

2. Run the Python bridge:
```bash
python loraIRC.py
```

3. The bot will connect to IRC and start bridging messages

4. Press `Ctrl+C` to gracefully shut down

## How It Works

- Messages received from LoRa radio are formatted as `<Lora User>: message` and sent to IRC
- Messages from IRC users are formatted as `<IRC Username>: message` and sent to LoRa
- The bot runs two independent threads:
  - One monitors the serial port for LoRa messages
  - One monitors IRC for messages and responds to server PINGs
- This ensures the bot stays connected to IRC even while waiting for LoRa data

## Project Status

**Python Bridge:** ✓ Complete and functional
**Arduino Sketch:** 🚧 In development

Contributions are welcome! I would love to see these deployed in multiple locations.

