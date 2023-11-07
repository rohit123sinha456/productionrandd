import cv2
import time
import logging
import numpy as np
import os
import threading
import uuid
import ffmpeg
import json
import multiprocessing as mp
from test_infer import Infer
from api_post import API
# rtsp_url = "rtsp://admin:Sheraton123@10.111.111.215:554/Streaming/Channels/101/"
# out_filename = "test.mp4"
# probe = ffmpeg.probe(rtsp_url)
# cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
# print("fps: {}".format(cap_info['r_frame_rate']))
# width = cap_info['width']          
# height = cap_info['height']
# process1 = (
#     ffmpeg
#     .input(rtsp_url)
#     .output('pipe:', format='rawvideo', pix_fmt='rgb24')
#     .run_async(pipe_stdout=True)
# )

# process2 = (
#     ffmpeg
#     .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(width, height))
#     .output(out_filename, pix_fmt='yuv420p')
#     .overwrite_output()
#     .run_async(pipe_stdin=True)
# )

# while True:
#     in_bytes = process1.stdout.read(width * height * 3)
#     if not in_bytes:
#         break
#     in_frame = (
#         np
#         .frombuffer(in_bytes, np.uint8)
#         .reshape([height, width, 3])
#     )
#     out_frame = in_frame * 0.3
#     process2.stdin.write(
#         out_frame
#         .astype(np.uint8)
#         .tobytes()
#     )

# process2.stdin.close()
# process1.wait()
# process2.wait()




































































class TESTFFMPEGC():
    def __init__(self):
        self.logger = logging.getLogger('app.FFMPEGC')
        #self.camera_config = camera_config
        self.rtsp_url = "rtsp://admin:Sheraton123@10.111.111.215:554/Streaming/Channels/101/"#camera_config['rtsp_url']
        self.img_folder = "Camera10"#camera_config['camera']
        self.inferob = Infer()
        self.api = API()
        self.args = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer",
        "flags": "low_delay"}
        try:
            print("Begin Probing RTSP Stream for camera :- {}".format(self.rtsp_url))
            print("Begin Probing RTSP Stream with url :- {}".format(self.img_folder))
            probe = ffmpeg.probe(self.rtsp_url)
            cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
            print("fps: {}".format(cap_info['r_frame_rate']))
            self.width = cap_info['width']          
            self.height = cap_info['height']
            print(self.width,self.height)
            up, down = str(cap_info['r_frame_rate']).split('/')
            fps = eval(up) / eval(down)
            print("fps: {}".format(fps))   
        except Exception as e:
            self.logger.error("Failed to Probe RTSP Stream")
            self.logger.error(e)
            raise e
        
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)

    def enqueue_frame_buffer(self):
        self.process1 = (
            ffmpeg
            .input(self.rtsp_url, **self.args)
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .overwrite_output()
            .run_async(pipe_stdout=True)
        )
        
        while True:
            try:
                in_bytes = self.process1.stdout.read(self.width * self.height * 3)   
                if not in_bytes:
                    print("Some Issue with reading from STDOUT")
                    break
                
                Frame = (
                    np
                    .frombuffer(in_bytes, np.uint8)
                    .reshape([self.height, self.width, 3])
                )
                if Frame is not None:
                    dets = self.inferob.detection(Frame)
                    frames = self.inferob.tracking(Frame,dets)
                    i = uuid.uuid4()
                    fnmae = "frame" + str(i) + '.jpg'
                    frame_name = os.path.join('.', self.img_folder, fnmae)

                    if(frames is not None):
                        self.logger.info("Saving Image to Local Storage")
                        cv2.imwrite(frame_name,frames)
                        try:
                            self.api.posting(frame_name,self.camera_config)
                            self.logger.info("Image Successfully Sent to Server")
                        except Exception as e:
                            self.logger.error("Failed to Send Image to Server")
                            self.logger.error(e)


            except Exception as e:
                self.logger.error("Problem with Processing")
                self.logger.error(e)
        self.process1.wait()
    def run_threads(self):
        print("running threads")
        # self.enqueue_frame_buffer()
        self.QueueThread = mp.Process(target=self.enqueue_frame_buffer)
        self.QueueThread.start()

if __name__ == "__main__":

    rtspob = TESTFFMPEGC()
    rtspob.run_threads()
    
    print("=========================================")
