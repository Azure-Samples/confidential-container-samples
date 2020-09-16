# https://pytorch.org/hub/mateuszbuda_brain-segmentation-pytorch_unet/

from PIL import Image
import torch
import numpy as np
import onnx
import onnxruntime as ort

from unet import UNet

dummy_input = torch.randn(1, 3, 256, 256)

unet = UNet(in_channels=3, out_channels=1)
weights = torch.load('brain-segmentation-pytorch/weights/unet.pt', map_location=torch.device('cpu'))
unet.load_state_dict(weights)

# https://pytorch.org/docs/stable/onnx.html
torch.onnx.export(unet, dummy_input, "unet.onnx", verbose=True)

model = onnx.load("unet.onnx")

# Check that the IR is well formed
onnx.checker.check_model(model)

# Print a human readable representation of the graph
onnx.helper.printable_graph(model.graph)

ort_session = ort.InferenceSession('unet.onnx')

input_image = np.asarray(Image.open('brain-segmentation-pytorch/assets/TCGA_CS_4944.png')) # HWC
input_image = np.transpose(input_image, (2, 0, 1)) # CHW
m, s = np.mean(input_image, axis=(1, 2)), np.std(input_image, axis=(1, 2))
x = (input_image - m.reshape(-1, 1, 1)) / s.reshape(-1, 1, 1)
x = x[np.newaxis, :, :, :].astype(np.float32) # BCHW
print(x.min(), x.max())

outputs = ort_session.run(None, {'input.1': x})

mask = outputs[0]
print(mask.shape) # 1, 1, 256, 256

def gray2rgb(image):
    w, h = image.shape
    image += np.abs(np.min(image))
    image_max = np.abs(np.max(image))
    if image_max > 0:
        image /= image_max
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = image * 255
    return ret


def outline(image, mask, color):
    mask = np.round(mask)
    yy, xx = np.nonzero(mask)
    for y, x in zip(yy, xx):
        if 0.0 < np.mean(mask[max(0, y - 1) : y + 2, max(0, x - 1) : x + 2]) < 1.0:
            image[max(0, y) : y + 1, max(0, x) : x + 1] = color
    return image

image = gray2rgb(input_image[1].astype(float)) # channel 1 is for FLAIR
image = outline(image, mask[0, 0], color=[255, 0, 0])
im = Image.fromarray(image)
im.save("pred.png")
