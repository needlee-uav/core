# Needlee
## Overview
![Alt text](./docs/general_scheme.png?raw=true "General scheme")

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
### Run test Needlee instance
```
cd ~/t-needle
python3 main.py
```
### Run tests

## Setup ground station application on Windows 11