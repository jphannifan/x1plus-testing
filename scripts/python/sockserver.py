import socket
import socketserver
import threading
import json
import os

# threaded TCP server example - used to communicate from a remote device to your X1C
# The example here will turn the backlight and chamber LED on/off when it receives 
# LED_ON and LED_OFF, which you can send remotely via netcat or other tools

def example_command	(command):
    if command == "LED_ON":
        print("Turning sys led and backlight on")
        os.system("echo 255 > /sys/devices/platform/gpio-leds/leds/sys_led/brightness")
        os.system("echo 255 > /sys/devices/platform/backlight/backlight/backlight/brightness")
        return "on"
    elif command == "LED_OFF":
        print("Turning sys led and backlight off")
        os.system("echo 0 > /sys/devices/platform/gpio-leds/leds/sys_led/brightness")
        os.system("echo 0 > /sys/devices/platform/backlight/backlight/backlight/brightness")        
        return "off"
    else:
        return "Unknown command."

class ReqHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print(f"Received: {self.data} from {self.client_address[0]}")
        response = self.server.command_processor(self.data)
        self.request.sendall(response.encode('utf-8'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class SockServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = ThreadedTCPServer((host, port), ReqHandler)
        self.server.command_processor = example_command

    def start(self):
        print(f"Starting printer server on {self.host}:{self.port}")
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        print("Printer server stopped.")

def send_command(host, port, command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(command.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        print(f"Server response: {response}")


# Import this class into a script running on the X1 and communicate with it via netcat or another tool
# ex: echo "LED_ON" | nc 192.168.x.xx 9999
# replace 192.168.x.xx with your printer's ip address
HOST, PORT = "0.0.0.0", 9999
server = SockServer(HOST, PORT)
print("Server is running...")
server.start()

try:
	input("Press Enter to stop the server...\n")
finally:
	server.stop()





