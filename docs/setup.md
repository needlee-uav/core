## JETSON JETPACK4.6 | QENG 
sudo apt update
sudo apt upgrade
sudo apt-get update
sudo apt-get upgrade

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
sudo chmod a+rw /dev/ttyACM0
mavproxy.py --master /dev/ttyACM0 --baud 56700

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


## Setup test environment on Ubuntu 22.04
Test instance reads Gazebo sim camera directly from the screen. Pay attention to the camera module settings
### Install
```
sudo apt update && sudo apt install python3-pip
pip3 install --user --upgrade pip
pip3 install --user mavsdk
pip3 install --user numpy
sudo chmod a+rw /dev/ttyACM0

pip3 install aioconsole
pip3 install --user opencv-contrib-python==4.5.5.62
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
pip3 install --user opencv-contrib-python==4.5.5.62
pip3 install ultralytics
git clone https://github.com/steven-kollo/t-needle
```

============================================

## Setup Jetson Nano environment on Debian Ubuntu 20
https://sahilchachra.medium.com/setting-up-nvidias-jetson-nano-from-jetpack-to-yolov5-60a004bf48bc
###
Download required packages
```
sudo apt install minicom
sudo apt install net-tools
sudo apt update
sudo apt upgrade
```
Plug SIM7600
```
sudo minicom -D /dev/ttyUSB2
```
Check SIM7600 connection (3 OK responses required)
```
ATE1
AT+CGDCONT=1,"IP","super"
AT+COPS?
```
Send the following commands through minicom and wait for the module to restart
```
ATE1
AT+CUSBPIDSWITCH=9011,1,1
```
Run the ifconfig command to see if a USB0 card is identified
```
ifconfig
```
Route to SIM7600 & disable wifi
```
sudo dhclient -v usb0
sudo ifconfig wlan0 down
ping google.com
```
Troubleshooting:

https://www.twilio.com/docs/iot/supersim/getting-started-super-sim-raspberry-pi-waveshare-4g-hat

https://www.twilio.com/docs/iot/supersim/cellular-modem-knowledge-base/simcom-supersim#sim7600-cat-4

https://www.spotpear.com/index.php/index/study/detail/id/234.html

### Python 3.12
https://phoenixnap.com/kb/how-to-install-python-3-ubuntu

