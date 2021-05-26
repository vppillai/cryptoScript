# Security test Scripts

This repo contains a bunch of quick and dirty scripts that were written to meet very specific needs during the course of developing embedded projects. A lot of the code is a result of advanced google-fu and stack-overflow-ology.  So, no copyrights or guarantees.

Some of the items below are sample commands that can be issued with existing programs. 

|  Script Name   |                                                             Function                                                              |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| cert2header.py | Convert a certificate in PEM format into C header for use with embedded TLS stacks. Usage: python cert2header.py rootCert.cer     |
| key2header.py  | Convert a key in PEM format into C header for use with embedded TLS stacks. Usage: python key2header.py privateKey.key            |
| createCert.py  | Generate a self-signed certificate and key in PEM, DER and a C header file format.Can be used to spin up a local server for test. |
| scan ciphers   |`pysslscan scan --scan=server.ciphers --ssl2 --ssl3 --tls10 --tls11 --tls12 test.mosquitto.org:8883`                               |
| httpsServer    |A simple python script that can be used as a test HTTPs server                                                                     |

## create self signed test certificates with

```bash
openssl ecparam -genkey -name prime256v1 -noout -out ECC_prime256v1.key
MSYS_NO_PATHCONV=1 openssl req -new -x509 -key ECC_prime256v1.key -out ECC_prime256v1.cer -days 900000 -subj "/C=IN/ST=Kerala/L=Kollam/O=embeddedinn/CN=embeddedinn"
```

Curves can be listed with `openssl ecparam --list_curves`

> Note: MSYS_NO_PATHCONV is set to prevent gitbash from covnerting `/C` to path


## openssl test server with debug

```bash
openssl s_server -key ECC_prime256v1.key -cert ECC_prime256v1.cer -verify 2 -accept 8883 -debug -msg -CApath capath/ -state
```

