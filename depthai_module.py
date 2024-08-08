import depthai as dai
import os
import time
import cv2

class DepthAIModule:
    def __init__(self, cameras, output_folder="output"):
        self.cameras = cameras
        self.devices = dai.Device.getAllAvailableDevices()
        self.output_folder = output_folder

        if len(self.devices) == 0:
            raise RuntimeError("No DepthAI devices found!")

        os.makedirs(self.output_folder, exist_ok=True)

    def create_pipeline(self):
        pipeline = dai.Pipeline()
        camera_nodes = {}

        if 'left' in self.cameras:
            mono_left = pipeline.create(dai.node.MonoCamera)
            mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
            xout_left = pipeline.create(dai.node.XLinkOut)
            xout_left.setStreamName("left")
            mono_left.out.link(xout_left.input)
            camera_nodes['left'] = xout_left

        if 'right' in self.cameras:
            mono_right = pipeline.create(dai.node.MonoCamera)
            mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
            xout_right = pipeline.create(dai.node.XLinkOut)
            xout_right.setStreamName("right")
            mono_right.out.link(xout_right.input)
            camera_nodes['right'] = xout_right

        if 'rgb' in self.cameras:
            color_cam = pipeline.create(dai.node.ColorCamera)
            xout_rgb = pipeline.create(dai.node.XLinkOut)
            xout_rgb.setStreamName("rgb")
            color_cam.video.link(xout_rgb.input)
            camera_nodes['rgb'] = xout_rgb

        return pipeline, camera_nodes

    def record_video(self, output_folder=None):
        if output_folder is None:
            output_folder = self.output_folder

        start_time = int(time.time())

        for device_info in self.devices:
            pipeline, camera_nodes = self.create_pipeline()

            with dai.Device(pipeline, device_info) as device:
                recording_folder = os.path.join(output_folder, f"recording_{device_info.getMxId()}_{start_time}")
                os.makedirs(recording_folder, exist_ok=True)

                file_handlers = {}
                for cam, xout in camera_nodes.items():
                    file_name = f"{device_info.getMxId()}_{cam}_{start_time}_"
                    file_handlers[cam] = open(os.path.join(recording_folder, f"{file_name}.h265"), "wb")

                try:
                    queues = {cam: device.getOutputQueue(name.getStreamName(), 8, blocking=True) for cam, name in camera_nodes.items()}
                    while True:
                        for cam, queue in queues.items():
                            packet = queue.tryGet()
                            if packet is not None:
                                file_handlers[cam].write(packet.getData())
                except KeyboardInterrupt:
                    stop_time = int(time.time())

                    for cam, handler in file_handlers.items():
                        handler.close()

                    for cam in file_handlers:
                        old_name = os.path.join(recording_folder, f"{device_info.getMxId()}_{cam}_{start_time}_.h265")
                        new_name = os.path.join(recording_folder, f"{device_info.getMxId()}_{cam}_{start_time}_{stop_time}.h265")
                        os.rename(old_name, new_name)

                    print(f"Recording stopped. Files saved in {recording_folder}")

    def live_stream(self):
        pipelines = {}
        queues = {}

        for device_info in self.devices:
            pipeline = dai.Pipeline()
            camera_nodes = {}

            if 'left' in self.cameras:
                mono_left = pipeline.create(dai.node.MonoCamera)
                mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
                xout_left = pipeline.create(dai.node.XLinkOut)
                xout_left.setStreamName("left")
                mono_left.out.link(xout_left.input)
                camera_nodes['left'] = xout_left

            if 'right' in self.cameras:
                mono_right = pipeline.create(dai.node.MonoCamera)
                mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
                xout_right = pipeline.create(dai.node.XLinkOut)
                xout_right.setStreamName("right")
                mono_right.out.link(xout_right.input)
                camera_nodes['right'] = xout_right

            if 'rgb' in self.cameras:
                color_cam = pipeline.create(dai.node.ColorCamera)
                xout_rgb = pipeline.create(dai.node.XLinkOut)
                xout_rgb.setStreamName("rgb")
                color_cam.video.link(xout_rgb.input)
                camera_nodes['rgb'] = xout_rgb

            device = dai.Device(pipeline, device_info)
            pipelines[device_info.getMxId()] = device
            queues[device_info.getMxId()] = {cam: device.getOutputQueue(name.getStreamName(), 8, blocking=False) for cam, name in camera_nodes.items()}

        try:
            while True:
                for device_id, device_queues in queues.items():
                    for cam, queue in device_queues.items():
                        frame = queue.tryGet()
                        if frame is not None:
                            cv2.imshow(f"{device_id} - {cam} Camera", frame.getCvFrame())

                if cv2.waitKey(1) == ord('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            for device in pipelines.values():
                device.close()

            cv2.destroyAllWindows()
