IMAGE ?= shining-channels

install:
	pip install -e .

figures:
	shining-run-all

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -v $(PWD)/data:/artifact/data -v $(PWD)/results:/artifact/results $(IMAGE)

.PHONY: install figures docker-build docker-run
