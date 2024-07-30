import csv
import zmq
import pickle

class GPSSubscriber:
    def __init__(self, port='5555', out='out'):
        self.csv_filename = out+'/gnrmc_data.csv'
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f'tcp://localhost:{port}')
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
    
    def receive_data(self):
        with open(self.csv_filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Timestamp', 'GNRMC Data'])

        while True:
            serialized_data = self.subscriber.recv()
            data = pickle.loads(serialized_data)
            print(f'Received data: {(data)}')

    def close(self):
        self.subscriber.close()
        self.context.term()

if __name__ == "__main__":
    gps_subscriber = GPSSubscriber()
    try:
        gps_subscriber.receive_data()
    except KeyboardInterrupt:
        gps_subscriber.close()
