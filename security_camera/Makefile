.PHONY init:
init:
	pip install -r requirements.txt

.PHONY clean:
clean:
	./docker/build.sh clean

.PHONY build:
build: clean
	./docker/build.sh build


