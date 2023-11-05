## Setup test environment on Ubuntu 22.04
Test instance reads Gazebo sim camera directly from the screen. Pay attention to the camera module settings
### Install
```
git clone --depth 1 --branch v1.14.0-rc1 https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh

sudo reboot

pip3 install mavsdk
pip3 install aioconsole
pip3 install opencv-python
pip3 install ultralytics
git clone https://github.com/steven-kollo/t-needle
```

### Run simulation
```
cd ~/PX4-Autopilot
make px4_sitl_default gz_x500
```
### Run test T-Needle app
```
cd ~/t-needle
python3 main.py
```
## Setup Raspberry Pi environment on Debian Bookworm 64 bit
Core instance reads sensors and camera from PX4 and physical camera. Pay attention to the hardware guide.
### Install
```
git clone --depth 1 --branch v1.14.0-rc1 https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh

sudo reboot

sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED

sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev libl

pip3 install mavsdk
pip3 install aioconsole
pip3 install opencv-python
pip3 install ultralytics
git clone https://github.com/steven-kollo/t-needle
```
### Test camera
https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/Libcamera-User-Guide/

```
libcamera-hello --help
libcamera-jpeg -o test.jpg
python3 ./needlee/rpi_camera_test.py
```
