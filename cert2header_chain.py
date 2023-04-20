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

# Python script to accept a PEM certificate file and output a C header file including the full certificate chain
# Thw two a rduments passed to the script are a PEM certificate file and a folder containing other certificates in the chain
# The script will output a C header with the passed in certificate name as the header file name and header guard
# If all the certificates in the chain are in the same folder as the script, the second argument can be omitted
# If all certificates in the chain are not present, the script will output a warning and the chain will be incomplete
# the script should also include a comment in the header file with the number and details of certificates in the chain
# some of the certificates in the folder might already be a chain, the script should be able to process them
# cert2header.py implements this functionality for a single certificate file and does not include the chain in the header file 
# cert2header_chain.py implements this functionality for a single certificate file and includes the chain in the header file
# issuer is identified using the subject name of the certificate and the issuer name of the next certificate in the chain
# the script should be able to handle the case where the issuer name is not present in the next certificate in the chain


from string import Template
import binascii
import sys
import os
import OpenSSL.crypto as crypto
import re

def generate_chain(certName,cert,cert_folder):
    # generate list of certificates in the folder. consider only valid PEM files by looking in the contents
    cert_list = [f for f in os.listdir(cert_folder) if os.path.isfile(os.path.join(cert_folder, f)) and "-----BEGIN CERTIFICATE-----" in open(os.path.join(cert_folder, f)).read()]

    #pop certName from cert_list
    cert_list.remove(os.path.basename(certName))

    # parse all the certificates in the list and store in a dictionary
    cert_dict = {}
    for cert_file in cert_list:
        cert_dict[cert_file] = crypto.load_certificate(crypto.FILETYPE_PEM, open(os.path.join(cert_folder, cert_file)).read())
        
    cert_chain=[cert]

    # find the issuer of the current certificate in the list of certificates
    # if the issuer is found, add it to the chain and remove it from the list
    # if the issuer is not found, add the current certificate to the chain and continue
    # if the list is empty, break out of the loop
    while len(cert_dict) > 0:
        for cert_file in cert_dict:
            if cert.get_issuer().get_components() == cert_dict[cert_file].get_subject().get_components():
                cert_chain.append(cert_dict[cert_file])
                cert = cert_dict[cert_file]
                cert_dict.pop(cert_file)
                break
        else:
            cert_chain.append(cert)
            break

    # remove duplicate certificates from the chain
    cert_chain = list(dict.fromkeys(cert_chain))
    
    # print the certificate subject and issuer names for each certificate in the chain.
    for cert in cert_chain:
        print("Subject: " + cert.get_subject().CN)
        print("Issuer: " + cert.get_issuer().CN)
        print("")

    # If the last certificate in the chain is not self signed, pritn a warning 
    if cert_chain[-1].get_issuer().get_components() != cert_chain[-1].get_subject().get_components():
        print("WARNING: All certificates in the chain was not found in the folder. The chain is incomplete.")
    return cert_chain
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cert2header_chain.py <cert_file> <cert_folder>")
        sys.exit(1)

    cert_file = sys.argv[1]
    cert_folder = sys.argv[2]
    inCert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_file).read())
    cert_chain=generate_chain(cert_file,inCert,cert_folder)
    certSubject=inCert.get_subject().CN
    certSubject=re.sub(r"[^a-zA-Z0-9_]", "_", certSubject)
    certSubject=certSubject.strip("_")


    # generate the header file name from the certificate file name
    header_file = os.path.splitext(os.path.basename(cert_file))[0] 
    header_guard = "_"+certSubject + "_H_"

    certString=""
    #print certchain as PEM. Each line in the string should be wrapped in " and terminated with \n
    for cert in cert_chain:
        string=crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("UTF-8")
        string=string.replace("\n","\\n\"\n\"")
        string='"'+string.strip('"')
        string=f"/*{cert.get_subject().CN}*/\n"+string
        certString=certString+string

    # Header file template formatted string
    certHeaderTemplate=Template("""/* GENERATED CERTIFICATE CHAIN FOR $certSubject_raw FROM $cert_file */

#ifndef $header_guard
#define $header_guard

static const unsigned char $certSubject[] =$certString;

static const int sizeof_$certSubject = sizeof($certSubject);

#endif /*$header_guard*/
""")

with open(f"{certSubject}.h", 'w') as file: 
    file.write(certHeaderTemplate.substitute(header_guard=header_guard,certString=certString,certSubject=certSubject,cert_file=cert_file, certSubject_raw=inCert.get_subject().CN))
        