import csv
import datetime
import logging
import os

import numpy as np
import scipy

try:
  # Import TFLite interpreter from tflite_runtime package if it's available.
  from tflite_runtime.interpreter import Interpreter
except ImportError:
  # If not, fallback to use the TFLite interpreter from the full TF package.
  import tensorflow as tf
  Interpreter = tf.lite.Interpreter

OVERLAP = 0.1
DETECTION_MIN_THRESHOLD = 0.2

CLASS_NAME_SILENCE = 'Silence'
MODEL_DIR = os.path.dirname(__file__) + '/../models'


def extract_class_names_from_csv(csv_filename):
  """Returns list of class names corresponding to score vector."""
  class_names = []
  with open(csv_filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      class_names.append(row['display_name'])

  return class_names


class SoundEventDetector():
    def __init__(self, samplerate, lite):
        self.samplerate = samplerate
        self.lite = lite
        self.detected_event = None

        if self.lite:
            model_path = f'{MODEL_DIR}/yamnet_tflite/1.tflite'
            self.interpreter = Interpreter(model_path)
            self.waveform_input_index = self.interpreter.get_input_details()[0]['index']
            self.scores_output_index = self.interpreter.get_output_details()[0]['index']
            logging.info(f'Successfully loaded the YAMNet tflite model.')
        else:
            model_path = f'{MODEL_DIR}/yamnet'
            logging.info(f'Loading the YAMNet model from the local file system...')
            self.model = tf.saved_model.load(model_path)
            logging.info(f'Successfully loaded the model.')

        class_map_csv = f'{MODEL_DIR}/yamnet_class_map.csv'
        self.class_names = extract_class_names_from_csv(class_map_csv)
        logging.info(f'Successfully loaded the label file with {len(self.class_names)} labels.')

    def get_top_n_classes(self, scores, n=5):
        top_class_indices = np.argsort(scores)[::-1][:n]
        classes_with_scores = [(self.class_names[top_class_indices[x]], scores[top_class_indices[x]]) for x in range(n)]
        logging.debug(f'The top sound classes detected are: {classes_with_scores}')
        return classes_with_scores

    def infer(self, waveform, verbose=False):
        """
        infer the given waveform using a standard model.
        :param waveform: the waveform data to infer, type is float64 numpy array
        :param verbose: whether log top 5 predictions
        :return: the inferred class and its probability
        """
        scores, embeddings, spectrogram = self.model(waveform)
        # logging.debug(f'scores shape {scores.shape}, embedding shape {embeddings.shape}, spectrogram shape {spectrogram.shape}')

        # get the mean score/probability of the measured time window.
        mean_scores = np.mean(scores, axis=0)
        top_class_index = mean_scores.argmax()
        inferred_class, probability = self.class_names[top_class_index], mean_scores[top_class_index]
        logging.debug(f'The main sound is: {inferred_class}, probability: {probability}')

        if verbose:
            self.get_top_n_classes(mean_scores)

        return inferred_class, probability

    def infer_lite(self, waveform, verbose=False):
        """
        infer the given waveform using tflite model. The wavefrom has to be 0.975 seconds long, which is 15600 steps
        of an 16 kHz sample rate
        :param waveform: the waveform data to infer, type is float32 numpy array
        :param verbose: whether log top 5 predictions
        :return: the inferred class and its probability
        """
        waveform = np.float32(waveform)
        self.interpreter.resize_tensor_input(self.waveform_input_index, [waveform.size], strict=True)
        self.interpreter.allocate_tensors()
        self.interpreter.set_tensor(self.waveform_input_index, waveform)
        self.interpreter.invoke()
        scores = np.squeeze(self.interpreter.get_tensor(self.scores_output_index))

        inferred_class, probability = self.class_names[scores.argmax()], scores[scores.argmax()]
        logging.debug(f'The main sound is: {inferred_class}, probability: {probability}')

        if verbose:
            self.get_top_n_classes(scores)

        return inferred_class, probability

    def ensure_sample_rate(self, original_sample_rate, waveform, desired_sample_rate=16000):
        """
        Verify and convert a loaded audio is on the proper sample_rate (16K), otherwise it would affect YAMNet model's
        performance.
        """
        if original_sample_rate != desired_sample_rate:
            desired_length = int(round(float(len(waveform)) / original_sample_rate * desired_sample_rate))
            waveform = scipy.signal.resample(waveform, desired_length)

        return desired_sample_rate, waveform

    def log_events(self, inferred_class, probability):
        timestamp = datetime.datetime.now()
        if inferred_class:
            if not self.detected_event:
                # new event after silence
                logging.info(f'{inferred_class} EVENT on {timestamp} with probability {probability}')
            elif self.detected_event != inferred_class:
                # different event
                logging.info(
                    f'{self.detected_event} EVENT off, and {inferred_class} EVENT on {timestamp} with probability {probability}')
            self.detected_event = inferred_class
        else:
            if self.detected_event:
                logging.info(f'{self.detected_event} EVENT off {timestamp}')
                self.detected_event = None

    def stream_infer(self, audio_queue, output_sound_file, window_size):
        """
        With the given audio stream queue, continuously infer the wave data in the sliding window for sound events.
        Log the event on and off, and record the detected sound.
        The sliding window has the stride size of 0.1 overlapping.
        :param audio_queue: the stream audio queue
        :param output_sound_file the sound file recording the event capture
        :param window_size: the buffer size before feeding the sound clip to the model for inferencing
        :return: None
        """
        audio_buffer = np.zeros(shape=(window_size,))
        stride_size = window_size * (1 - OVERLAP)

        new_samples = 0
        detected_event = None

        while True:
            data = np.squeeze(audio_queue.get())
            len_data = data.size

            # move existing data forward towards the beginning of the time axis.
            audio_buffer = np.roll(audio_buffer, -len_data, axis=0)
            # append the new data to the end of the buffer
            audio_buffer[-len_data:] = data
            new_samples += len_data
            # check if we have received enough new data to do new classification
            if new_samples >= stride_size:
                new_samples = 0  # reset for the next window

                # inference the waveform
                _, waveform = self.ensure_sample_rate(self.samplerate, audio_buffer)
                if self.lite:
                    inferred_class, probability = self.infer_lite(waveform, verbose=True)
                else:
                    inferred_class, probability = self.infer(waveform, verbose=True)

                # fine tune the inferred_class
                if inferred_class == CLASS_NAME_SILENCE or probability < DETECTION_MIN_THRESHOLD:
                    inferred_class = None

                # check event on/off and log accordingly. if the even is detected, capture the sound to the file.
                self.log_events(inferred_class, probability)
                if inferred_class:
                    output_sound_file.write(audio_buffer)



