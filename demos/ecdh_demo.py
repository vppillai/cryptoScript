"""
ecdh_demo.py
This script demonstrates the Elliptic Curve Diffie-Hellman (ECDH) key exchange protocol using the NIST384p curve.
It generates a shared secret between a server and a client, and checks if the shared secrets are the same.

Dependencies:
    cryptography
    ecdsa

The file performs the following operations to demo the use of ECDH:
1. C1 and C2 generate their own private keys
2. C1 and C2 generate their own public keys
3. C1 and C2 load the public keys of the other party
4. C1 and C2 generate the shared secret
5. C1 and C2 derive a key and an IV from the shared secret using HKDF
6. C1 encrypts a plaintext using AES CBC with the derived key and IV
7. C2 decrypts the ciphertext using AES CBC with the derived key and IV
8. C1 and C2 check if the decrypted plaintext is the same as the original plaintext

The mermaid diagram below shows the steps performed in this file is at :
https://mermaid.live/edit#pako:eNqNk01vwjAMhv9K5BNIHVpK-eqBS0HTDjsh7TBVQlnirRE07dJ0giH--0zDNiYoWy9x6sfva1nODmShEGKo8K1GI3GmxasVeWoYfaWwTktdCuNYwpmoWLLWSBfOLgDhCRD6fMJvptOEx-wODVrhkJVWvx_OFW5ZB6XKlpJ3j3B4gMPrcNhtVa6f11p61sdLiq_Kt1T89qCKBRr1T33-B93ef5UJi4pVKC061vHntfZbCs4cZkhj9EMU1Nn9I-v4xgOKLxi08aHnz_TnRtpt6Vi5Fto43FAvtBIZ2kN8cZQ_aXbm7bVOiI7y_1Bd0ksylCumX07cdcVcRuMROUIAOdpcaEUrvjuUpkC5HFOIKVTCrlJIzZ64ulQ01LnSrrAQv4h1hQGI2hWLrZEQO1vjF3R8I98UrT_EO9hAHPF-rz-Joskg4uE4im6jALYQD3sD3h8NeTQcjceTSX-wD-CjKEiBB4CN5YN_hs1rbBSfmnzjsP8EyNQkFw

Author: Vysakh P Pillai
"""

from ecdsa import ECDH, NIST384p # NIST256p, NIST384p, NIST521p

#operation on Server to generate public key
ecdh_c1 = ECDH(curve=NIST384p)
ecdh_c1.generate_private_key()
public_key_c1 = ecdh_c1.get_public_key() # this is the public key that will be sent to the client


#operation on Client to generate public key
ecdh_c2 = ECDH(curve=NIST384p)
ecdh_c2.generate_private_key()
public_key_c2 = ecdh_c2.get_public_key() # this is the public key that will be sent to the server

# operation on Server to load the received public key from the client
ecdh_c1.load_received_public_key_pem(public_key_c2.to_pem().decode())
# operation on Client to load the received public key from the server
ecdh_c2.load_received_public_key_pem(public_key_c1.to_pem().decode())

# operation on Server to generate the shared secret
secret_c1 = ecdh_c1.generate_sharedsecret_bytes()
# operation on Client to generate the shared secret
secret_c2 = ecdh_c2.generate_sharedsecret_bytes()

# check if the shared secret is the same
# length of secret will be the same as the length of the curve prime ; 32 for NIST256p, 48 for NIST384p, 66 for NIST521p
if (secret_c1 == secret_c2):
    print("Shared Secret is the same")
else:
    print("Shared Secret is different")
    exit()

#############################################################################################################################
# use HKDF to derive a key and AES IV from the shared secret. use sha-384 HKDF as hash function
from cryptography.hazmat.primitives import hashes as h
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

# Server: derive a key that will be used in AES CBC
key_hkdf_c1 = HKDF(
    algorithm=h.SHA384(),
    length=32,
    salt=None, # if a salt is used, it needs to be handled in the same way on both sides
    info=b'',
    backend=default_backend()
)
key_c1 = key_hkdf_c1.derive(secret_c1)

# Server: Derive an IV that will be used in AES CBC
IV_hkdf_c1 = HKDF(
    algorithm=h.SHA384(),
    length=16, # AES 128
    salt=None, # if a salt is used, it needs to be handled in the same way on both sides
    info=b'',
    backend=default_backend()
)
IV_c1 = IV_hkdf_c1.derive(secret_c1)

# Client: derive a key that will be used in AES CBC
key_hkdf_c2 = HKDF(
    algorithm=h.SHA384(),
    length=32, # AES 256
    salt=None, # if a salt is used, it needs to be handled in the same way on both sides
    info=b'',
    backend=default_backend()
)
key_c2 = key_hkdf_c2.derive(secret_c2)

# Client derive an IV that will be used in AES CBC
IV_hkdf_c2 = HKDF(
    algorithm=h.SHA384(),
    length=16, # AES 128
    salt=None, # if a salt is used, it needs to be handled in the same way on both sides
    info=b'',
    backend=default_backend()
)
IV_c2 = IV_hkdf_c2.derive(secret_c2)


if(key_c1 == key_c2):
    print("HKDF Keys are the same on both the sides")
else:
    print("HKDF Keys are different on both the sides")
    exit()

if(IV_c1 == IV_c2):
   print("HKDF IVs are the same on both the sides")
else:
   print("HKDF IVs are different on both the sides")
   exit()

#############################################################################################################################

# aes encrypt plaintext with key_c1 and decrypt with key_c2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

plaintext = b"Hello World"
# AES CBC needs padding to be a multiple of 128 bits
# PKCS7 is a padding scheme. The value of each added byte is the number of bytes added
padder = padding.PKCS7(128).padder()
padded_data = padder.update(plaintext) + padder.finalize()

# iv needs to be the same on both sides. to share it, it can be prepended to the ciphertext
cipher_c1 = Cipher(algorithms.AES(key_c1), modes.CBC(IV_c1), backend=default_backend())
encryptor = cipher_c1.encryptor()
ciphertext = encryptor.update(padded_data) + encryptor.finalize()

cipher_c2 = Cipher(algorithms.AES(key_c2), modes.CBC(IV_c2), backend=default_backend())
decryptor = cipher_c2.decryptor()
decryptedtext = decryptor.update(ciphertext) + decryptor.finalize()

# remove padding
unpadder = padding.PKCS7(128).unpadder()
data = unpadder.update(decryptedtext) + unpadder.finalize()

if (plaintext == data):
    print("Encryption and Decryption is successful")
else:
    print("Encryption and Decryption is not successful")
    exit()

