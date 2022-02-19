
### setup the ML training environment (on Mac):
```
>> python3 -m venv tensor_env
>> source tensor_env/bin/activate
(tensor_env) >> pip install --upgrade pip
(tensor_env) >> pip install jupyterlab
(tensor_env) >> pip install -r requirements.txt
(tensor_env) >> pip install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime
```

### Setup the ML inference environment: (on Raspberry Pi)
```
>> python3 -m venv tensor_env
>> source tensor_env/bin/activate
(tensor_env) >> pip install --upgrade pip
(tensor_env) >> pip install -r requirements_raspi.txt 
```

Notes: 
* requirements_raspi.txt does not use tensorflow library. It uses tflite_runtime. 

====

to show core dump, add the following line in the python code: faulthandler is part of Python3
import faulthandler
faulthandler.enable()

====



