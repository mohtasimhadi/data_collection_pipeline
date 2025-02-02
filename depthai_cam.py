import argparse
from publishers.depthai import DepthAIPublisher

def main():
    parser = argparse.ArgumentParser(description="DepthAI Camera Info Parser")
    parser.add_argument('--mxid', type=str, required=True, help="Camera MX ID")
    parser.add_argument('--port_no', type=str, required=True, help="Publisher Port No")
    parser.add_argument('--out', type=str, default="out", help="Output directory")

    args = parser.parse_args()
    print(f'Camera ID: {args.mxid}')
    print(f'Port No  : {args.port_no}')

    publisher = DepthAIPublisher(port_no=args.port_no, camera_id=args.mxid, output_dir=args.out)
    publisher.publish()

if __name__ == "__main__":
    main()