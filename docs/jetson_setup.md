## Flash image
Download image from https://developer.nvidia.com/embedded/jetpack-sdk-45-archive
Flash to 64gb sd card with BalenaEtcher
Follow instructions in this video https://www.youtube.com/watch?v=uvU8AXY1170

Run
```
sudo apt-get update
sudo apt-get upgrade
sudo apt install nano
```
Reboot & run
Numpy at 1.19.4 is required
```
sudo apt-get install python3-pip
python -m pip3 install --upgrade pip
pip3 install cython
pip3 install numpy==1.19.4
pip3 install opencv-python
```
Reboot & install PyTorch
Help https://qengineering.eu/install-pytorch-on-jetson-nano.html
```
sudo apt-get install libjpeg-dev libopenblas-dev libopenmpi-dev libomp-dev
sudo apt install libfreetype6-dev python3-dev zlib1g-dev

sudo -H pip3 install future
sudo pip3 install -U --user wheel mock pillow
sudo -H pip3 install testresources
sudo -H pip3 install setuptools==58.3.0
sudo -H pip3 install Cython

sudo -H pip3 install gdown
gdown https://drive.google.com/uc?id=1TqC6_2cwqiYacjoLhLgrZoap6-sVL2sd
sudo -H pip3 install torch-1.10.0a0+git36449ea-cp36-cp36m-linux_aarch64.whl
rm torch-1.10.0a0+git36449ea-cp36-cp36m-linux_aarch64.whl
```
Test
```
python3
>>> import torch as tr
>>> tr.__version__
>>> print(tr.rand(5,4))
```
Reboot & install TensorFlow 2.4.1
Help https://qengineering.eu/install-tensorflow-2.4.0-on-jetson-nano.html
```
sudo -H pip3 install protobuf==3.9.2
sudo apt-get install gfortran
sudo apt-get install libhdf5-dev libc-ares-dev libeigen3-dev
sudo apt-get install libatlas-base-dev libopenblas-dev libblas-dev
sudo apt-get install liblapack-dev
sudo -H pip3 install Cython==0.29.21

sudo -H pip3 install h5py==2.10.0
sudo -H pip3 install -U numpy==1.19.4
sudo -H pip3 install pybind11 google-pasta
sudo -H pip3 install -U six mock wheel requests gast
sudo -H pip3 install keras_applications --no-deps
sudo -H pip3 install keras_preprocessing --no-deps

gdown https://drive.google.com/uc?id=1DLk4Tjs8Mjg919NkDnYg02zEnbbCAzOz
sudo -H pip3 install tensorflow-2.4.1-cp36-cp36m-linux_aarch64.whl
```
Test
```
python3
>>> import tensorflow as tf
>>> tf.__version__
'2.4.1'
>>> print(tf.reduce_sum(tf.random.normal(1000, 1000)))
tf.Tensor(501.81415, shape(), dtype=float32)
```
https://docs.ultralytics.com/yolov5/tutorials/running_on_jetson_nano/#deepstream-configuration-for-yolov5
https://forums.developer.nvidia.com/t/getting-error-as-error-failed-building-wheel-for-onnx/267524

ONNX RUNTIME
```
wget https://nvidia.box.com/shared/static/iizg3ggrtdkqawkmebbfixo7sce6j365.whl -O onnxruntime_gpu-1.10.0-cp36-cp36-linux_aarch64.whl
python3 -m pip install onnxruntime_gpu-1.10.0-cp36-cp36-linux_aarch64.whl
```
```
sudo apt-get install protobuf-compiler lobprotoc-dev
python3 -m pip install onnx
```
