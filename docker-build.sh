#!/bin/bash

docker buildx build --platform linux/amd64,linux/arm64 -t eitansuez/fake-llm:2.4 --push .

