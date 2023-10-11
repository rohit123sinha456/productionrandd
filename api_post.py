import requests
import yaml
import os
import logging
class API:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.url = self.config['url']['upload']
        self.save_url = self.config['url']['save']
        self.image_folder = self.config['output']['folder']
        # logging.basicConfig(filename=os.path.join('.', 'logs', 'api_posting.log'),format='%(asctime)s:%(levelname)s: %(message)s')

    def posting(self,filename,camera_config):
        imgencode = ""
        x = ""
        #logging.info("reading filename",filename)
        filepath = filename #os.path.join('.', self.image_folder, filename)
        with open(filepath, "rb") as img_file:
            x = requests.post(self.url, files= {"image": img_file})
            try:
                #logging.info("Image Saved in server with name :- ",x.json()['data']['fileName'])
                serverfilepath = x.json()['data']['fileName']
                msgbody = {"dept_name": camera_config['dept_name'],
                           "camera": camera_config['camera'],
                           "alarm_type": camera_config['alarm_type'],
                           "image": serverfilepath}
                x = requests.post(self.save_url, json=msgbody)
                #logging.info("Image Updated in Server Database")
                #logging.info(x.content)
            except Exception as e:
                pass
                #logging.warning(e)
        return x
