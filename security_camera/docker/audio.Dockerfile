# dockerfile for the audio component
FROM amd64/python:3.10-slim-bullseye

RUN apt-get -y update && apt-get install -y libportaudio2

ENV ROBOT_HOME=/home/robot
WORKDIR $ROBOT_HOME/app
RUN groupadd -g 4000 robot && useradd -u 2000 -m robot -g robot -d $ROBOT_HOME && usermod -g 4000 robot
RUN chown -R robot:robot /run $ROBOT_HOME

USER robot

COPY build/requirements.txt $ROBOT_HOME/requirements.txt

ENV PYTHONPATH $ROBOT_HOME/app

RUN python3 -m pip install --user --no-cache-dir --no-compile -r $ROBOT_HOME/requirements.txt
ENV PATH="/home/robot/.local/bin:$PATH"
COPY build/app $ROBOT_HOME/app

CMD ["python", "event_detection/sound_event_main.py"]
