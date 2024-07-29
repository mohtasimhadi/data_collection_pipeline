import argparse
from publishers.depthai import DepthAIPublisher

def func():
    parser = argparse.ArgumentParser(description="DepthAI Camera Info Parser")
    parser.add_argument('--mxid', type=str, required=True, help="Camera MX ID")
    parser.add_argument('--port_no', type=str, required=True, help="Publisher Port No")

    args = parser.parse_args()
    print(f'Camera ID: {args.mxid}')
    print(f'Port No  : {args.port_no}')

    publisher = DepthAIPublisher(port_no=args.port_no, camera_id=args.mxid)
    publisher.publish()

if __name__ == "__main__":
    func()