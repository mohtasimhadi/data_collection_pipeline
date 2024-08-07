import depthai as dai
import cv2

# Function to create a pipeline for a specific device
def create_pipeline():
    pipeline = dai.Pipeline()

    # Color camera node
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.setFps(30)

    # Create output stream
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("rgb")
    cam_rgb.video.link(xout_rgb.input)

    return pipeline

# List of available devices
device_infos = dai.Device.getAllAvailableDevices()

if len(device_infos) < 2:
    print("You need at least two DepthAI devices connected")
else:
    # Create pipelines and devices
    pipeline1 = create_pipeline()
    pipeline2 = create_pipeline()

    with dai.Device(pipeline1, device_infos[0]) as device1, dai.Device(pipeline2, device_infos[1]) as device2:
        q_rgb1 = device1.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        q_rgb2 = device2.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            in_rgb1 = q_rgb1.tryGet()
            in_rgb2 = q_rgb2.tryGet()

            if in_rgb1 is not None:
                cv2.imshow("RGB Camera 1", in_rgb1.getCvFrame())
            
            if in_rgb2 is not None:
                cv2.imshow("RGB Camera 2", in_rgb2.getCvFrame())

            if cv2.waitKey(1) == ord('q'):
                break

cv2.destroyAllWindows()
