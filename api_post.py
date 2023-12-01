import requests
import yaml
import os
import logging
import cv2
import numpy as np

class API:
    def __init__(self):
        self.logger = logging.getLogger('app.API')
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.url = self.config['url']['upload']
        self.save_url = self.config['url']['save']
        self.image_folder = self.config['output']['folder']
        # logging.basicConfig(filename=os.path.join('.', 'logs', 'api_posting.log'),format='%(asctime)s:%(levelname)s: %(message)s')

    def check_corrupation(self,filepath):
        img = cv2.imread(filepath)
        filesize = os.stat(filepath).st_size/(1024)
        image_median = np.median(img)
        # print(filepath,filesize,image_median)
        if(filesize < 400 and image_median > 110):
            return True
        else:
            return False
        
    def posting(self,filename,camera_config):
        imgencode = ""
        x = ""
        self.logger.info("Begin Sending Data to API Server")
        filepath = filename #os.path.join('.', self.image_folder, filename)
        if(self.check_corrupation(filepath) == True):
            return
        with open(filepath, "rb") as img_file:
            try:
                x = requests.post(self.url, files= {"image": img_file})
            except Exception as e:
                self.logger.error("Failed to Post Image to Server")
                raise e
            try:
                self.logger.info("Image Saved in server with name :- ".format(x.json()['data']['fileName']))
                serverfilepath = x.json()['data']['fileName']
                msgbody = {"dept_name": camera_config['dept_name'],
                           "camera": camera_config['camera'],
                           "alarm_type": camera_config['alarm_type'],
                           "image": serverfilepath}
                x = requests.post(self.save_url, json=msgbody)
                self.logger.info("Image Updated in Server Database")
                self.logger.info(x.content)
            except Exception as e:
                self.logger.error("Failed to Post Image Details to Server")
                raise e
                #logging.warning(e)
        return x
