import argparse
from record import record_video
from stream import live_stream
from extract_frames import extract_frames_from_video

def main():
    parser = argparse.ArgumentParser(description="DepthAI Camera Operations")
    parser.add_argument('operation', choices=['record', 'stream', 'extract'], help="Operation to perform: record, stream, extract")
    parser.add_argument('--cameras', nargs='+', choices=['left', 'right', 'rgb'], help="Cameras to use: left, right, rgb")
    parser.add_argument('--output', type=str, help="Output file for recording or extracting frames")
    parser.add_argument('--input', type=str, help="Input file for extracting frames")

    args = parser.parse_args()

    if args.operation == 'record':
        record_video(args.cameras, args.output)
    elif args.operation == 'stream':
        live_stream(args.cameras)
    elif args.operation == 'extract':
        extract_frames_from_video(args.input, args.output)

if __name__ == "__main__":
    main()
