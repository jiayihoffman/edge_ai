#!/bin/bash

IMAGE_NAME=sound_event
PROJECT_NAME=${DOCKER_REGISTRY:-localhost:5000/robot}

GIT_ROOT=$(dirname $0)/..

function usage {
  echo "usage: $SCRIPT_NAME [command]"
  echo "  commands:"
  echo "    build: build image only"
  echo "    build-push: build and push the image"
  echo "    push: push image only"
  echo "    clean: clean the output from the build"
  exit 1
}

function build_setup {
  mkdir -p build/
  mkdir -p build/app
  mkdir -p build/app/models

  cp ${GIT_ROOT}/requirements.txt ./build
  cp -r ${GIT_ROOT}/event_detection ./build/app/event_detection
  cp -r ${GIT_ROOT}/object_detection ./build/app/object_detection
  cp -r ${GIT_ROOT}/models/yamnet_tflite ./build/app/models/yamnet_tflite
  cp ${GIT_ROOT}/models/yamnet_class_map.csv ./build/app/models
  cp ${GIT_ROOT}/models/efficientdet_lite3.tflite ./build/app/models

  find ./build/app/ -path '*/__pycache__*' -delete
  find ./build/app/ -path '*/.DS_Store*' -delete

  if [ -z "$IMAGE_LABEL" ] ; then
    IMAGE_LABEL=$(date +"%Y-%m-%dT%H-%M-%S")
    echo "Set image label to $IMAGE_LABEL"
  fi
  echo $IMAGE_LABEL > ./build/LABEL.txt
}

function build_teardown {
  echo rm -rf ./build
  rm -rf ./build
}

function build {
  echo "Building $IMAGE_NAME image"
  docker build --tag $PROJECT_NAME/$IMAGE_NAME:$IMAGE_LABEL --file $GIT_ROOT/docker/audio.Dockerfile .
  echo "Built"
}

function push {
  echo ""
  echo "Pushing $PROJECT_NAME/$IMAGE_IMAGE_NAME:$IMAGE_LABEL image"
  docker push $PROJECT_NAME/$IMAGE_IMAGE_NAME:$IMAGE_LABEL
  echo "Pushed"
}

# run functions for the given input
case $1 in
  build)
      build_setup
      # build
      ;;
  push)
      build_setup
      push
      ;;
  build-push)
      build_setup
      build
      push
      ;;
  clean)
    build_teardown
    ;;
  *)
    usage
    exit 1
    ;;
  esac
    

