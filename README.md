# Security test Scripts

This repo contains a bunch of quick and dirty scripts that were written to meet very specific needs during the course of developing embedded projects. A lot of the code is a result of advanced google-fu and stack-overflow-ology.  So, no copyrights or guarantees.

|  Script Name   |                                                             Function                                                              |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| cert2header.py | Convert a certificate in PEM format into C header for use with embedded TLS stacks. Usage: python cert2header.py rootCert.cer     |
| createCert.py  | Generate a self-signed certificate and key in PEM, DER and a C header file format.Can be used to spin up a local server for test. |