import json
from argparse import ArgumentParser
import jose.jws
from jose.utils import base64url_decode, base64url_encode
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from base64 import b64decode, b16encode
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from pathlib import Path

parser = ArgumentParser(description='extract device certificates from manifest without verification')
parser.add_argument('-m','--manifest',help='Manifest file to process',nargs=1,type=str,required=True,metavar='file')
args = parser.parse_args()


with open(args.manifest[0], 'rb') as f:
    manifest = json.load(f)

for i, signed_se in enumerate(manifest):
    serial=signed_se["header"]["uniqueId"]
    print(f'Serial: {serial}')
    # Decode the protected header
    protected = json.loads(base64url_decode(signed_se['protected'].encode('ascii')))
    jws_compact = '.'.join([signed_se['protected'],signed_se['payload'],signed_se['signature']])
    se = json.loads(jose.jws.verify(token=jws_compact,verify=False, key=None, algorithms=None))

    Path("./certs").mkdir(exist_ok=True)

    try:
        public_keys = se['publicKeySet']['keys']
    except KeyError:
        public_keys = []
    for jwk in public_keys:
        for cert_b64 in jwk.get('x5c', []):
            cert = x509.load_der_x509_certificate(data=b64decode(cert_b64),backend=default_backend())
            cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            
            #consider only the device cert if a chain is present.
            if ('sn'+serial).lower() == cn.lower():
                pemCert=(cert.public_bytes(encoding=serialization.Encoding.PEM).decode('ascii'))
                with open("./certs/"+serial+".cer", 'w') as f:
                    f.write(pemCert)
