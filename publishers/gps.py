import argparse
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
    
    def read_serial(self):
        print("GPS Data Publisher started...")
        while True:
            line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith('$GNRMC'):
                serialized_data = pickle.dumps(line)
                self.publisher.send(serialized_data)