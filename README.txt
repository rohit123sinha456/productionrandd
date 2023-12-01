Python 3.11.3
pip 22.3.1

## To install
1. git clone
2. Create virtual environment
3. install dependencies [pip install updated_requirements.txt]
4. configure cameras and config file respectively
5. put ffmpeg,ffplay and ffprobe exe in the environment


## To create Service for Windows :-
1. Download nssm[https://stackoverflow.com/questions/32404/how-do-you-run-a-python-script-as-a-service-in-windows]
2. Add nssm to environment variable.
3. Create a service of nssm [nssm inatall "name of ther service" ]
    - Path to python is the environment python Path
    - AppDirectry is the project direcctory
    - Arguments is the ffmpeg__main.py file path.
    - Environment Path=<path to ffmpeg_bin>
4. Then start the service as nssm start "service Name"
5. Check windows services if its running and startup type is automatic. Check logs to see the status



New Approach ( by Saroj Sir)

Create New service for each camera.
cam1 is for camera1
and so on. in the code file change the RTSP URLS