```
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

cd /tmp
wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz
tar -xf Python-3.12.1.tgz
cd Python-3.12.1
./configure --enable-optimizations
```
Build takes 20-30 minutes
```
sudo make install
python3 --version
```
### Setup Needlee Core
```
sudo apt update && sudo apt install python3-pip
pip3 install --user --upgrade pip
pip3 install --user mavsdk
pip3 install --user numpy
pip3 install --user aioconsole
pip3 install --user opencv-contrib-python==4.5.5.62
pip3 install --user ultralytics

sudo chmod a+rw /dev/ttyACM0 # optional, tests only
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
    data='42.134_43.123_123_8'sudo pip3 install mavproxy (optional)
sudo apt remove modemmanager (optional)
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
============================================

## Setup Raspberry Pi environment on Debian Ubuntu 22
### SIM7600
Download required packages
```
sudo apt install minicom
sudo apt install raspi-config
sudo apt install net-tools
sudo apt install linux-modules-extra-raspi
sudo apt update
sudo apt upgrade
```
Open serial port
```
sudo raspi-config
Interface -> Serial -> No -> Yes
reboot
```
Plug SIM7600
```
sudo minicom -D /dev/ttyUSB2
```
Check SIM7600 connection (3 OK responses required)
```
ATE1
AT+CGDCONT=1,"IP","super"
AT+COPS?
```
Send the following commands through minicom and wait for the module to restart
```
ATE1
AT+CUSBPIDSWITCH=9011,1,1
```
Run the ifconfig command to see if a USB0 card is identified
```
ifconfig
```
Route to SIM7600 & disable wifi
```
sudo dhclient -v usb0
sudo ifconfig wlan0 down
ping google.com
```
Troubleshooting:

https://www.twilio.com/docs/iot/supersim/getting-started-super-sim-raspberry-pi-waveshare-4g-hat

https://www.twilio.com/docs/iot/supersim/cellular-modem-knowledge-base/simcom-supersim#sim7600-cat-4

https://www.spotpear.com/index.php/index/study/detail/id/234.html

### Legacy camera 2.0

Enable legacy camera software
```
sudo raspi-config
Interface -> Legacy Camera -> Yes
reboot
```
Install pip3 git, & meson
```
sudo apt update && sudo apt install python3-pip
sudo apt install -y git
sudo pip3 install meson=1.1.1 # (as root!)
```
Install v4l-utils
```
sudo apt install v4l-utils
```
Add camera driver to the OS config
```
sudo nano /boot/firmware/config.txt
dtoverlay=ov5647
```
Install vision packages
```
pip3 install aioconsole
pip3 install opencv-python
pip3 install ultralytics
```
Install camera dependencies
```
sudo apt install -y libcamera-dev libjpeg-dev libtiff5-dev libpng.dev
sudo apt install -y libcamera-dev libepoxy-dev libjpeg-dev libtiff5-dev
sudo apt install -y qtbase5-dev libqt5core5a libqt5gui5 libqt5widgets5
sudo apt install libavcodec-dev libavdevice-dev libavformat-dev libswresample-dev
sudo apt install -y python3-pip git python3-jinja2
sudo apt install -y libboost-dev
sudo apt install -y libgnutls28-dev openssl libtiff5-dev pybind11-dev
sudo apt install -y qtbase5-dev libqt5core5a libqt5gui5 libqt5widgets5
sudo apt install -y meson cmake
sudo apt install -y python3-yaml python3-ply
sudo apt install -y libglib2.0-dev libgstreamer-plugins-base1.0-dev
```
Build libcamera
```
cd
git clone https://github.com/raspberrypi/libcamera.git
cd libcamera
```
```
meson setup build --buildtype=release -Dpipelines=rpi/vc4,rpi/pisp -Dipas=rpi/vc4,rpi/pisp -Dv4l2=true -Dgstreamer=enabled -Dtest=false -Dlc-compliance=disabled -Dcam=disabled -Dqcam=disabled -Ddocumentation=disabled -Dpycamera=enabled
```
```
ninja -C build
sudo ninja -C build install
```
Build rpicam-apps
```
sudo apt install -y cmake libboost-program-options-dev libdrm-dev libexif-dev
sudo apt install -y meson ninja-build
```
```
cd
git clone https://github.com/raspberrypi/rpicam-apps.git
cd rpicam-apps
meson setup build -Denable_libav=true -Denable_drm=true -Denable_egl=true -Denable_qt=true -Denable_opencv=false -Denable_tflite=false
```
```
meson compile -C build
sudo meson install -C build
sudo ldconfig # this is only necessary on the first build
```
```
sudo reboot
```
```
libcamera-hello --help
libcamera-jpeg -o test.jpg
python3 ./needlee/rpi_camera_test.py
```
Streaming TCP full test
```
sudo libcamera-vid -n -t 0 --width 320 --height 320 --framerate 10 --mode 320:320:10 --inline --listen -o tcp://127.0.0.1:8888
python3 ./needlee/rpi_camera_test.py
```
Troubleshooting:

https://www.raspberrypi.com/documentation/computers/camera_software.html

https://www.waveshare.com/rpi-camera-b.htm

https://docs.ultralytics.com/guides/raspberry-pi/#modify-detectpy

### Setup Needlee Core
```
sudo apt update && sudo apt install python3-pip
pip3 install --user --upgrade pip
pip3 install --user mavsdk
pip3 install --user numpy
pip3 install --user aioconsole
pip3 install --user opencv-contrib-python==4.5.5.62
pip3 install --user ultralytics

sudo chmod a+rw /dev/ttyACM0 # optional, tests only
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
    data='42.134_43.123_123_8'sudo pip3 install mavproxy (optional)
sudo apt remove modemmanager (optional)
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
