import depthai as dai
import cv2

def live_stream(cameras):
    pipeline = dai.Pipeline()

    camera_nodes = {}

    if 'left' in cameras:
        mono_left = pipeline.create(dai.node.MonoCamera)
        mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        xout_left = pipeline.create(dai.node.XLinkOut)
        xout_left.setStreamName("left")
        mono_left.out.link(xout_left.input)
        camera_nodes['left'] = "left"

    if 'right' in cameras:
        mono_right = pipeline.create(dai.node.MonoCamera)
        mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        xout_right = pipeline.create(dai.node.XLinkOut)
        xout_right.setStreamName("right")
        mono_right.out.link(xout_right.input)
        camera_nodes['right'] = "right"

    if 'rgb' in cameras:
        color_cam = pipeline.create(dai.node.ColorCamera)
        xout_rgb = pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        color_cam.video.link(xout_rgb.input)
        camera_nodes['rgb'] = "rgb"

    with dai.Device(pipeline) as device:
        queues = {cam: device.getOutputQueue(name, 8, blocking=False) for cam, name in camera_nodes.items()}
        
        while True:
            for cam, queue in queues.items():
                frame = queue.tryGet()
                if frame is not None:
                    cv2.imshow(f"{cam} Camera", frame.getCvFrame())
            
            if cv2.waitKey(1) == ord('q'):
                break

    cv2.destroyAllWindows()
