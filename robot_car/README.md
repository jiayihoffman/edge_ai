# Robot Car

I have two lovely cats. I often miss them when I am travel. I have a cat sitter help, but having a robot that I can remotely drive and see what the robot sees will be great. Then I can see what my cats are doing and talk to them whenever I want.   

Technologies used here are Arduino, Raspberry Pi, WebRTC, and Kafka event streaming. Arduino is for IO; Raspberry Pi is the controller, the robot’s brain. The Pi sends me the live video stream through WebRTC while driving through the house, and it responds to commands I sent remotely through Kafka or the WebRTC data channel.


