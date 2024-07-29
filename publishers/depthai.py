import pickle, zmq
from modules.depthai.utils import *
from modules.depthai.hostsync import HostSync

class DepthAIPublisher():
    def __init__(self, camera_id, port_no = 5000) -> None:
        self.camera_id = camera_id
        self.create_pipeline()
        self.create_publisher(port_no)

    def create_pipeline(self):
        pipeline = dai.Pipeline()

        monoL_pipeline = get_mono_pipeline(pipeline, dai.CameraBoardSocket.CAM_B)
        monoR_pipeline = get_mono_pipeline(pipeline, dai.CameraBoardSocket.CAM_C)
        depth_pipeline = get_depth_pipeline(pipeline, monoL_pipeline, monoR_pipeline)
        color_pipeline = get_color_pipeline(pipeline)
        imu_pipeline   = get_imu_pipeline(pipeline)

        color_encoder = get_encoder(pipeline, dai.VideoEncoderProperties.Profile.H265_MAIN)
        monoL_encoder = get_encoder(pipeline, dai.VideoEncoderProperties.Profile.H264_MAIN)
        monoR_encoder = get_encoder(pipeline, dai.VideoEncoderProperties.Profile.H264_MAIN)

        color_pipeline.video.link(color_encoder.input)
        monoL_pipeline.out.link(monoL_encoder.input)
        monoR_pipeline.out.link(monoR_encoder.input)

        set_depth_xout(pipeline, depth_pipeline)
        xout_color = get_xout(pipeline, 'color')
        xout_monoL = get_xout(pipeline, 'monoL')
        xout_monoR = get_xout(pipeline, 'monoR')
        xout_imu   = get_xout(pipeline, 'imu')

        color_encoder.bitstream.link(xout_color.input)
        monoL_encoder.bitstream.link(xout_monoL.input)
        monoR_encoder.bitstream.link(xout_monoR.input)

        imu_pipeline.enableIMUSensor([dai.IMUSensor.ACCELEROMETER_RAW, dai.IMUSensor.GYROSCOPE_RAW], 120)
        imu_pipeline.setBatchReportThreshold(1)
        imu_pipeline.setMaxBatchReports(30)
        imu_pipeline.out.link(xout_imu.input)

        self.pipeline = pipeline

    
    def create_publisher(self, port_no):
        self.publisher = zmq.Context().socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{port_no}")

    def publish(self):
        with dai.Device(self.pipeline, self.camera_id) as device:
            queues, imu_queue = get_queues(device)
            sync = HostSync()
            print("Publisher started...")
            while True:
                for queue in queues:
                    message = sync.add_msg(queue.getName(), queue.get())
                    if message:
                        
                        buffer = pickle.dumps({
                            "color": message['color'].getData(),
                            "monoL": message['monoL'].getData(),
                            "monoR": message['monoR'].getData(),
                            "depth": {
                                "frame":     message['depth'].getFrame(),
                                "timestamp": message['depth'].getTimestampDevice(),
                                "sequence":  message['depth'].getSequenceNum()
                                },
                            "imu"  : imu_data_processing(imu_queue.get())
                        })
                        self.publisher.send(buffer)