import os
import cv2
import pickle
import zmq
import argparse
from modules.depthai.utils import get_files

def main():
    parser = argparse.ArgumentParser(description="Data Collection Subscriber")
    parser.add_argument('--port_nos', type=str, required=True, help="Comma-separated list of publisher port numbers")
    parser.add_argument('--out', type=str, required=True, help="Output directory.")
    parser.add_argument('--mxids', type=str, required=True, help="Camera MX ID.")
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

    while True:
        for port, subscriber in zip(ports, subscribers):
            try:
                message = pickle.loads(subscriber.recv(zmq.NOBLOCK))
                file_color, file_monoL, file_monoR, file_imus = files_dict[port]

                file_color.write(message["color"])
                file_monoL.write(message["monoL"])
                file_monoR.write(message["monoR"])
                depth_file_name = f"depth_{message['camera_id']}/" + str(message['depth']['sequence']) + f"_{str(message['depth']['timestamp'])}.png"
                # depth_file_name = f'depth_{message['camera_id']}/' + str(message['depth']['sequence']) + f"_{str(message['depth']['timestamp'])}.png"
                # os.makedirs(os.path.join(args.out, f'depth_{message['camera_id']}_{port}'), exist_ok=True)
                cv2.imwrite(os.path.join(args.out, depth_file_name), message['depth']['frame'])
                
                file_imus.write((str(message['imu']) + '\n').encode())
            except zmq.Again:
                pass

if __name__ == "__main__":
    main()
