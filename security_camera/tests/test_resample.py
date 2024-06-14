import os

import tensorflow as tf
import tensorflow_io as tfio

notebook_path = os.path.dirname(__file__) + '/../notebooks'


#@tf.function
def load_wav_16k_mono(filename):
    """
    Utility functions for loading audio files and making sure the sample rate is correct.
    Load a WAV file, convert it to a float tensor, resample to 16 kHz single-channel audio.
    """
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    # wav = wav / tf.int16.max
    return wav

def test_tfio():
    """
    error in tensorflow io lib on Apple chip. Test this until once the io lib is fixed.
    Error message:
    module '77ab628d7ad4acaa62f6bde524b9d631895821c9' has no attribute 'io_audio_resample'
    posted the issue in tensorflow io's github issue board: https://github.com/tensorflow/io/issues/1859
    :return:
    """
    testing_wav_file_name = notebook_path + '/miaow_16k.wav'
    testing_wav_data = load_wav_16k_mono(testing_wav_file_name)
    assert testing_wav_data is not None


