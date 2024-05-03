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


### Setup Needlee Core
```
sudo apt update && sudo apt install python3-pip
pip3 install --user --upgrade pip
pip3 install --user mavsdk
pip3 install --user numpy
pip3 install --user aioconsole
pip3 install --user opencv-python
pip3 install --user ultralytics

pip3 install --user Flask
pip3 install --user eventlet
pip3 install --user Flask-socketio
pip3 install --user python-engineio
pip3 install --user python-socketio
pip3 install --user simple-websocket
pip3 install --user gunicorn
pip3 install --user python-socketio[client]

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