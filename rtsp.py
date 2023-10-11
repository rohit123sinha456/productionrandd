import cv2
import time
import logging
import numpy as np
import os
import queue 
import threading
import uuid


class RTSP():
    def __init__(self,Inference,API,camera_config,MaxRetries=3):
        self.inferob = Inference
        self.api = API
        self.camera_config = camera_config
        self.rtsp_url = camera_config['rtsp_url']
        self.img_folder = camera_config['camera']
        self.maxretries = MaxRetries
        self.retryinterval = 30
        self.framequeue = queue.Queue()
        self.MaxCorruptFrameDuration = 30
        self.cap = None
        logging.basicConfig(filename=os.path.join('.', 'logs', 'rtsp.log'),format='%(asctime)s:%(levelname)s: %(message)s')
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)
    # def setup_connection(self):
        Retry = 0
        for Retry in range(self.maxretries):
            try:
                # Connect to the RTSP stream
                self.cap = cv2.VideoCapture(self.rtsp_url)
                ret, Frame = self.cap.read()

                if not ret:
                    logging.info("No video feed available. Retrying in {} seconds (Retry {}/{})".format(self.retryinterval, Retry + 1, self.maxretries))
                if not self.cap.isOpened():
                    logging.info("Failed to Open RTSP Stream. Retrying in {} seconds (Retry {}/{})".format(self.retryinterval, Retry + 1, self.maxretries))
                    time.sleep(self.retryinterval)
                    continue
                else:
                    logging.info("Connection Successfully Established")
                    break
                
            except Exception as e:
                print("Exception whiole reading RTSP STream")
                print(e)
                Retry += 1
                time.sleep(self.retryinterval)
                

    def enqueue_frame_buffer(self,event):
        print("Reading and Enqueing Frames")
        print("Capture Status",self.cap.isOpened())
        while not event.is_set():
            try:
                ret, Frame = self.cap.read()
            except:
                logging.warning("Problem in reading Frames")
                
            if not ret:
                logging.warning("No video feed available")
                break
                
            # Enqueue the frame for saving
            try:
                if Frame is not None:
                    dets = self.inferob.detection(Frame)
                    frames = self.inferob.tracking(Frame,dets)
                    i = uuid.uuid4()
                    fnmae = "frame" + str(i) + '.jpg'
                    frame_name = os.path.join('.', self.img_folder, fnmae)
                    # print("Frame processing Done")
                    
                    if(frames is not None):

                        # cv2.imshow(self.camera_config['camera'],frames)
                        # if cv2.waitKey(1) & 0xFF == ord('q'):
                        #     cv2.destroyAllWindows()
                        #     break

                        logging.info("Sending Image")
                        cv2.imwrite(frame_name,frames)
                        self.api.posting(frame_name,self.camera_config)
                        logging.info("Frame posting done")

                        
            except Exception as e:
                print("Problem with processing")
                print(e)
                logging.warning("Problem with processing")

    def run_threads(self,event):
        self.QueueThread = threading.Thread(target=self.enqueue_frame_buffer,args=(event,))
        # self.DequeueThread = threading.Thread(target=self.dequeue_frame_buffer,args=(event,))
        # self.DequeueThread.daemon = True
        self.QueueThread.daemon = True
        self.QueueThread.start()
        # self.DequeueThread.start()
        # print("Queue Thread Status :- ", QueueThread.is_alive())
        # print("Dequeue Thread Status :- ", DequeueThread.is_alive())
        # while True:
        #     print("Queue Thread Status :- ", QueueThread.is_alive())
        #     print("Dequeue Thread Status :- ", DequeueThread.is_alive())
        #     time.sleep(60)