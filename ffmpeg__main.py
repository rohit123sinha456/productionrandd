from infer import Infer
from api_post import API
from ffmpegpy import FFMPEGC
import json
import time
from threading import Event
import os

def create_FFMPEG_pool(inferob,api,data):
    rtsp_object_list = []
    for camera_config in data['cameras']:
        retry = 0
        while retry<=3: ## Will Rety to create object for 3 times
            try:
                rtspob = FFMPEGC(inferob,api,camera_config)
                rtspobevent = Event()
                rtsp_object_list.append([rtspob,rtspobevent,camera_config])
                break
            except:
                print("exception in creating FFMPEG object pool : retryin in 30 seconds again")
                time.sleep(30)
                retry+=1
        if (retry == 3):
            print("Failed to probe RTSP Stream for camera :- ",camera_config['camera'])
            print("Failed to probe RTSP Stream for URL :- ",camera_config['rtsp_url'])
    return rtsp_object_list


def kill_and_respawn_FFMPEG_thread(inferob,api,camera_config):
    retry = 0
    while retry <= 3:
        try:
            rtspob = FFMPEGC(inferob,api,camera_config)
            rtspobevent = Event()
            print("Running Threads")
            rtspob.run_threads(rtspobevent)
            print("appending object")
            return rtspob,rtspobevent
        except Exception as e:
            print("Couldn't respawn new FFMPEG Connection, retrying {}/3".format(retry))
            print(e)
            retry+=1
            time.sleep(15)
    return None,None



if __name__=="__main__":
    inferob = Infer()
    api = API()
    f = open('camera_config.json')
    data = json.load(f)
    rtsp_object_list = create_FFMPEG_pool(inferob,api,data)

    for rtsp_object,rtspobevent,_ in rtsp_object_list:
        rtsp_object.run_threads(rtspobevent)
    
    while True:
        print("Object pool----------------------------------------------------------------------")
        print(rtsp_object_list,len(rtsp_object_list))
        for rtsp_object,rtspob_event,camera_config in rtsp_object_list:
            print("Queue Thread Status :- ", rtsp_object.QueueThread.is_alive())
            if(rtsp_object.QueueThread.is_alive() == False):
                print("killing Dequeue")
                rtspob_event.set()
                # rtsp_object.DequeueThread.join()
                print("GC Object")
                if [rtsp_object,rtspob_event,camera_config] in rtsp_object_list:
                    print("Check and remove rtsp object")
                    rtsp_object_list.remove([rtsp_object,rtspob_event,camera_config])
                print("Creating New object")
                rtspob,rtspobevent = kill_and_respawn_FFMPEG_thread(inferob,api,camera_config)
                if(rtspob is not None and rtspobevent is not None):
                    rtsp_object_list.append([rtsp_object,rtspob_event,camera_config])
            
        time.sleep(60)
    