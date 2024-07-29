import os, cv2, pickle, zmq, argparse
from modules.depthai.utils import get_files

def main():
    parser = argparse.ArgumentParser(description="Data Collection Subscriber")
    # parser.add_argument('--device_count', type=int, required=True, help="Number of Camera")
    parser.add_argument('--port_no', type=str, required=True, help="Publisher Port No")
    args = parser.parse_args()

    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{args.port_no}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    file_color, file_monoL, file_monoR, file_imus = get_files("out", "thread")

    while True:
        message = pickle.loads(subscriber.recv())
        file_color.write(message["color"])
        file_monoL.write(message["monoL"])
        file_monoR.write(message["monoR"])
        depth_file_name = f'depth/' +str(message['depth']['sequence']) + f"_{str(message['depth']['timestamp'])}.png"
        cv2.imwrite(os.path.join("out", depth_file_name), message['depth']['frame'])
        file_imus.write((str(message['imu']) + "\n").encode())


if __name__ == "__main__":
    main()
