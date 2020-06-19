# Author Vysakh P Pillai
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from string import Template
import binascii
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import sys

def make_sublist_group(lst: list, grp: int) -> list:
    """
    Group list elements into sublists.
    make_sublist_group([1, 2, 3, 4, 5, 6, 7], 3) = [[1, 2, 3], [4, 5, 6], 7]
    """
    return [lst[i:i+grp] for i in range(0, len(lst), grp)]

def do_convension(content: bytes) -> str:
    hexstr = binascii.hexlify(content).decode("UTF-8")
    hexstr = hexstr.upper()
    array = ["0x" + hexstr[i:i + 2] + "" for i in range(0, len(hexstr), 2)]
    array = make_sublist_group(array, 10)
    
    return sum(len(a) for a in array ), "\n".join([", ".join(e) + ", " for e in array])


#Creating a Certificate


with open(sys.argv[1], "rb") as certfile:
    certData=certfile.read()
    cert = x509.load_pem_x509_certificate(certData, default_backend())
    
cert_der = cert.public_bytes(serialization.Encoding.DER)
cer_length , cerArray=do_convension(cert_der)

certHeaderTemplate=Template("""
/*GENERATED FILE*/

#ifndef _CERTS_TEST_H_
#define _CERTS_TEST_H_

static const unsigned char ca_cert_der[] =
{
$caCert
};

/* size is $ceCertSize */
static const int sizeof_ca_cert_der = sizeof(ca_cert_der);

#endif /*_CERTS_TEST_H_*/
""")

with open('cert_header.h', 'w') as file: 
    file.write(certHeaderTemplate.substitute(caCert=cerArray,ceCertSize=cer_length))
