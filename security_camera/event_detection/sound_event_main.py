import argparse
import datetime
import logging
import os
import queue
import sys
import tempfile

import sounddevice as sd
import soundfile as sf

import logging_utils
from sound_inference import SoundEventDetector

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tensorflow").addHandler(logging.NullHandler(logging.ERROR))

logging_utils.init_logging()


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def parse():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        'filename', nargs='?', metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        'channels', type=int, default=[1], nargs='*', metavar='CHANNEL',
        help='input channels to use (default: the first)')
    parser.add_argument(
        '-r', '--samplerate', type=float, help='sampling rate of audio device')

    parser.add_argument(
        '--overlap', type=float, default=0.5,
        help='how much overlap between consequctive windows to classify')

    args = parser.parse_args()
    if any(c < 1 for c in args.channels):
        parser.error('argument CHANNEL: must be >= 1')

    return parser, args


def start_streaming(args):
    mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
    audio_queue = queue.Queue()
    sound_event_detector = SoundEventDetector(args.samplerate, lite=True)

    def audio_callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            logging.error(status, file=sys.stderr)

        audio_queue.put(indata[:, mapping])
        # logging.debug(f'n_frames: {frames}, indata shape: {indata.shape}')

    try :
        with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
                          channels=len(args.channels), subtype=args.subtype) as file:
            with sd.InputStream(samplerate=args.samplerate, device=args.device,
                                channels=max(args.channels), callback=audio_callback) as stream:
                logging.debug(f'Stream start on input device {args.device} {stream}.')

                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)

                # streaming inference using classification-tflite requires 0.975 second waveform
                # https://www.kaggle.com/models/google/yamnet/tfLite/classification-tflite
                waveform_len = int(0.975 * args.samplerate)
                sound_event_detector.stream_infer(audio_queue, file, waveform_len)
    except KeyboardInterrupt:
        logging.info('\nRecording finished: ' + repr(args.filename))
        parser.exit(0)
    except Exception as e:
        logging.exception(e)
        parser.exit(type(e).__name__ + ': ' + str(e))

    logging.info('Stopped.')

if __name__ == '__main__':

    sound_clips_dir = os.path.dirname(__file__) + '/../sound_clips'
    if not os.path.exists(sound_clips_dir):
        os.makedirs(sound_clips_dir)

    parser, args = parse()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    # initialize arguments with default values
    if args.device is None:
        args.device = sd.query_devices(args.device, 'input')['name']
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])
        logging.info(f'The input device is {args.device} and its samplerate is {args.samplerate}')
    if args.filename is None:
        today = datetime.datetime.now().strftime("%m-%d-%y")
        args.filename = tempfile.mktemp(prefix=f'rec_{today}_', suffix='.wav', dir=sound_clips_dir)

    start_streaming(args)