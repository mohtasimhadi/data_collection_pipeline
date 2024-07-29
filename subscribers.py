import os, cv2, pickle, zmq, argparse
from modules.depthai.utils import get_files

def main():
    parser = argparse.ArgumentParser(description="Data Collection Subscriber")
    parser.add_argument('--port_no', type=str, required=True, help="Publisher port no")
    parser.add_argument('--out', type=str, required=True, help="Output directory.")
    parser.add_argument('--mxid', type=str, required=True, help="Camer MX ID.")
    args = parser.parse_args()

    print(f'Camera ID         : {args.mxid}')
    print(f'Port No           : {args.port_no}')
    print(f'Press Ctl+C to stop subscriber...')

    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{args.port_no}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    file_color, file_monoL, file_monoR, file_imus = get_files(args.out, args.mxid)

    while True:
        message = pickle.loads(subscriber.recv())
        file_color.write(message["color"])
        file_monoL.write(message["monoL"])
        file_monoR.write(message["monoR"])
        depth_file_name = f'depth_{args.mxid}/' +str(message['depth']['sequence']) + f"_{str(message['depth']['timestamp'])}.png"
        cv2.imwrite(os.path.join(args.out, depth_file_name), message['depth']['frame'])
        file_imus.write(str(message['imu']).encode())


if __name__ == "__main__":
    main()
