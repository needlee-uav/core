## Setup Python3.6.9 test environment on Ubuntu 20.04

### PX4-Autopilot Python>=3.7
Update packages
```
sudo apt update
pip3 install --user --upgrade pip
```
Install PX4 with Python>=3.7
```
git clone --depth 1 --branch v1.14.0-rc1 https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
sudo reboot
```
Test PX4 gazebo-classic
```
pip3 install empy==3.3.4
make px4_sitl gazebo-classic_typhoon_h480
```

### Python3.6.9
Download packages
```
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
```
Install Python3.6.9
```
cd /tmp
wget https://www.python.org/ftp/python/3.12.1/Python-3.6.9.tgz
tar -xf Python-3.6.9.tgz
cd Python-3.6.9
./configure --enable-optimizations
```
Build takes 20-30 minutes
```
sudo make altinstall
python3.6 --version
```

### Python3.6.9 env
Create env
```
python3.6 -m venv env
source env/bin/activate
```
Download packages

```
pip3 install pycairo
pip3 install PyGObject
pip3 install protobuf==3.19.6
pip3 install mavsdk
pip3 install aioconsole

pip3 install Flask
pip3 install gunicorn
pip3 install eventlet
pip3 install Flask-socketio
pip3 install python-engineio
pip3 install python-socketio
pip3 install simple-websocket
pip3 install python-socketio[client]

pip3 install numpy==1.19.4
pip3 install opencv-python
```

### Troubleshooting
PX4 guide
https://docs.px4.io/main/en/dev_setup/building_px4.html

Python3.6.9
https://phoenixnap.com/kb/how-to-install-python-3-ubuntu

Sim vision
https://github.com/bozkurthan/PX4-Gazebo-Opencv
```
sudo apt install libgtk2.0-dev pkg-config
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python-dev gir1.2-gtk-3.0
```

### Needlee Core setup
Download core
```
git clone https://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@github.com/needlee-uav/core.git
```
Run Gazebo simulation
```
cd ./Path-to-PX4-Autopilot
make px4_sitl gazebo-classic_typhoon_h480
```
Run core from the second terminal
```
cd ./Path-to-Needlee-Core
python3 main.py
```