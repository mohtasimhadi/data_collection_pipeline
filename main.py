from publishers.depthai import DepthAIPublisher

publisher = DepthAIPublisher(port_no=5555)
publisher.publish()