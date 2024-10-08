import socket
import serial
import threading


BLUE = '\033[0;34m'
NC = '\033[0m'

print(f"{BLUE}██╗{NC}      {BLUE}██████╗{NC} {BLUE}██████╗{NC}  {BLUE}█████╗{NC}     {BLUE}██╗{NC}      {BLUE}██╗██████╗{NC}  {BLUE}██████╗{NC}")
print(f"{BLUE}██║{NC}     {BLUE}██╔═══██╗{NC}{BLUE}██╔══██╗{NC}{BLUE}██╔══██╗{NC}    {BLUE}╚██╗{NC}     {BLUE}██║██╔══██╗██╔════╝{NC}")
print(f"{BLUE}██║{NC}     {BLUE}██║   ██║{NC}{BLUE}██████╔╝{NC}{BLUE}███████║{NC}     {BLUE}╚██╗{NC}    {BLUE}██║██████╔╝██║{NC}     ")
print(f"{BLUE}██║{NC}     {BLUE}██║   ██║{NC}{BLUE}██╔══██╗{NC}{BLUE}██╔══██║{NC}     {BLUE}██╔╝{NC}    {BLUE}██║██╔══██╗██║{NC}     ")
print(f"{BLUE}███████╗{NC}{BLUE}╚██████╔╝{NC}{BLUE}██║  ██║{NC}{BLUE}██║  ██║{NC}    {BLUE}██╔╝{NC}     {BLUE}██║██║  ██║╚██████╗{NC}")
print(f"{BLUE}╚══════╝{NC} {BLUE}╚═════╝{NC} {BLUE}╚═╝  ╚═╝{NC}{BLUE}╚═╝  ╚═╝{NC}    {BLUE}╚═╝{NC}      {BLUE}╚═╝╚═╝  ╚═╝ ╚═════╝{NC}")



# ToDO: Convert into a config file
# ToDO: Enable SSL
# TODO: Nickserv login
# ToDO: SASL Authentication

# IRC server details
server = "irc.server.com"  # Replace with your IRC server
port = 6667
channel = "#lora"
nickname = "LoraBot"

# Serial port for Arduino/LoRa
serial_port = "/dev/ttyUSB0"  # Replace with your serial port
baud_rate = 9600

# Initialize serial connection to Arduino
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Connect to IRC server
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, port))

# Send IRC commands
irc.send(f"NICK {nickname}\r\n".encode('utf-8'))
irc.send(f"USER {nickname} 0 * :LoRa Bot\r\n".encode('utf-8'))
irc.send(f"JOIN {channel}\r\n".encode('utf-8'))

def send_message_to_channel(message):
    irc.send(f"PRIVMSG {channel} :{message}\r\n".encode('utf-8'))
    print(f"PRIVMSG {channel} :{message}\r\n".encode('utf-8'))

# Function to handle incoming LoRa messages
def handle_lora():
    while True:
        if ser.in_waiting > 0:
            lora_message = ser.readline().decode('utf-8').strip()
            # Format the message as <Lora User>: <Message>
            send_message_to_channel(f"<Lora User>: {lora_message}")

# Function to handle IRC messages and pings
def handle_irc():
    while True:
        irc_data = irc.recv(2048).decode('utf-8', errors='ignore').strip()

        if irc_data.startswith("PING"):
            irc.send(f"PONG {irc_data.split()[1]}\r\n".encode('utf-8'))

        elif "PRIVMSG" in irc_data:
            nick = irc_data.split('!')[0][1:]
            message = irc_data.split('PRIVMSG')[1].split(':')[1]

            # Check if user is admin or has voice (usually "+v" for voiced)
            if f"{channel} +v" in irc_data or "admin" in irc_data:
                # Format the outgoing message as <IRC Username>: <Message>
                lora_message = f"<{nick}>: {message}"
                ser.write(f"{lora_message}\n".encode('utf-8'))

# Start threads to handle LoRa and IRC messages concurrently
lora_thread = threading.Thread(target=handle_lora)
irc_thread = threading.Thread(target=handle_irc)

lora_thread.start()
irc_thread.start()

lora_thread.join()
irc_thread.join()
