```sh
git clone msr-gryffindor@vs-ssh.visualstudio.com:v3/msr-gryffindor/PrivateAI/confonnx
cd confonnx

# Build and install client
PYTHON_VERSION=3.7 docker/client/build.sh
python3 -m pip install dist/Release/lib/python/confonnx-0.1.0-cp37-cp37m-linux_x86_64.whl

# Build and run server
docker/server/build.sh
MODEL_PATH=.../model/unet.onnx IMAGE_NAME=model-server docker/server/build_image.sh
docker run --rm --name model-server-test --device=/dev/sgx -p 8888:8888 model-server
```
