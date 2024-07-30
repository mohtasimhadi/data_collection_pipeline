import argparse
from publishers.gps import GPSPublisher

def main():
    parser = argparse.ArgumentParser(description="GPS Data Publisher")
    parser.add_argument('--port', type=str, default='6000', help="Publisher Port No")
    args = parser.parse_args()
    gps = GPSPublisher(port=args.port)
    gps.read_serial()

if __name__ == '__main__':
    main()