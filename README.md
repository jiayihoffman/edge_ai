## Smart robots make home safe and fun

[Security Camera](./security_camera/README.md) is a image classify project running on Raspberry Pi using Pi camera streaming. The model is a pre-trained mobilenet model, downloaded from TensorFlow Hub, and fine tuned using my personal images. The model then is quantized to fit on a Raspberry Pi. 

The V2 of this project uses an IR sensor for motion detection and is paired with sound detection, object detection, and recording if a motion is detected. The V2 of the Security Camera can be used for wildlife detection. The sound detection using a quantized pretrained YAMNet, and object detection uses a quantized pretrained EfficientDet.

[Robot Car](./robot_car/README.md) is another project that allows me to remotely drive the car and see the house while I am away. It uses Arduino for IO, Raspberry Pi for robot control and WebRTC for video streaming and remote control.

The V2 of the Robot Car uses ROS2_Nav2 for autonomous driving with mapping and localization. It is currently working in progress. 
