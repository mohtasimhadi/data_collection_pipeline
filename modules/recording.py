import cv2
import os
import time
import argparse
import threading
import depthai as dai
from modules.recordings import *
from utils.host_sync import HostSync
from utils.general_helper import save_calibration, get_queues, get_files, write_imu

def initiate_pipeline(thread, output_dir):
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

    os.makedirs(output_dir+f'/{thread}_depth')
    with dai.Device(pipeline) as device:
        queues, imu_queue = get_queues(device)
        sync = HostSync()
        save_calibration(device.readCalibration(), output_dir, thread)
        file_color, file_monoL, file_monoR, file_imus = get_files(output_dir, thread)
        print(f'{thread} started...')
        try:
            while True:
                write_imu(imu_queue.get(), file_imus)
                for queue in queues:
                    new_message = queue.get()
                    message = sync.add_msg(queue.getName(), new_message)
                    if message:
                        file_color.write(message['color'].getData())
                        file_monoL.write(message['monoL'].getData())
                        file_monoR.write(message['monoR'].getData())
                        depth_file_name = f'{thread}_depth/' +str(message['depth'].getSequenceNum()) + f"_{str(message['depth'].getTimestampDevice())}.png"
                        cv2.imwrite(os.path.join(output_dir, depth_file_name), message['depth'].getFrame())
        except KeyboardInterrupt:
            pass

def start_recording(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    thread_01 = threading.Thread(target=initiate_pipeline, args=('thread_01', output_dir))
    thread_02 = threading.Thread(target=initiate_pipeline, args=('thread_02', output_dir))
    thread_01.start()
    time.sleep(2)
    thread_02.start()
    
    thread_01.join()
    thread_02.join()

    print("All recordings stopped.")