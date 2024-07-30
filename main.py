import os
import time
import argparse
import depthai as dai
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Data Collection Executionar")
    parser.add_argument('--port_no', type=int, default=5500, help="Initial Publisher Port")
    parser.add_argument('--out', type=str, default="out", help="Output directory")
    parser.add_argument('--gps', type=bool, default=False, help="If GPS data to be collected")
    args = parser.parse_args()

    devices = dai.Device.getAllAvailableDevices()

    if len(devices) == 0:
        print("No camera connected!")
    else:
        print(f"{len(devices)} camera(s) connected.")

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    port_no = args.port_no
    ports = []
    mxids = []
    for device in devices:
        ports.append(str(port_no))
        mxids.append(str(device.mxid))
        if not os.path.exists(args.out+'/depth_'+device.mxid):
            os.makedirs(args.out+'/depth_'+device.mxid)
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 depthai_cam.py --out {args.out} --port_no {port_no} --mxid {device.mxid}; exec bash'])
        port_no += 1
    if args.gps:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 gps.py; exec bash'])
    ports = ','.join(map(str, ports))
    mxids = ','.join(map(str, mxids))
    time.sleep(5)
    if args.gps:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 test.py --out {args.out} --port_nos {ports} --mxids {mxids} --gps true; exec bash'])
    else:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 subscriber.py --out {args.out} --port_nos {ports} --mxids {mxids}; exec bash'])

if __name__ == "__main__":
    main()