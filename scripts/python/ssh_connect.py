import paramiko
import time
import select

# SSH connection in Python for communicating from a remote device to your X1C

class SSHClient:
    def __init__(self, hostname,port, username, password, retry_interval=5, max_retries=3):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.client = paramiko.SSHClient()

    def connect(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for attempt in range(self.max_retries):
            try:
                self.client.connect(self.hostname, self.port, username=self.username, password=self.password)
                return 
            except (paramiko.SSHException, paramiko.ssh_exception.NoValidConnectionsError) as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_interval) 
                else:
                    raise 

    def is_active(self):
        transport = self.client.get_transport()
        return transport and transport.is_active() and transport.sock is not None

    def execute_command(self, command, timeout=2):
        if not self.is_active():
            self.connect()
        stdin, stdout, stderr = self.client.exec_command(command)
        while not select.select([stdout.channel], [], [], timeout)[0]:
            if not self.is_active():
                raise Exception("SSH connection dropped")
        return stdout.read().decode().strip()

    def send_file_to_printer(self, local_filepath, remote_filepath):
        if not self.is_active():
            self.connect()
        try:
            with self.client.open_sftp() as sftp:
                sftp.put(local_filepath, remote_filepath)
            print(f"File {local_filepath} successfully sent to printer.")
        except Exception as e:
            print(f"Failed to send file: {e}")
        finally:
            if self.client:
                self.client.close()
                
            
    def connect_with_retry(self, max_retries=5, retry_delay=5):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for attempt in range(max_retries):
            try:
                self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
                print("SSH connection established.")
                return True
            except paramiko.SSHException as e:
                print(f"SSH connection attempt {attempt + 1} failed: {e}")
                time.sleep(retry_delay)
        raise Exception("SSH connection failed after retries")
    
    def close(self):
        if self.client:
            self.client.close()

