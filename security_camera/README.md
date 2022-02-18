# Security Camera

## Why another security camera?
Security cameras out there use generic image recognition models. They can only detect generic images, i.e., a person, but cannot distinguish who the person is, a mail man or a stranger.  Besides that, the image model does not have good classification performance. For example, I often woke up in the midnight by security alerts from my doorbell. The alert says a person is detected, but video shows a cat just walked by. 

The reason the image model is generic is because it is not trained using customer's own images. What if I can train the image model using my own data. Is it possible? Does it require a supercomputer to train the model? Does the training take days? 

With the technology called "transfer learning", I can easily train a good image recognition model using my own images. The training is conducted in my mac, and the training takes less than 30 minutes.  

Once I have the model, I repackage the model into a tensor lite model. The model runs on a raspberry pi that has a pi camera attached to.  As the name suggested, the tensor lite model is small, fast, and with equivalent ML performance. 
 
