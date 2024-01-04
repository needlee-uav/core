## Setup test environment on Ubuntu 22.04
Test instance reads Gazebo sim camera directly from the screen. Pay attention to the camera module settings
### Install
```
sudo apt update && sudo apt install python3-pip
pip3 install --user --upgrade pip
pip3 install --user mavsdk
sudo pip3 install mavproxy (optional)
sudo apt remove modemmanager (optional)
sudo chmod a+rw /dev/ttyACM0

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
### Setup service
```
sudo nano /lib/systemd/system/test.service
```
```
 [Unit]
 Description=Test Service
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=/usr/bin/python /home/px/test.py

 [Install]
 WantedBy=multi-user.target
```

Script
```
import requests
import time

def handshake():
    data='42.134_43.123_123_8'
    connected=False
    i=0
    while not connected:
        try:
            i+=1
            url=f'https://needlee-server-4ohicpymya-uc.a.run.app/handshake/UAV-1234/{data}'
            res=requests.get(url).text
            print(res)
            if res=='success':
                connected=True
                print('success')
        except:
            print('internet error')
        time.sleep(1)

handshake()
```

```
sudo chmod 644 /lib/systemd/system/test.service
sudo systemctl daemon-reload
sudo systemctl enable sample.service
sudo reboot
```

```
systemctl status test.service
```