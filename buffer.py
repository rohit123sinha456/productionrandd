import ffmpeg
import numpy as np
import cv2


def main(source):
    args = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer",
        "flags": "low_delay"
    }    
    probe = ffmpeg.probe(source)
    cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
    print("fps: {}".format(cap_info['r_frame_rate']))
    width = cap_info['width']          
    height = cap_info['height']         
    up, down = str(cap_info['r_frame_rate']).split('/')
    fps = eval(up) / eval(down)
    print("fps: {}".format(fps))    
    process1 = (
        ffmpeg
        .input(source, **args)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .overwrite_output()
        .run_async(pipe_stdout=True)
    )
    while True:
        in_bytes = process1.stdout.read(width * height * 3)   
        if not in_bytes:
            break
        
        in_frame = (
            np
            .frombuffer(in_bytes, np.uint8)
            .reshape([height, width, 3])
        )
        # frame = cv2.resize(in_frame, (1280, 720))  
        in_frame = cv2.cvtColor(in_frame, cv2.COLOR_RGB2BGR)  
        cv2.imshow("ffmpeg", in_frame)
        if cv2.waitKey(1) == ord('q'):
            break
    process1.kill()           


if __name__ == "__main__":
   
    camera_ip = "192.168.20.221"   
    camera_login_user = "admin"
    camera_login_pwd = "admin123"
    camera_channel = 0     

    alhua_rtsp = "rtsp://admin:Sheraton123@10.111.111.215:554/Streaming/Channels/101/"

    main(alhua_rtsp)
