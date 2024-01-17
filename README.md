## Setup test environment on Ubuntu 22.04
Test instance reads Gazebo sim camera directly from the screen. Pay attention to the camera module settings
### Install
```
sudo apt update && sudo apt install python3-pip
pip3 install --user --upgrade pip
pip3 install --user mavsdk
pip3 install --user numpy

pip3 install aioconsole
pip3 install opencv-python
pip3 install ultralytics
git clone https://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@github.com/needlee-uav/core.git
```

### Run simulation
```
cd ~/PX4-Autopilot
make px4_sitl_default gz_x500
```
### Run test Needlee simulation
```
cd ~/core
python3 main.py
```

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
sudo libcamera-vid -n -t 0 --width 640 --height 480 --framerate 24 --inline --listen -o tcp://127.0.0.1:8888
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
pip3 install --user opencv-python
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