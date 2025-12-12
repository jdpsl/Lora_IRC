import socket
import ssl
import serial
import threading
import json
import base64
import time
import os


BLUE = '\033[0;34m'
NC = '\033[0m'

print(f"{BLUE}██╗{NC}      {BLUE}██████╗{NC} {BLUE}██████╗{NC}  {BLUE}█████╗{NC}     {BLUE}██╗{NC}      {BLUE}██╗██████╗{NC}  {BLUE}██████╗{NC}")
print(f"{BLUE}██║{NC}     {BLUE}██╔═══██╗{NC}{BLUE}██╔══██╗{NC}{BLUE}██╔══██╗{NC}    {BLUE}╚██╗{NC}     {BLUE}██║██╔══██╗██╔════╝{NC}")
print(f"{BLUE}██║{NC}     {BLUE}██║   ██║{NC}{BLUE}██████╔╝{NC}{BLUE}███████║{NC}     {BLUE}╚██╗{NC}    {BLUE}██║██████╔╝██║{NC}     ")
print(f"{BLUE}██║{NC}     {BLUE}██║   ██║{NC}{BLUE}██╔══██╗{NC}{BLUE}██╔══██║{NC}     {BLUE}██╔╝{NC}    {BLUE}██║██╔══██╗██║{NC}     ")
print(f"{BLUE}███████╗{NC}{BLUE}╚██████╔╝{NC}{BLUE}██║  ██║{NC}{BLUE}██║  ██║{NC}    {BLUE}██╔╝{NC}     {BLUE}██║██║  ██║╚██████╗{NC}")
print(f"{BLUE}╚══════╝{NC} {BLUE}╚═════╝{NC} {BLUE}╚═╝  ╚═╝{NC}{BLUE}╚═╝  ╚═╝{NC}    {BLUE}╚═╝{NC}      {BLUE}╚═╝╚═╝  ╚═╝ ╚═════╝{NC}")


# Load configuration
def load_config(config_path='config.json'):
    if not os.path.exists(config_path):
        print(f"Error: Config file '{config_path}' not found!")
        print("Please create a config.json file. See config.example.json for reference.")
        exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()

# IRC server details
server = config['irc']['server']
port = config['irc']['port']
channel = config['irc']['channel']
nickname = config['irc']['nickname']
use_ssl = config['irc']['use_ssl']
nickserv_enabled = config['irc']['nickserv']['enabled']
nickserv_password = config['irc']['nickserv']['password']
sasl_enabled = config['irc']['sasl']['enabled']
sasl_username = config['irc']['sasl']['username']
sasl_password = config['irc']['sasl']['password']

# Serial port for Arduino/LoRa
serial_port = config['serial']['port']
baud_rate = config['serial']['baud_rate']

# Initialize serial connection to Arduino
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Connected to serial port: {serial_port}")
except Exception as e:
    print(f"Error connecting to serial port: {e}")
    exit(1)

# Connect to IRC server
irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Wrap with SSL if enabled
if use_ssl:
    context = ssl.create_default_context()
    irc = context.wrap_socket(irc_socket, server_hostname=server)
    print(f"Connecting to {server}:{port} with SSL...")
else:
    irc = irc_socket
    print(f"Connecting to {server}:{port} without SSL...")

irc.connect((server, port))
print("Connected to IRC server")

# SASL Authentication (PLAIN mechanism)
if sasl_enabled:
    print("Attempting SASL authentication...")
    irc.send(b"CAP REQ :sasl\r\n")

    # Wait for CAP ACK
    time.sleep(1)

    irc.send(b"AUTHENTICATE PLAIN\r\n")

    # Wait for AUTHENTICATE +
    time.sleep(1)

    # Encode credentials for SASL PLAIN
    auth_string = f"{sasl_username}\0{sasl_username}\0{sasl_password}"
    auth_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    irc.send(f"AUTHENTICATE {auth_encoded}\r\n".encode('utf-8'))

    # Wait for authentication response
    time.sleep(1)

    irc.send(b"CAP END\r\n")
    print("SASL authentication sent")

# Send IRC commands
irc.send(f"NICK {nickname}\r\n".encode('utf-8'))
irc.send(f"USER {nickname} 0 * :LoRa Bot\r\n".encode('utf-8'))

# Wait for connection to complete
time.sleep(2)

# NickServ authentication
if nickserv_enabled and nickserv_password:
    print("Authenticating with NickServ...")
    irc.send(f"PRIVMSG NickServ :IDENTIFY {nickserv_password}\r\n".encode('utf-8'))
    time.sleep(2)

# Join channel
irc.send(f"JOIN {channel}\r\n".encode('utf-8'))
print(f"Joined channel: {channel}")

def send_message_to_channel(message):
    irc.send(f"PRIVMSG {channel} :{message}\r\n".encode('utf-8'))
    print(f"Sent to IRC: {message}")

# Function to handle incoming LoRa messages
def handle_lora():
    while True:
        try:
            if ser.in_waiting > 0:
                lora_message = ser.readline().decode('utf-8').strip()
                if lora_message:
                    # Format the message as <Lora User>: <Message>
                    send_message_to_channel(f"<Lora User>: {lora_message}")
        except Exception as e:
            print(f"Error handling LoRa message: {e}")

# Function to handle IRC messages and pings
def handle_irc():
    while True:
        try:
            irc_data = irc.recv(2048).decode('utf-8', errors='ignore').strip()

            if not irc_data:
                continue

            # Print raw IRC data for debugging
            # print(f"IRC: {irc_data}")

            if irc_data.startswith("PING"):
                pong_response = f"PONG {irc_data.split()[1]}\r\n"
                irc.send(pong_response.encode('utf-8'))
                print("Responded to PING")

            elif "PRIVMSG" in irc_data:
                try:
                    nick = irc_data.split('!')[0][1:]
                    message = irc_data.split('PRIVMSG')[1].split(':', 1)[1]

                    # Check if user is admin or has voice (usually "+v" for voiced)
                    # Note: This is a simplified check. For production, consider using WHO or WHOIS
                    if f"{channel} +v" in irc_data or "admin" in irc_data:
                        # Format the outgoing message as <IRC Username>: <Message>
                        lora_message = f"<{nick}>: {message}"
                        ser.write(f"{lora_message}\n".encode('utf-8'))
                        print(f"Sent to LoRa: {lora_message}")
                    else:
                        # For now, forward all messages (consider adding proper access control)
                        lora_message = f"<{nick}>: {message}"
                        ser.write(f"{lora_message}\n".encode('utf-8'))
                        print(f"Sent to LoRa: {lora_message}")

                except Exception as e:
                    print(f"Error parsing PRIVMSG: {e}")

        except Exception as e:
            print(f"Error handling IRC message: {e}")
            time.sleep(1)

# Start threads to handle LoRa and IRC messages concurrently
lora_thread = threading.Thread(target=handle_lora, daemon=True)
irc_thread = threading.Thread(target=handle_irc, daemon=True)

lora_thread.start()
irc_thread.start()

print("Bot is running. Press Ctrl+C to stop.")

try:
    lora_thread.join()
    irc_thread.join()
except KeyboardInterrupt:
    print("\nShutting down...")
    irc.send(f"QUIT :LoRa Bot shutting down\r\n".encode('utf-8'))
    irc.close()
    ser.close()
    print("Goodbye!")
