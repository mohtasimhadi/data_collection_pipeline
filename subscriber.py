import csv
import os
import cv2
import pickle
import zmq
import argparse
from modules.depthai.utils import get_files

class GPSSubscriber:
    def __init__(self, port='5555', out='out'):
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

    context = zmq.Context()
    ports = args.port_nos.split(',')
    mxids = args.mxids.split(',')
    subscribers = []
    files_dict = {}

    for port, mxid in zip(ports, mxids):
        subscriber = context.socket(zmq.SUB)
        subscriber.connect(f"tcp://localhost:{port}")
        subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        subscribers.append(subscriber)
        files_dict[port] = get_files(args.out, f"{mxid}_{port}")
    time = "-"
    if args.gps:
        gps_subscriber = GPSSubscriber(port=6000, out=args.out)
        with open(args.out+'/gnrmc_data.csv', mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Timestamp', 'GNRMC Data'])

    while True:
        for port, subscriber in zip(ports, subscribers):
            try:
                message = pickle.loads(subscriber.recv(zmq.NOBLOCK))
                file_color, file_monoL, file_monoR, file_imus = files_dict[port]
                time = message['depth']['timestamp']
                file_color.write(message["color"])
                file_monoL.write(message["monoL"])
                file_monoR.write(message["monoR"])
                depth_file_name = f"depth_{message['camera_id']}/" + str(message['depth']['sequence']) + f"_{str(message['depth']['timestamp'])}.png"
                cv2.imwrite(os.path.join(args.out, depth_file_name), message['depth']['frame'])
                
                file_imus.write((str(message['imu']) + '\n').encode())
            except zmq.Again:
                pass
        if args.gps:
            with open(args.out+'/gnrmc_data.csv', mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([time, gps_subscriber.receive_data()])

if __name__ == "__main__":
    main()
