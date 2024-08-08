import depthai as dai

def record_video(cameras, output_file):
    pipeline = dai.Pipeline()

    camera_nodes = {}
    encoders = {}

    if 'left' in cameras:
        mono_left = pipeline.create(dai.node.MonoCamera)
        mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        encoder_left = pipeline.create(dai.node.VideoEncoder)
        encoder_left.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H265_MAIN)
        mono_left.out.link(encoder_left.input)
        camera_nodes['left'] = encoder_left

    if 'right' in cameras:
        mono_right = pipeline.create(dai.node.MonoCamera)
        mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        encoder_right = pipeline.create(dai.node.VideoEncoder)
        encoder_right.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H265_MAIN)
        mono_right.out.link(encoder_right.input)
        camera_nodes['right'] = encoder_right

    if 'rgb' in cameras:
        color_cam = pipeline.create(dai.node.ColorCamera)
        encoder_rgb = pipeline.create(dai.node.VideoEncoder)
        encoder_rgb.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H265_MAIN)
        color_cam.video.link(encoder_rgb.input)
        camera_nodes['rgb'] = encoder_rgb

    with dai.Device(pipeline) as device:
        for cam, encoder in camera_nodes.items():
            with open(f"{output_file}_{cam}.h265", "wb") as file:
                while True:
                    packets = device.getOutputQueue(encoder.getName(), 8, blocking=True).tryGetAll()
                    for packet in packets:
                        file.write(packet.getData())
