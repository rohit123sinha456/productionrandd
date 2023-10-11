import subprocess
import os
import signal
import time 
import multiprocessing
if __name__=="__main__":
    while True:
        process = subprocess.Popen(["env\Scripts\python.exe", "rtsp_main.py"],shell=False)
        pid = process.pid
        print(process.pid)
        time.sleep(240)
        print("----------------------------------------------------Killing Process-------------------------------------------------------------------------------------------------")
        os.kill(pid, signal.SIGTERM)
        time.sleep(15)
