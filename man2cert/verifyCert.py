# (c) 2019 Microchip Technology Inc. and its subsidiaries.
#
# Subject to your compliance with these terms, you may use Microchip software
# and any derivatives exclusively with Microchip products. It is your
# responsibility to comply with third party license terms applicable to your
# use of third party software (including open source software) that may
# accompany Microchip software.
#
# THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
# EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
# WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
# PARTICULAR PURPOSE. IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT,
# SPECIAL, PUNITIVE, INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE
# OF ANY KIND WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF
# MICROCHIP HAS BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE
# FORESEEABLE. TO THE FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL
# LIABILITY ON ALL CLAIMS IN ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED
# THE AMOUNT OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR
# THIS SOFTWARE.

import json
from base64 import b64decode, b16encode
from argparse import ArgumentParser
import jose.jws
from jose.utils import base64url_decode, base64url_encode
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
parser = ArgumentParser(
    description='Verify and decode secure element manifest'
)
parser.add_argument(
    '--manifest',
    help='Manifest file to process',
    nargs=1,
    type=str,
    required=True,
    metavar='file'
)
parser.add_argument(
    '--cert',
    help='Verification certificate file in PEM format',
    nargs=1,
    type=str,
    required=True,
    metavar='file'
)
args = parser.parse_args()
# List out allowed verification algorithms for the JWS. Only allows
# public-key based ones.
verification_algorithms = [
    'RS256', 'RS384', 'RS512', 'ES256', 'ES384', 'ES512'
]
# Load manifest as JSON
with open(args.manifest[0], 'rb') as f:
    manifest = json.load(f)
# Load verification certificate in PEM format
with open(args.cert[0], 'rb') as f:
    verification_cert = x509.load_pem_x509_certificate(
        data=f.read(),
        backend=default_backend()
    )
# Convert verification certificate public key to PEM format
verification_public_key_pem = verification_cert.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('ascii')
# Get the base64url encoded subject key identifier for the verification cert
ski_ext = verification_cert.extensions.get_extension_for_class(
    extclass=x509.SubjectKeyIdentifier
)
verification_cert_kid_b64 = base64url_encode(
    ski_ext.value.digest
).decode('ascii')
# Get the base64url encoded sha-256 thumbprint for the verification cert
verification_cert_x5t_s256_b64 = base64url_encode(
    verification_cert.fingerprint(hashes.SHA256())
).decode('ascii')
# Process all the entries in the manifest
for i, signed_se in enumerate(manifest):
    print('')
    print('Processing entry {} of {}:'.format(i+1, len(manifest)))
    print('uniqueId: {}'.format(
        signed_se['header']['uniqueId']
    ))
    # Decode the protected header
    protected = json.loads(
        base64url_decode(
            signed_se['protected'].encode('ascii')
        )
    )
    if protected['kid'] != verification_cert_kid_b64:
        raise ValueError('kid does not match certificate value')
    if protected['x5t#S256'] != verification_cert_x5t_s256_b64:
        raise ValueError('x5t#S256 does not match certificate value')
    # Convert JWS to compact form as required by python-jose
    jws_compact = '.'.join([
        signed_se['protected'],
        signed_se['payload'],
        signed_se['signature']
    ])
    # Verify and decode the payload. If verification fails an exception will
    # be raised.
    se = json.loads(
        jose.jws.verify(
            token=jws_compact,
            key=verification_public_key_pem,
            algorithms=verification_algorithms
        )
    )
    if se['uniqueId'] != signed_se['header']['uniqueId']:
        raise ValueError(
            (
                'uniqueId in header "{}" does not match version in' +
                ' payload "{}"'
            ).format(
                signed_se['header']['uniqueId'],
                se['uniqueId']
            )
        )
    print('Verified')
    print('SecureElement = ')
    print(json.dumps(se, indent=2))
    # Decode public keys and certificates
    try:
        public_keys = se['publicKeySet']['keys']
    except KeyError:
        public_keys = []
    for jwk in public_keys:
        print('Public key in slot {}:'.format(int(jwk['kid'])))
        if jwk['kty'] != 'EC':
            raise ValueError(
                'Unsupported {}'.format(json.dumps({'kty': jwk['kty']}))
            )
        if jwk['crv'] != 'P-256':
            raise ValueError(
                'Unsupported {}'.format(json.dumps({'crv': jwk['crv']}))
            )
        # Decode x and y integers
        # Using int.from_bytes() would be more efficient in python 3
        x = int(
            b16encode(base64url_decode(jwk['x'].encode('utf8'))),
            16
        )
        y = int(
            b16encode(base64url_decode(jwk['y'].encode('utf8'))),
            16
        )
        public_key = ec.EllipticCurvePublicNumbers(
            curve=ec.SECP256R1(),
            x=x,
            y=y
        ).public_key(default_backend())
        print(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('ascii'))
        # Decode any available certificates
        for cert_b64 in jwk.get('x5c', []):
            cert = x509.load_der_x509_certificate(
                data=b64decode(cert_b64),
                backend=default_backend()
            )
        print(cert.public_bytes(
            encoding=serialization.Encoding.PEM
        ).decode('ascii'))