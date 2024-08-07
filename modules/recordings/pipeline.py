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