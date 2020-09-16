#!/bin/bash
set -ex

git clone https://github.com/mateuszbuda/brain-segmentation-pytorch || true
PYTHONPATH=$(pwd)/brain-segmentation-pytorch python convert_onnx.py
