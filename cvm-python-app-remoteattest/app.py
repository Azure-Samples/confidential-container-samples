import subprocess
import os
import base64
import jwt
import json

# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "0.0.0.0"
serverPort = 8081

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        sample_dataset = {
                    "id": "bigqueryproject:datasetname",
                    "datasetReference": {
                        "datasetId": "datasetname",
                        "projectId": "bigqueryproject"
                    }
                }
        #self.wfile.write(json.dumps({"kind": "bigquery#datasetList", "datasets": [sample_dataset]}).encode("utf-8"))
        #self.wfile.write(bytes("<html><head><title>CVM Attestation Report</title></head>", "utf-8"))
        #self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        #self.wfile.write(bytes("<body>", "utf-8"))
        # run the CMD here and return the details
        #child = subprocess.Popen(['ls','-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #child = os.popen('sudo', './AttestationClient')
        #child = poppen('sudo', './AttestationClient');
        #self.wfile.write(bytes("<p>This is an example web server from Amar Gowda</p>", "utf-8"))
        p = subprocess.Popen(['./AttestationClient'], shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)
        #print(p.stdout.read())
        g = str(p.stdout.read())
        #g= base64.b64
        g = g.replace("b'","")
        g = g.replace("'","")
        #print(g)
        #res = g.split(".", 1)[1]
        res = g.split(".")
        l = len(res) 
        if  l == 3:
            #now we have a fully formed JWT perform the decode and split
            print("JWT Token length Found ", l)
            decoded = jwt.decode(g, options={"verify_signature": False})
            print (decoded)
            self.wfile.write(json.dumps(decoded).encode("utf-8"))

            #j = str(decoded, "utf-8")
           # self.wfile.write(bytearray(decoded, "utf-8"))
        else:
            self.wfile.write(json.dumps({"error": "JWT was not formed properly"}).encode("utf-8"))
        #print(res)
        #work on decode logic here

        #decodedBytes =  base64.urlsafe_b64decode(res)
        #decodedStr = str(decodedBytes, "utf-8")
        #print(decodedStr)

        
        #self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")