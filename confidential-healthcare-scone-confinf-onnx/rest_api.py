import sys
import os
import json
import random
from hashlib import sha256
import base64
from io import BytesIO

from PIL import Image
import numpy as np
from cffi import FFI
import requests
from confonnx.client import Client

from flask import Flask, request
from flask_restful import Resource, Api
import redis

sys.path.insert(0, os.path.dirname(__file__))

letsencrypt_cert = "/fspf/encrypted-files/fullchain.pem"
letsencrypt_key = "/fspf/encrypted-files/privkey.pem"

if os.path.exists(letsencrypt_cert):
    private_key_path = "/fspf/encrypted-files/privkey.pem"
    public_key_path = "/fspf/encrypted-files/fullchain.pem"
    print('Using Lets Encrypt cert')
else:
    private_key_path = "/tls/flask.key"
    public_key_path = "/tls/flask.crt"

app = Flask(__name__)

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

api = Api(app)

# Setup redis instance.
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
db = redis.StrictRedis(
   host=REDIS_HOST,
   port=REDIS_PORT,
   ssl=True,
   ssl_keyfile='/tls/client.key',
   ssl_certfile='/tls/client.crt',
   ssl_cert_reqs="required",
   ssl_ca_certs='/tls/redis-ca.crt')

# Test connection to redis (break if the connection fails).
db.info()

# Attestation
def get_sgx_report(public_key_path):
    with open(public_key_path, 'rb') as f:
        public_key = f.read()
    ffi = FFI()
    ffi.cdef("""
    int scone_sgx_report_get(
        const unsigned char *report_data, 
        const unsigned char *target_info,
        unsigned char *report);
    """)
    C = ffi.dlopen("/libreport.so")

    sgx_report_data = sha256(public_key).digest() + bytes(32)
    sgx_report = bytes(432)
    sgx_report_cdata = ffi.from_buffer("unsigned char[]", sgx_report)
    print('Calling scone_sgx_report_get()')
    res = C.scone_sgx_report_get(sgx_report_data, ffi.NULL, sgx_report_cdata)
    if res != 0:
        print('Error retrieving SGX report')

    return {
        "sgx_quote": base64.b64encode(sgx_report).decode(),
        "sgx_ehd": base64.b64encode(public_key).decode()
    }

def convert_to_maa_token(sgx_quote, sgx_ehd):
    # Note: sgx_quote is assumed to be an OE report.

    app_id = os.environ["AZ_APP_ID"]
    app_pwd = os.environ["AZ_APP_PWD"]

    r = requests.post("https://login.microsoftonline.com/common/oauth2/token", data={
        "grant_type": "client_credentials",
        "client_id": app_id,
        "client_secret": app_pwd,
        "resource":"https://attest.azure.net"
    })
    r.raise_for_status()
    aad_token = r.json()["access_token"]
    r = requests.post("https://sharedeus.eus.test.attest.azure.net/attest/Tee/OpenEnclave?api-version=2018-09-01-preview", json={
        "Quote": sgx_quote,
        "EnclaveHeldData": sgx_ehd
    }, headers={"Authorization": f"Bearer {aad_token}"})
    r.raise_for_status()
    jwt = r.json()
    return jwt

sgx_report = get_sgx_report(public_key_path)

# Inference
assert 'CONFONNX_DUMP_QUOTE' in os.environ

CONFONNX_URL = os.environ.get("CONFONNX_URL", "http://127.0.0.1:8888")
CONFONNX_API_KEY = os.environ.get("CONFONNX_API_KEY")
auth = None
if CONFONNX_API_KEY:
    auth = {'user': 'api', 'pass': CONFONNX_API_KEY}
# In a production scenario, the keyword arguments enclave_signing_key 
# or enclave_hash should be specified to verify the enclave identity.
confonnx_client = Client(url=CONFONNX_URL, auth=auth)

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

def run_inference(input_file):
    input_image = np.asarray(Image.open(input_file)) # HWC
    input_image = np.transpose(input_image, (2, 0, 1)) # CHW
    m, s = np.mean(input_image, axis=(1, 2)), np.std(input_image, axis=(1, 2))
    x = (input_image - m.reshape(-1, 1, 1)) / s.reshape(-1, 1, 1)
    x = x[np.newaxis, :, :, :].astype(np.float32) # BCHW

    outputs = confonnx_client.predict({'input.1': x})
    mask = outputs['186']

    image = gray2rgb(input_image[1].astype(float)) # channel 1 is for FLAIR
    image = outline(image, mask[0, 0], color=[255, 0, 0])
    im = Image.fromarray(image)
    temp = BytesIO()
    im.save(temp, format='png')
    img_delineated = base64.b64encode(temp.getvalue()).decode('ascii')

    # read quote and enclave-held data dumped to disk
    with open('confonnx_sgx_quote.bin', 'rb') as f:
        sgx_quote = base64.urlsafe_b64encode(f.read()).decode('ascii')
    with open('confonnx_sgx_ehd.bin', 'rb') as f:
        sgx_ehd = base64.urlsafe_b64encode(f.read()).decode('ascii')
    
    maa_token = convert_to_maa_token(sgx_quote, sgx_ehd)

    return {
            'img_delineated': img_delineated,
            'sgx_quote': sgx_quote,
            'sgx_ehd': sgx_ehd,
            'maa_token': maa_token
        }

class SGXReport(Resource):
    def get(self):
        return sgx_report

class Patient(Resource):
    def get(self, patient_id):
        patient_data = db.get(patient_id)
        if patient_data is not None:
            decoded_data = json.loads(patient_data.decode('utf-8'))
            decoded_data["id"] = patient_id
            return decoded_data
        return {"error": "unknown patient_id"}, 404

    def post(self, patient_id):
        if db.exists(patient_id):
            return {"error": "already exists"}, 403
        else:
            # convert patient data to binary.
            patient_data = json.dumps({
            "fname": request.form['fname'],
            "lname": request.form['lname'],
            "address": request.form['address'],
            "city": request.form['city'],
            "state": request.form['state'],
            "ssn": request.form['ssn'],
            "email": request.form['email'],
            "dob": request.form['dob'],
            "contactphone": request.form['contactphone'],
            "drugallergies": request.form['drugallergies'],
            "preexistingconditions": request.form['preexistingconditions'],
            "dateadmitted": request.form['dateadmitted'],
            "insurancedetails": request.form['insurancedetails'],
            "score": random.random()
            }).encode('utf-8')
            try:
                db.set(patient_id, patient_data)
            except Exception as e:
                print(e)
                return {"error": "internal server error"}, 500
            patient_data = json.loads(patient_data.decode('utf-8'))
            patient_data["id"] = patient_id
            return patient_data

class Delineate(Resource):
    def post(self):
        input_file = request.files['img'].stream
        result = run_inference(input_file)
        return result

api.add_resource(Patient, '/patient/<string:patient_id>')
api.add_resource(Delineate, '/delineate')
api.add_resource(SGXReport, '/sgx_report')


if __name__ == '__main__':
    app.debug = False
    ssl_context = (public_key_path, private_key_path)
    app.run(host='0.0.0.0', port=4996, threaded=True, ssl_context=ssl_context)
