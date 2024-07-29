import os
import cv2
import pickle
import zmq
from modules.depthai.utils import get_files

def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5555")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    file_color, file_monoL, file_monoR, file_imus = get_files("out", "thread")

    while True:
        print("Dhukse!")
        message = pickle.loads(subscriber.recv())
        file_color.write(message["color"])
        file_monoL.write(message["monoL"])
        file_monoR.write(message["monoR"])
        depth_file_name = f'{"thread"}_depth/' +str(message['depth']['sequence']) + f"_{str(message['depth']['timestamp'])}.png"
        cv2.imwrite(os.path.join("out", depth_file_name), message['depth']['frame'])


if __name__ == "__main__":
    main()
