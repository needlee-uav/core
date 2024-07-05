## TEST ENV SETUP DESKTOP UBUNTU 20
```
git clone --depth 1 --branch v1.14.0-rc1 https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
```
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

Run simulation
```
cd ~/PX4-Autopilot
make px4_sitl gazebo-classic_typhoon_h480
```
Run core
```
cd /core
python3 main.py --run main --server web --mode test --camera vision
```

## JETSON NANO UBUNTU 20 QENGINEERING IMAGE + CV PACKS
https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image
Download the extended one, 8.7GB 

```
sudo usermod -a -G sudo username
sudo adduser $USER $(stat --format="%G" /dev/ttyACM0 )
sudo apt update
sudo apt upgrade
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip

(ignore tensorflow2.4.1 pip dependency errors)
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade numpy
python3 -m pip install mavsdk
python3 -m pip install python-socketio
python3 -m pip install python-socketio[client]

cd (local root)
git clone https://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@github.com/needlee-uav/core.git

sudo chmod a+rw /dev/ttyACM0
sudo reboot
```

### JETSON INFERENCE
https://www.youtube.com/watch?v=bcM5AQSAzUY
```
cd (local root)
git clone --recursive https://github.com/dusty-nv/jetson-inference
cd jetson-inference/
mkdir build
cd build/
cmake ../
make
make install (to connect local packages, run until the error)
sudo make install (complete make on sudo)
sudo ldconfig

cd core/test_scripts/main.py
python3 main.py (wait until net archives installed on the first launch)

sudo reboot
```
### TEST
```
cd core/test_sripts/main.py
python3 main.py
```
```
sudo nano /lib/systemd/system/test.service
```
```
[Unit]
Description=Test Service
After=multi-user.target

[Service]
Type=simple
User=jetson
ExecStart=/usr/bin/python3 /home/jetson/core/test_sripts/main.py

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl enable test.service
sudo systemctl start test.service
sudo systemctl status test.service
(optional, on errors) sudo chmod 644 /lib/systemd/system/test.service
```

### SIM7600
Download required packages
```
sudo apt install minicom
sudo apt install net-tools
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
ping google.com
```
Troubleshooting:

https://www.twilio.com/docs/iot/supersim/getting-started-super-sim-raspberry-pi-waveshare-4g-hat

https://www.twilio.com/docs/iot/supersim/cellular-modem-knowledge-base/simcom-supersim#sim7600-cat-4

https://www.spotpear.com/index.php/index/study/detail/id/234.html
