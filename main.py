import os
import time
import argparse
import depthai as dai
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Data Collection Executionar")
    parser.add_argument('--port_no', type=int, default=5500, help="Initial Publisher Port")
    parser.add_argument('--out', type=str, default="out", help="Output directory")
    args = parser.parse_args()

    devices = dai.Device.getAllAvailableDevices()

    if len(devices) == 0:
        print("No camera connected!")
    else:
        print(f"{len(devices)} camera(s) connected.")

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    port_no = args.port_no
    for device in devices:
        if not os.path.exists(args.out+'/depth_'+device.mxid):
            os.makedirs(args.out+'/depth_'+device.mxid)
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 depthai_cam.py --out {args.out} --port_no {port_no} --mxid {device.mxid}; exec bash'])
        port_no += 1

    time.sleep(15)
    port_no = args.port_no
    for device in devices:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 subscribers.py --out {args.out} --port_no {port_no} --mxid {device.mxid}; exec bash'])
        port_no += 1


if __name__ == "__main__":
    main()