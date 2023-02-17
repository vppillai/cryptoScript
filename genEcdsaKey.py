# Author: Vysakh P Pillai
# Date: 2023-02-17
# Description: Generate an ECDSA keypair

from ecdsa import SigningKey, SECP256k1

def generate_keypair():
    priKey = SigningKey.generate(curve=SECP256k1)
    open("private.pem", "wb").write(priKey.to_pem())
    pubKey = priKey.get_verifying_key()
    open("public.pem", "wb").write(pubKey.to_pem())
    print("Keys saved to private.pem and public.pem")