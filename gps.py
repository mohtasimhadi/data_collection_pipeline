from publishers.gps import GPSPublisher

def main():
    gps_publisher = GPSPublisher()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        gps_publisher.close()

if __name__ == '__main__':
    main()