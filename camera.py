import cv2 as cv
import numpy as np
import datetime

class SimVideo():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    def __init__(self, port=5600):
        self.Gst.init(None)
        self.port = port
        self._frame = None
        self.video_source = 'udpsrc port={}'.format(self.port)
        self.video_codec = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        self.video_decode = \
            '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        self.video_sink_conf = \
            '! appsink emit-signals=true sync=false max-buffers=2 drop=true'
        self.video_pipe = None
        self.video_sink = None

        self.run()

    def start_gst(self, config=None):
        if not config:
            config = \
                [
                    'videotestsrc ! decodebin',
                    '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                    '! appsink'
                ]
        command = ' '.join(config)
        self.video_pipe = self.Gst.parse_launch(command)
        self.video_pipe.set_state(self.Gst.State.PLAYING)
        self.video_sink = self.video_pipe.get_by_name('appsink0')

    @staticmethod
    def gst_to_opencv(sample):
        buf = sample.get_buffer()
        caps = sample.get_caps()
        array = np.ndarray(
            (
                caps.get_structure(0).get_value('height'),
                caps.get_structure(0).get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def frame(self):
        return self._frame

    def frame_available(self):
        return type(self._frame) != type(None)

    def run(self):
        self.start_gst(
            [
                self.video_source,
                self.video_codec,
                self.video_decode,
                self.video_sink_conf
            ])
        self.video_sink.connect('new-sample', self.callback)

    def callback(self, sink):
        sample = sink.emit('pull-sample')
        new_frame = self.gst_to_opencv(sample)
        self._frame = new_frame
        return self.Gst.FlowReturn.OK

def view_camera_video(child_conn, config):
    img = np.zeros([config.vision.width, config.vision.height, 3],dtype=np.uint8)
    img.fill(255)
    if config.sim:
        video = SimVideo()
        while True:
            if not video.frame_available():
                continue
            frame = video.frame()
            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        #     img = cv.cvtColor(np.array(img)[600:1000, 1500:1900], cv.COLOR_BGRA2RGB)
        #     results = model(img, verbose=False)
        #     sent = False
        #     for result in results:
        #         #some sorting logic
        #         for r in result.boxes.data.tolist():
        #             x1, y1, x2, y2, score, class_id = r
        #             if score > 0.30 and int(class_id) == 0 and not sent:
        #                 child_conn.send([x1, y1, x2, y2, img])
        #                 sent = True
        #     if not sent: child_conn.send([0, 0, 0, 0, img])

    else:
        import jetson_interface
        import jetson_utils
        model = jetson_interface.detectNet(config.vision.model, threshold=0.5)
        camera = jetson_utils.gstCamera(config.vision.width, config.vision.height, config.vision.camera_address)
        while True:
            img, width, height = camera.CaptureRGBA()
            aimg = jetson_utils.cudaToNumpy(img, width, height, 4)
            frame = cv.cvtColor(aimg.astype(np.uint8), cv.COLOR_RGBA2BGR)
            detections = model.Detect(img, width, height)
            sent = False
            if len(detections) > 0:
                #some sorting logic
                for d in detections:
                    if d.ClassID == 1 and not sent:
                        child_conn.send([int(d.Left), int(d.Top), int(d.Right), int(d.Bottom), frame])
                        sent = True
            if not sent: child_conn.send([0, 0, 0, 0, frame])
