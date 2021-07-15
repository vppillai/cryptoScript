# Tool to extract device certificates from the TNGTLS manifest file

A tool to extract device certificates from the TNGTLS manifest file. Certificates will be written into a `certs` folder parallel to teh script. 

> **Note** verification is not performed by this script. Please refer to the script at the end of `TrustPlatform Manifest File Format` spec for an example of how to do it. A version of it is present in `verifyCert.py`

> The official manifest signer certs are under `Manifest signer cert - MCHP` in https://www.microchip.com/wwwproducts/en/ATECC608A-TNGTLS
