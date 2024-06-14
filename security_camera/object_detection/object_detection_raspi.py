import argparse
import time

import cv2
from picamera2 import Picamera2, Preview

import logging_utils
import visualizer
from alerting_utils import alert_object_detection
from object_inference import ObjectDetector
from object_inference import ObjectDetectorOptions

_MODEL_FPS = 2  # Ensure the input images are fed to the model at this fps.
_MODEL_FPS_ERROR_RANGE = 0.1  # Acceptable error range in fps.


logging_utils.init_logging()

def run(model: str, camera_id: int, width: int, height: int, num_threads: int) -> None:
  """Continuously run inference on images acquired from the camera.

  Args:
    model: Name of the TFLite object detection model.
    camera_id: The camera id to be passed to OpenCV.
    width: The width of the frame captured from the camera.
    height: The height of the frame captured from the camera.
    num_threads: The number of CPU threads to run the model.
  """

  # Variables to calculate FPS
  fps, last_inference_start_time, last_alert_time = 0, 0, 0
  last_detected_categories = set()

  # Visualization parameters
  row_size = 20  # pixels
  left_margin = 24  # pixels
  text_color = (0, 0, 255)  # red
  font_size = 1
  font_thickness = 1

  # Initialize the object detection model
  options = ObjectDetectorOptions(
      num_threads=num_threads,
      score_threshold=0.4,
      max_results=3)
  detector = ObjectDetector(model_path=model, options=options)

  picam2 = Picamera2()
  picam2.start_preview(Preview.NULL)
  config = picam2.create_preview_configuration(main={"size": (width, height), "format": "BGR888"})
  picam2.configure(config)
  picam2.start()

  while True:
    # fetch the image array from the main stream
    array = picam2.capture_array("main")
    image = array

    # Ensure that frames are feed to the model at {_MODEL_FPS} frames per second
    # reduce the frequency to conserve the energy
    current_frame_start_time = time.time()
    diff = current_frame_start_time - last_inference_start_time
    if diff * _MODEL_FPS >= (1 - _MODEL_FPS_ERROR_RANGE):
      image = cv2.flip(image, 1)
      # Store the time when inference starts.
      last_inference_start_time = current_frame_start_time

      # Calculate the inference FPS
      fps = 1.0 / diff
      # Run object detection estimation using the model.
      detections = detector.detect(image)
      # Draw keypoints and edges on input image
      image = visualizer.visualize(image, detections)

      # Show the FPS
      fps_text = 'FPS = {:.1f}'.format(fps)
      text_location = (left_margin, row_size)
      cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                font_size, text_color, font_thickness)

      last_detected_categories = alert_object_detection(detections, last_detected_categories, image)

      # Stop the program if the ESC key is pressed.
      if cv2.waitKey(1) == 27:
        break

  cv2.destroyAllWindows()


def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model',
      help='Path of the object detection model.',
      required=False,
      default='./models/efficientdet_lite3.tflite')
  parser.add_argument(
      '--cameraId', help='Id of camera.', required=False, type=int, default=0)
  parser.add_argument(
      '--frameWidth',
      help='Width of frame to capture from camera.',
      required=False,
      type=int,
      default=640)
  parser.add_argument(
      '--frameHeight',
      help='Height of frame to capture from camera.',
      required=False,
      type=int,
      default=480)
  parser.add_argument(
      '--numThreads',
      help='Number of CPU threads to run the model.',
      required=False,
      type=int,
      default=4)
  args = parser.parse_args()

  run(args.model, int(args.cameraId), args.frameWidth, args.frameHeight,
      int(args.numThreads))


if __name__ == '__main__':
    main()
