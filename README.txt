Python 3.11.3
pip 22.3.1
## To install
1. git clone
2. Create virtual environment
3. install dependencies
4. configure cameras and config file respectively
5. put ffmpeg,ffplay and ffprobe exe in the environment
## To create Service for Windows :-
1. Download nssm[https://stackoverflow.com/questions/32404/how-do-you-run-a-python-script-as-a-service-in-windows]
2. Add nssm to environment.
3. Create a service of nssm
    - Path to python is the environment python Path
    - AppDirectry is the project direcctory
    - Arguments is the ffmpeg__main.py file path.
    - Environment Path=<path to ffmpeg_bin>