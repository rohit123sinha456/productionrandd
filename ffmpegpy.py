import cv2
import time
import logging
import numpy as np
import os
import threading
import uuid
import ffmpeg


class FFMPEGC():
    def __init__(self,Inference,API,camera_config,MaxRetries=3):
        self.inferob = Inference
        self.api = API
        self.camera_config = camera_config
        self.rtsp_url = camera_config['rtsp_url']
        self.img_folder = camera_config['camera']
        self.args = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer",
        "flags": "low_delay"}
        try:
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
            print("failed to Probe RTSP Stream")
            print(e)
            raise e
        
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)

    def enqueue_frame_buffer(self,event):
        self.process1 = (
            ffmpeg
            .input(self.rtsp_url, **self.args)
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .overwrite_output()
            .run_async(pipe_stdout=True)
        )
        
        while not event.is_set():
            try:
                in_bytes = self.process1.stdout.read(self.width * self.height * 3)   
                if not in_bytes:
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
                        logging.info("Sending Image")
                        cv2.imwrite(frame_name,frames)
                        self.api.posting(frame_name,self.camera_config)
                        logging.info("Frame posting done")
                        
            except Exception as e:
                print("Problem with Processing")
                print(e)
        print("Killing FFMPEG Process")
        self.process1.kill()   

    def run_threads(self,event):
        self.QueueThread = threading.Thread(target=self.enqueue_frame_buffer,args=(event,))
        self.QueueThread.daemon = True
        self.QueueThread.start()