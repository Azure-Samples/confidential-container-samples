from io import BytesIO
import os
import json
from PIL import Image
import numpy as np
import base64

from confonnx.client import Client

input_image = np.asarray(Image.open('brain-segmentation-pytorch/assets/TCGA_CS_4944.png')) # HWC
input_image = np.transpose(input_image, (2, 0, 1)) # CHW
m, s = np.mean(input_image, axis=(1, 2)), np.std(input_image, axis=(1, 2))
x = (input_image - m.reshape(-1, 1, 1)) / s.reshape(-1, 1, 1)
x = x[np.newaxis, :, :, :].astype(np.float32) # BCHW
print(x.min(), x.max())

url = os.environ.get('URL', 'http://localhost:8888')
auth = None
password = os.environ.get('PASS')
if password:
    auth = {'user': 'api', 'pass': password}
client = Client(url=url, auth=auth)

outputs = client.predict({'input.1': x})
mask = outputs['186']
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
temp = BytesIO()
im.save(temp, format='png')
img_delineated = base64.b64encode(temp.getvalue()).decode('ascii')
with open('pred.png', 'wb') as f:
    f.write(temp.getvalue())

with open('confonnx_sgx_quote.bin', 'rb') as f:
    sgx_quote = base64.b64encode(f.read()).decode('ascii')
with open('confonnx_sgx_ehd.bin', 'rb') as f:
    sgx_ehd = base64.b64encode(f.read()).decode('ascii')

with open('pred.json', 'w') as f:
    json.dump({
        'img_delineated': img_delineated,
        'sgx_quote': sgx_quote,
        'sgx_ehd': sgx_ehd
    }, f, indent=2)
