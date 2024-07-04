## JETSON JETPACK4.6 | QENG 
sudo apt update
sudo apt upgrade
sudo apt-get update
sudo apt-get upgrade
sudo apt remove modemmanager

python3 -m pip install --upgrade pip
python3 -m pip install MAVProxy 
python3 -m pip install --upgrade wheel
python3 -m pip install protobuf
python3 -m pip install mavsdk
python3 -m pip install python-socketio
python3 -m pip install python-socketio[client]

git clone https://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@github.com/needlee-uav/core.git
sudo reboot

TEST 1
sudo chmod a+rw /dev/ttyACM0 && mavproxy.py --master /dev/ttyACM0 --baud 56700

TEST 2
cd core
python3 test.py

TEST 3
python3 main.py --run main --server web --mode test --camera none -> Run and check main.log for the line "INIT: Connected to drone!"


CAMERA
https://www.youtube.com/watch?v=bcM5AQSAzUY

cd 
git clone --recursive https://github.com/dusty-nv/jetson-inference
cd jetson-inference/
mkdir build
cd build/
cmake ../
make
sudo make install
sudo ldconfig

cd 
cd core
python3 main.py --run main --server web --mode visiontest --camera vision --visiontest 101

TEST SYS
python3 main.py --run main --server web --mode test --camera stream


### Setup service: Inet
SET MINICOM
somehow minicom opens two usb ports on ifconfig: usb0 & usb1
line check the connection on one and another

```
sudo nano /lib/systemd/system/needlee_minicom.service
```
```
[Unit]
Description=Inet Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/bin/sh -c 'sleep 10 && ifconfig | grep usb1:.*RUNNING* >/dev/null && sudo dhclient -v usb1 || sudo dhclient -v usb0'

[Install]
WantedBy=multi-user.target
```
```
sudo chmod 644 /lib/systemd/system/needlee_minicom.service
sudo systemctl daemon-reload
sudo systemctl enable needlee_minicom.service
sudo systemctl start needlee_minicom.service
sudo reboot
```

```
systemctl status needlee_minicom.service
ping google.com
```

### Setup service: MAVProxy

```
sudo nano /lib/systemd/system/needlee_mavproxy.service
```
```
[Unit]
Description=MAVProxy Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/bin/sh -c 'sudo chmod a+rw /dev/ttyACM0 && /usr/bin/python3.6 /home/jetson/Desktop/mavproxy_script.py'

[Install]
WantedBy=multi-user.target
```
```
sudo chmod 644 /lib/systemd/system/needlee_mavproxy.service
sudo systemctl daemon-reload
sudo systemctl enable needlee_mavproxy.service
sudo systemctl start needlee_mavproxy.service
sudo reboot
```
```
systemctl status needlee_mavproxy.service
```