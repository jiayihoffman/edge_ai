
### setup the command center environment (on Mac):
```
>> python3 -m venv tensor_env
>> source tensor_env/bin/activate
(tensor_env) >> pip install --upgrade pip
(tensor_env) >> pip install -r requirements.txt

# install Tkinter, python graphic UI for key detection. 
(tensor_env) >> sudo apt-get install python-tk
```

### Setup the robot controller environment: (on Raspberry Pi)
```
>> python3 -m venv tensor_env
>> source tensor_env/bin/activate
(tensor_env) >> pip install --upgrade pip
(tensor_env) >> pip install -r requirements_raspi.txt 
```

### Arduino and Raspberry Pi communication:
1. Direct communication using the USB serial port 
https://www.woolseyworkshop.com/2020/02/05/controlling-an-arduino-from-a-raspberry-pi/
2. Use firmata
(tensor_env) >> pip install pyfirmata
https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/
3. Use IOC bus to do logical level conversion
https://dronebotworkshop.com/i2c-arduino-raspberry-pi/
	


