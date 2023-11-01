from test_infer import Infer
from api_post import API
from ffmpegpy import FFMPEGC
import json
import time
from threading import Event
import os
import logging
import sys

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
logger = logging.getLogger('app')


def create_FFMPEG_pool(inferob,api,data):
    rtsp_object_list = []
    logger.info("Creating FFMPEG RTSP Stream Capture Object Group")
    for camera_config in data['cameras']:
        retry = 0
        waittime = 30
        while retry <= 12: ## Will Rety to create object forever
            try:
                rtspob = FFMPEGC(inferob,api,camera_config)
                rtspobevent = Event()
                rtsp_object_list.append([rtspob,rtspobevent,camera_config])
                break
            except:
                waittime = (waittime * 2 ) % 3600
                logger.warning("exception in creating FFMPEG object pool : retryin in {} seconds again, retry:- {}/12 ".format(waittime,retry))
                time.sleep(waittime)
                retry+=1
        if (retry == 12):
            logger.error("Failed to probe RTSP Stream for camera :- ",camera_config['camera'])
            logger.error("Failed to probe RTSP Stream for URL :- ",camera_config['rtsp_url'])
            logger.error("Exiting Process")
            sys.exit(0)
    logger.info("FFMPEG RTSP Stream Capture Object Group of size {} is created".format(len(rtsp_object_list)))
    return rtsp_object_list


def kill_and_respawn_FFMPEG_thread(inferob,api,camera_config):
    retry = 0
    while retry <= 3:
        try:
            logger.info("Respwaning FFMPEG Capture Object")
            rtspob = FFMPEGC(inferob,api,camera_config)
            rtspobevent = Event()
            logger.info("Running FFMPEG Capture Threads")
            rtspob.run_threads(rtspobevent)
            logger.info("Successfully Respwaned FFMPEG Capture Object")
            return rtspob,rtspobevent
        except Exception as e:
            logger.error("Couldn't respawn new FFMPEG Connection, retrying {}/3".format(retry))
            logger.error(e)
            retry+=1
            time.sleep(15)
    logger.warning("Failed to Respwaned FFMPEG Capture Object")
    return None,None



if __name__=="__main__":
    inferob = Infer()
    api = API()
    f = open('camera_config.json')
    data = json.load(f)
    logger.info("Begin Creating FFMPEG RTSP Stream Capture Object Group")
    rtsp_object_list = create_FFMPEG_pool(inferob,api,data)

    for rtsp_object,rtspobevent,_ in rtsp_object_list:
        rtsp_object.run_threads(rtspobevent)
    
    while True:
        logger.info("Object pool size :- {} ".format(len(rtsp_object_list)))
        # print(rtsp_object_list,len(rtsp_object_list))
        for rtsp_object,rtspob_event,camera_config in rtsp_object_list:
            logger.info("Queue Thread Status :- {}".format(rtsp_object.QueueThread.is_alive()))
            if(rtsp_object.QueueThread.is_alive() == False):
                logger.info("Killing Failed Thread")
                rtspob_event.set()
                # rtsp_object.DequeueThread.join()
                logger.info("Removing Failed Object from Object Group")
                if [rtsp_object,rtspob_event,camera_config] in rtsp_object_list:
                    # print("Check and remove rtsp object")
                    rtsp_object_list.remove([rtsp_object,rtspob_event,camera_config])
                logger.info("Begin Respwaning FFMPEG Capture Object")
                rtspob,rtspobevent = kill_and_respawn_FFMPEG_thread(inferob,api,camera_config)
                if(rtspob is not None and rtspobevent is not None):
                    rtsp_object_list.append([rtsp_object,rtspob_event,camera_config])
            
        time.sleep(60)