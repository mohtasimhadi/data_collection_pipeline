import depthai as dai

def get_encoder(pipeline, encoder_property):
    encoder = pipeline.create(dai.node.VideoEncoder)
    encoder.setDefaultProfilePreset(30, encoder_property)
    return encoder