1.	Download and install https://mosquitto.org/files/binary/win64/mosquitto-2.0.11-install-windows-x64.exe
2.	Create a certs folder in the installation folder
3.	Create a certificate and key pair with 
```bash
  openssl ecparam -genkey -name prime256v1 -noout -out ECC_prime256v1.key
  MSYS_NO_PATHCONV=1 openssl req -new -x509 -key ECC_prime256v1.key -out ECC_prime256v1.cer -days 900000 -subj "/C=IN/ST=Kerala/L=Kollam/O=embeddedinn/CN=embeddedinn"
```
4.	Open mosquitto.conf from the mosquito installation folder and update it to

    ```config
    per_listener_settings true
        listener 1883
        allow_anonymous true
        allow_zero_length_clientid true
        connection_messages true

    listener 8883
        protocol mqtt
        allow_anonymous true
        allow_zero_length_clientid true
        connection_messages true
        certfile certs\ECC_prime256v1.cer
        keyfile certs\ECC_prime256v1.key
    ```
5.	`.\mosquitto.exe -c .\mosquitto.conf -v`

