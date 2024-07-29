import argparse
import time
import depthai as dai
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Data Collection Executionar")
    parser.add_argument('--port_no', type=str, required=True, help="Initial Publisher Port")
    parser.add_argument('--out', type=str, required=True, help="Output Directory")
    args = parser.parse_args()

    devices = dai.Device.getAllAvailableDevices()

    if len(devices) == 0:
        print("No camera connected!")
    else:
        print(f"{len(devices)} camera(s) connected.")

    port_no = args.port_no

    for device in devices:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 depthai_cam.py --mxid {device.mxid} --port_no {port_no}; exec bash'])
        port_no += 1

    time.sleep(15)
    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 subscribers.py --port_no {port_no} --device_count {len(devices)}; exec bash'])


if __name__ == "__main__":
    main()