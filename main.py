import depthai as dai
import subprocess

def main():
    devices = dai.Device.getAllAvailableDevices()
    port_no = 5500
    for device in devices:
        print("Connected cameras:", device.mxid)
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 depthai_cam.py --mxid {device.mxid} --port_no {port_no}; exec bash'])
        port_no += 1

if __name__ == "__main__":
    main()