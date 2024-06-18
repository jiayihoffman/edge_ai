## Smart robots make home safe and fun

[Security Camera](./security_camera/README.md) is a image classify project running on Raspberry Pi using Pi camera streaming. The model is a pre-trained MobileNet model, downloaded from TensorFlow Hub, and fine tuned using my personal images. The model then is quantized to fit on a Raspberry Pi. 

The V2 of this project uses an IR sensor for motion detection and is paired with sound detection, object detection, and recording if a motion is detected. The V2 of the Security Camera can be used for wildlife detection. The sound detection uses a quantized YAMNet, and object detection uses a quantized EfficientDet.

[Robot Car](./robot_car/README.md) is another project that allows me to remotely drive the car and see my cats while away. The car uses Arduino to interact with sensors, Raspberry Pi for robot control, and WebRTC for video streaming.

The V2 of the Robot Car can autonomously drive itself with mapping and localization. Stay tuned. 
