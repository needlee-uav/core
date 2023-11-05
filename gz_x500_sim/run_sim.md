## Run Gazebo simulation with screen capture
Login into Ubuntu with X11 config (login screen settings)
```
python -m pip install -U --user mss
python -m pip install -U --user opencv-python
```
## Run simulation
```
cd ~/PX4-Autopilot
make px4_sitl_default gz_x500
```
## Run test T-Needle app
```
cd ~/t-needle
python3 main.py
```
## Run openCV screen capture script
```
cd ~/t-needle/gz_x500_sim/opencv_mss_screen
python3 read_screen.py
```