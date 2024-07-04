## JETSON NANO UBUNTU 20 QENGINEERING IMAGE + CV PACKS
https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image
Download the extended one, 8.7GB 

sudo apt update
sudo apt upgrade
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip

python3 -m pip install --upgrade pip
python3 -m pip install mavsdk
python3 -m pip install python-socketio
python3 -m pip install python-socketio[client]

cd (local root)
git clone https://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@github.com/needlee-uav/core.git

sudo chmod a+rw /dev/ttyACM0
sudo reboot

### JETSON INFERENCE
https://www.youtube.com/watch?v=bcM5AQSAzUY

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

sudo reboot

### TEST
cd core/tests/jetson
python3 main.py


sudo nano /lib/systemd/system/test.service

[Unit]
Description=Test Service
After=multi-user.target

[Service]
Type=simple
User=jetson
ExecStart=/usr/bin/python3 /home/jetson/tests/main.py

[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl enable test.service
sudo systemctl start test.service
sudo systemctl status test.service

(optional, on errors) sudo chmod 644 /lib/systemd/system/test.service

