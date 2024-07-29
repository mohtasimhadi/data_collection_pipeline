import os, json
import depthai as dai

def get_mono_pipeline(pipeline, camera):
    mono_pipeline = pipeline.create(dai.node.MonoCamera)
    mono_pipeline.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
    mono_pipeline.setBoardSocket(camera)
    return mono_pipeline

def get_depth_pipeline(pipeline, monoL_pipeline, monoR_pipeline):
    depth_pipeline = pipeline.create(dai.node.StereoDepth)
    depth_pipeline.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    depth_pipeline.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
    depth_pipeline.setLeftRightCheck(True)
    depth_pipeline.setExtendedDisparity(False)
    depth_pipeline.setSubpixel(False)
    monoL_pipeline.out.link(depth_pipeline.left)
    monoR_pipeline.out.link(depth_pipeline.right)
    depth_pipeline.setDepthAlign(dai.CameraBoardSocket.CAM_A)
    return depth_pipeline

def get_color_pipeline(pipeline):
    color_pipeline = pipeline.create(dai.node.ColorCamera)
    color_pipeline.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    color_pipeline.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    color_pipeline.setFps(30)
    return color_pipeline

def get_imu_pipeline(pipeline):
    return pipeline.create(dai.node.IMU)

def set_depth_xout(pipeline, depth_pipeline):
    xout_depth = pipeline.create(dai.node.XLinkOut)
    xout_depth.setStreamName("depth")
    depth_pipeline.depth.link(xout_depth.input)

def get_xout(pipeline, stream_name):
    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName(stream_name)
    return xout

def get_encoder(pipeline, encoder_property):
    encoder = pipeline.create(dai.node.VideoEncoder)
    encoder.setDefaultProfilePreset(30, encoder_property)
    return encoder

def get_queues(device):
    queues = []
    queues.append(device.getOutputQueue(name="depth", maxSize=30, blocking=True))
    queues.append(device.getOutputQueue(name="color", maxSize=30, blocking=True))
    queues.append(device.getOutputQueue(name="monoL", maxSize=30, blocking=True))
    queues.append(device.getOutputQueue(name="monoR", maxSize=30, blocking=True))
    imu_queue = device.getOutputQueue(name='imu', maxSize=30, blocking=True)
    return queues, imu_queue

def get_files(output_dir, thread):
    file_color = open(os.path.join(output_dir, f'{thread}_color.h265'), 'wb')
    file_monoL = open(os.path.join(output_dir, f'{thread}_monoL.h264'), 'wb')
    file_monoR = open(os.path.join(output_dir, f'{thread}_monoR.h264'), 'wb')
    file_imus = open(os.path.join(output_dir, f'{thread}_imu_data.txt'), 'wb')

    return file_color, file_monoL, file_monoR, file_imus

def imu_data_processing(imu_message):
    for imu_packet in imu_message.packets:
        acceleroValues = imu_packet.acceleroMeter
        gyroValues = imu_packet.gyroscope
        acceleroTs = acceleroValues.getTimestampDevice()
        gyroTs = gyroValues.getTimestampDevice()

    return {
            "acceleroMeter" : {
                "x": acceleroValues.x,
                "y": acceleroValues.y,
                "z": acceleroValues.z,
                "timestamp": acceleroTs
            },
            "gyroscope"     : {
                "x": gyroValues.x,
                "y": gyroValues.y,
                "z": gyroValues.z,
                "timestamp": gyroTs
            }
        }