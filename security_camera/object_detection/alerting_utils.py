import datetime
import logging
import os

from PIL import Image

image_path = os.path.dirname(__file__) + '/../image_captures'
if not os.path.exists(image_path):
    os.makedirs(image_path)

def alert_object_detection(detections, last_detected_categories, new_image):
    detected_categories = [d.categories[0].label for d in detections]
    diff = set(detected_categories) - last_detected_categories
    if len(diff):
        logging.info(f'the detected objects are: {detected_categories}')
        last_detected_categories.update(diff)

        # capture the image of the new objects detected
        today = datetime.datetime.now().strftime("%m-%d-%y_%H%M%S")
        im = Image.fromarray(new_image)
        im.save(f"{image_path}/{today}.jpg")

    return last_detected_categories