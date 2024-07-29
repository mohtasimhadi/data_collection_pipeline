import zmq
import serial
import threading
import pickle

class GPSPublisher:
    def __init__(self, port='5555', serial_port='/dev/ttyACM0', serial_baudrate=115200):
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f'tcp://*:{port}')
        
        self.serial_port = serial_port
        self.serial_baudrate = serial_baudrate
        self.serial_conn = serial.Serial(self.serial_port, self.serial_baudrate, timeout=1)
        
        self.read_thread = threading.Thread(target=self.read_serial)
        self.read_thread.daemon = True
        self.read_thread.start()
    
    def read_serial(self):
        while True:
            line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith('$GNRMC'):
                # Serialize the data using pickle
                serialized_data = pickle.dumps(line)
                # Publish the serialized data
                self.publisher.send(serialized_data)

    def close(self):
        self.serial_conn.close()
        self.publisher.close()
        self.context.term()