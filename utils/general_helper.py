import os, json
import depthai as dai

def get_queues(device):
    queues = []
    queues.append(device.getOutputQueue(name="depth", maxSize=30, blocking=True))
    queues.append(device.getOutputQueue(name="color", maxSize=30, blocking=True))
    queues.append(device.getOutputQueue(name="monoL", maxSize=30, blocking=True))
    queues.append(device.getOutputQueue(name="monoR", maxSize=30, blocking=True))
    imu_queue = device.getOutputQueue(name='imu', maxSize=30, blocking=True)
    return queues, imu_queue


def save_calibration(calibData, output_dir, thread):
    calib_dict = {
        'left_intrinsics'           : calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_B, dai.Size2f(1080, 720)),
        'right_intrinsics'          : calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_C, dai.Size2f(1080, 720)),
        'rgb_intrinsics'            : calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A, dai.Size2f(1920, 1080)),
        'left_distortion'           : calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_B),
        'right_distortion'          : calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_C),
        'rgb_distortion'            : calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_A),
        'extrinsics_left_to_right'  : calibData.getCameraExtrinsics(dai.CameraBoardSocket.CAM_B, dai.CameraBoardSocket.CAM_C),
        'extrinsics_right_to_left'  : calibData.getCameraExtrinsics(dai.CameraBoardSocket.CAM_C, dai.CameraBoardSocket.CAM_B),
        'extrinsics_left_to_rgb'    : calibData.getCameraExtrinsics(dai.CameraBoardSocket.CAM_B, dai.CameraBoardSocket.CAM_A),
        'extrinsics_right_to_rgb'   : calibData.getCameraExtrinsics(dai.CameraBoardSocket.CAM_C, dai.CameraBoardSocket.CAM_A)
    }
    file_calibration = os.path.join(output_dir, f'{thread}_calibration.json')
    with open(file_calibration, 'w') as f:
        json.dump(calib_dict, f, indent=4)

def get_files(output_dir, thread):
    file_color = open(os.path.join(output_dir, f'{thread}_color.h265'), 'wb')
    file_monoL = open(os.path.join(output_dir, f'{thread}_monoL.h264'), 'wb')
    file_monoR = open(os.path.join(output_dir, f'{thread}_monoR.h264'), 'wb')
    file_imus = open(os.path.join(output_dir, f'{thread}_imu_data.txt'), 'wb')

    return file_color, file_monoL, file_monoR, file_imus

def write_imu(imu_message, file_imus):
    for imu_packet in imu_message.packets:
        acceleroValues = imu_packet.acceleroMeter
        gyroValues = imu_packet.gyroscope
        acceleroTs = acceleroValues.getTimestampDevice()
        gyroTs = gyroValues.getTimestampDevice()

        imu_data = {
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
        file_imus.write(("{'imu_timestamp': '" + str(imu_message.getTimestampDevice()) + "',    'IMU': " + str(imu_data) + '\n').encode())