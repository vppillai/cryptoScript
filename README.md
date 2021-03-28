# Security test Scripts

This repo contains a bunch of quick and dirty scripts that were written to meet very specific needs during the course of developing embedded projects. A lot of the code is a result of advanced google-fu and stack-overflow-ology.  So, no copyrights or guarantees.

Some of the items below are sample commands that can be issued with existing programs. 

|  Script Name   |                                                             Function                                                              |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| cert2header.py | Convert a certificate in PEM format into C header for use with embedded TLS stacks. Usage: python cert2header.py rootCert.cer     |
| key2header.py  | Convert a key in PEM format into C header for use with embedded TLS stacks. Usage: python key2header.py privateKey.key     |
| createCert.py  | Generate a self-signed certificate and key in PEM, DER and a C header file format.Can be used to spin up a local server for test. |
|scan ciphers    |`pysslscan scan --scan=server.ciphers --ssl2 --ssl3 --tls10 --tls11 --tls12 test.mosquitto.org:8883`|

## openssl test server with debug

```
openssl s_server -key ECC_prime256v1.key -cert ECC_prime256v1.cer -verify 2 -accept 8883 -debug -msg -CApath capath/ -state
```
