import csv
import os
import cv2
import pickle
import time
import zmq
import argparse
import threading
from queue import Queue
from modules.depthai.utils import get_files

class GPSSubscriber:
    def __init__(self, port='6000'):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f'tcp://localhost:{port}')
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, '')

    def receive_data(self):
        serialized_data = self.subscriber.recv()
        return pickle.loads(serialized_data)

    def close(self):
        self.subscriber.close()
        self.context.term()

class DataCollector(threading.Thread):
    def __init__(self, ports, mxids, out, gps_queue):
        super().__init__()
        self.ports = ports
        self.mxids = mxids
        self.out = out
        self.gps_queue = gps_queue
        self.context = zmq.Context()
        self.subscribers = []
        self.files_dict = {}
        self.lock = threading.Lock()
        self.time = ''

        for port, mxid in zip(ports, mxids):
            subscriber = self.context.socket(zmq.SUB)
            subscriber.connect(f"tcp://localhost:{port}")
            subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
            self.subscribers.append(subscriber)
            self.files_dict[port] = get_files(out, f"{mxid}_{port}")

    def run(self):
        while True:
            for port, subscriber in zip(self.ports, self.subscribers):
                try:
                    message = pickle.loads(subscriber.recv(zmq.NOBLOCK))
                    file_color, file_monoL, file_monoR, file_imus = self.files_dict[port]
                    timestamp = message['depth']['timestamp']
                    
                    with self.lock:
                        file_color.write(message["color"])
                        file_monoL.write(message["monoL"])
                        file_monoR.write(message["monoR"])
                        depth_file_name = f"depth_{message['camera_id']}/" + str(message['depth']['sequence']) + f"_{timestamp}.png"
                        cv2.imwrite(os.path.join(self.out, depth_file_name), message['depth']['frame'])
                        file_imus.write((str(message['imu']) + '\n').encode())
                        self.time = timestamp
                except zmq.Again:
                    pass

class GPSCollector(threading.Thread):
    def __init__(self, port, out, gps_queue):
        super().__init__()
        self.gps_subscriber = GPSSubscriber(port=port)
        self.out = out
        self.gps_queue = gps_queue

    def run(self):
        with open(os.path.join(self.out, 'gnrmc_data.csv'), mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Timestamp', 'GNRMC Data'])
            while True:
                data = self.gps_subscriber.receive_data()
                self.gps_queue.put(data)

def main():
    parser = argparse.ArgumentParser(description="Data Collection Subscriber")
    parser.add_argument('--port_nos', type=str, required=True, help="Comma-separated list of publisher port numbers")
    parser.add_argument('--out', type=str, required=True, help="Output directory.")
    parser.add_argument('--mxids', type=str, required=True, help="Camera MX ID.")
    parser.add_argument('--gps', type=bool, default=False, help="GPS data to be collected or not.")
    args = parser.parse_args()

    print(f'Camera ID         : {args.mxids}')
    print(f'Port Nos          : {args.port_nos}')
    print(f'Press Ctrl+C to stop subscriber...')

    ports = args.port_nos.split(',')
    mxids = args.mxids.split(',')
    gps_queue = Queue()

    data_collector = DataCollector(ports, mxids, args.out, gps_queue)
    data_collector.start()

    if args.gps:
        gps_collector = GPSCollector(port=6000, out=args.out, gps_queue=gps_queue)
        gps_collector.start()

    while True:
        if not gps_queue.empty():
            gps_data = gps_queue.get()
            with open(os.path.join(args.out, 'gnrmc_data.csv'), mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([data_collector.time, gps_data])

if __name__ == "__main__":
    main()
