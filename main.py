import sys
import gi
import time
import json

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib

loop = GLib.MainLoop()
Gst.init(None)

PORT = 8554
LATENCY_DEFAULT = 250


class CustomRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, launch_string):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.launch_string = launch_string
        print("is_stop_on_disonnect", self.is_stop_on_disonnect())
        #print(self.launch_string)

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)


class GstreamerRtspServer():
    def __init__(self):
        self.rtspServer = GstRtspServer.RTSPServer()
        self.rtspServer.set_service(str(PORT))

    @staticmethod
    def build_rtsp_pipeline(cam):
        pipeline_str = "rtspsrc location=" + cam['url']
        if "username" in cam and "password" in cam \
                and cam['username'] is not None and cam['password'] is not None:
            pipeline_str = pipeline_str + " user-id=" + cam['username'] + " user-pw=" + cam['password']
        if "latency" in cam:
            latency = cam['latency']
        else:
            latency = LATENCY_DEFAULT
        #pipeline_str = pipeline_str + " latency=" + str(latency) + " drop-on-latency=true udp-reconnect=true" \
        #           + "! queue ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 "
        pipeline_str = pipeline_str + " latency=" + str(latency) + " " \
                   + "! queue ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 "
        return pipeline_str

    def add_source(self, cam):
        mount_points = self.rtspServer.get_mount_points()
        if cam['streamType'] == "rtsp":
            pipeline_str = self.build_rtsp_pipeline(cam)
            factory = CustomRtspMediaFactory(pipeline_str)
            factory.set_shared(True)
            factory.set_stop_on_disconnect(False)
            mount_points.add_factory("/" + cam['name'], factory)
        # elif cam['streamType'] == "simulation":
        #     factory = GstRtspServer.RTSPMediaFactory.new()
        #     factory.set_launch("videotestsrc ! videoconvert ! theoraenc ! queue ! rtptheorapay name=pay0")
        #     mount_points.add_factory("/" + cam['name'], factory)

    def start(self):
        mount_points = self.rtspServer.get_mount_points()
        f = open('cameras.json', )
        cameras = json.load(f)
        for cam in cameras:
            self.add_source(cam)
        self.rtspServer.attach(None)
        f.close()


if __name__ == '__main__':
    s = GstreamerRtspServer()
    s.start()
    loop.run()
    # test()