# Define environment variables
LIBOQS_VERSION ?= 0.12.0
LIBOQS_DIR ?= liboqs
OQS_PROVIDER_VERSION ?= 0.8.0
OQS_PYTHON_VERSION ?= 0.12.0
OPENSSL_VERSION ?= 3.4.1

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PROVIDER_STRING := -provider-path ${MAKEFILE_DIR}/${LIBOQS_DIR}-provider -provider oqsprovider -provider default
TEST_OPENSSL := LD_LIBRARY_PATH=${MAKEFILE_DIR}/openssl/lib64 ${MAKEFILE_DIR}/openssl/bin/openssl


# Define the virtual environment directory
VENV_DIR ?= venv

OPENSSL_TEST_DIR ?= test_openssl

# Targets
.PHONY: all build provider_test python_test clean

all: build test

# package:
# 	mkdir -p ../../.././sec_jtag_api/sec_jtag_api_py/liboqs/
# 	cp genoqs.sh liboqs-python_0.10.0.patch Makefile README.md  ../../.././sec_jtag_api/sec_jtag_api_py/liboqs/

build:
	@echo "Running genoqs.sh..."
	LIBOQS_VERSION=$(LIBOQS_VERSION) \
	LIBOQS_DIR=$(LIBOQS_DIR) \
	OQS_PROVIDER_VERSION=$(OQS_PROVIDER_VERSION) \
	OQS_PYTHON_VERSION=$(OQS_PYTHON_VERSION) \
	OPENSSL_VERSION=$(OPENSSL_VERSION) \
	ROOT_DIR=${MAKEFILE_DIR} \
	./genoqs.sh

test_provider: build
	@echo "Running tests..."
	# Run ctest in the provider source directory
	cd ${LIBOQS_DIR}-provider-src && ctest --test-dir _build && cd ..

test_python: 
	# Create a Python virtual environment
	python3 -m venv ${VENV_DIR}
	# Install the package in the venv
	cd ${LIBOQS_DIR}-python-src && ../${VENV_DIR}/bin/pip install --ignore-installed . 
	# Run the Python tests
	@echo PW: ${PWD}
	${VENV_DIR}/bin/python3 ${LIBOQS_DIR}-python-src/tests/test_kem.py
	${VENV_DIR}/bin/python3 ${LIBOQS_DIR}-python-src/tests/test_sig.py

# MLDSA65 certificate test
test_openssl_cert_mldsa65: #build
	@WORKDIR=${PWD}/${OPENSSL_TEST_DIR}/mldsa65 && \
	rm -rf $$WORKDIR && mkdir -p $$WORKDIR && cd $$WORKDIR && \
#Generate a mldsa65 CA key pair and self-signed certificate \
	$(TEST_OPENSSL) req -x509 -new -newkey mldsa65 -keyout mldsa65_CA.key -out mldsa65_CA.crt -nodes -subj "/CN=test CA" -days 365 ${PROVIDER_STRING} && \
#Generate a mldsa65 server key pair\
	$(TEST_OPENSSL) genpkey -algorithm mldsa65 -out mldsa65_srv.key ${PROVIDER_STRING} && \
#Generate a mldsa65 server certificate signing request \
	$(TEST_OPENSSL) req -new -newkey mldsa65 -keyout mldsa65_srv.key -out mldsa65_srv.csr -nodes -subj "/CN=test server" ${PROVIDER_STRING} && \
#Sign the server certificate with the CA key \
	$(TEST_OPENSSL) x509 -req -in mldsa65_srv.csr -out mldsa65_srv.crt -CA mldsa65_CA.crt -CAkey mldsa65_CA.key -CAcreateserial -days 365 ${PROVIDER_STRING} &&\
#Verify the server certificate \
	$(TEST_OPENSSL) verify ${PROVIDER_STRING} -CAfile $$WORKDIR/mldsa65_CA.crt $$WORKDIR/mldsa65_srv.crt && \
	if [ "$$?" -ne 0 ]; then echo "mldsa65 test failed"; exit 1; else echo "mldsa65 test passed"; fi

# MLDSA87 certificate test
test_openssl_cert_mldsa87: #build
	@WORKDIR=${PWD}/${OPENSSL_TEST_DIR}/mldsa87 && \
	rm -rf $$WORKDIR && mkdir -p $$WORKDIR && cd $$WORKDIR && \
#Generate a mldsa87 CA key pair and self-signed certificate \
	$(TEST_OPENSSL) req -x509 -new -newkey mldsa87 -keyout mldsa87_CA.key -out mldsa87_CA.crt -nodes -subj "/CN=test CA" -days 365 ${PROVIDER_STRING} && \
#Generate a mldsa87 server key pair\
	$(TEST_OPENSSL) genpkey -algorithm mldsa87 -out mldsa87_srv.key ${PROVIDER_STRING} && \
#Generate a mldsa87 server certificate signing request \
	$(TEST_OPENSSL) req -new -newkey mldsa87 -keyout mldsa87_srv.key -out mldsa87_srv.csr -nodes -subj "/CN=test server" ${PROVIDER_STRING} && \
#Sign the server certificate with the CA key \
	$(TEST_OPENSSL) x509 -req -in mldsa87_srv.csr -out mldsa87_srv.crt -CA mldsa87_CA.crt -CAkey mldsa87_CA.key -CAcreateserial -days 365 ${PROVIDER_STRING} &&\
#Verify the server certificate \
	$(TEST_OPENSSL) verify ${PROVIDER_STRING} -CAfile $$WORKDIR/mldsa87_CA.crt $$WORKDIR/mldsa87_srv.crt && \
	if [ "$$?" -ne 0 ]; then echo "mldsa87 test failed"; exit 1; else echo "mldsa87 test passed"; fi

# Generic MLDSA signature test
test_openssl_sign_mldsa65: build
	@WORKDIR=${PWD}/${OPENSSL_TEST_DIR}/mldsa65 && \
	rm -rf $$WORKDIR && mkdir -p $$WORKDIR && cd $$WORKDIR && \
#Generate a mldsa65 server key pair\
	$(TEST_OPENSSL) genpkey -algorithm mldsa65 -out mldsa65_sig.key ${PROVIDER_STRING} && \
#Extract the public key \
	$(TEST_OPENSSL) pkey -in mldsa65_sig.key -pubout -out mldsa65_sig.pub ${PROVIDER_STRING} && \
#sign a message using the server private key \
	echo "Secret message" > message.txt && \
	$(TEST_OPENSSL) dgst ${PROVIDER_STRING} -sign mldsa65_sig.key -out sign.bin -sha256 message.txt  &&\
#verify the signature using the server public key \
	$(TEST_OPENSSL) dgst ${PROVIDER_STRING} -verify mldsa65_sig.pub -signature sign.bin -sha256 message.txt && \
	if [ "$$?" -ne 0 ]; then echo "mldsa65 sign test failed"; exit 1; else echo "mldsa65 sign test passed"; fi

#MLKEM1024 key exchange test with message encryption
test_openssl_mlkem1024: build
	@mkdir -p ${OPENSSL_TEST_DIR}/mlkem1024 && cd ${OPENSSL_TEST_DIR}/mlkem1024 && \
#Generate a mlkem1024 key \
	$(TEST_OPENSSL) genpkey -algorithm mlkem1024 -out mlkem1024_srv.key ${PROVIDER_STRING} && \
#Extract the public key \
	$(TEST_OPENSSL) pkey -in mlkem1024_srv.key -pubout -out mlkem1024_srv.pub ${PROVIDER_STRING} && \
#Generate a Secret Key ane encapsulate it using the public key \
	$(TEST_OPENSSL) pkeyutl -encap -inkey mlkem1024_srv.pub -pubin -out mlkem1024_encap.bin -secret secret.bin ${PROVIDER_STRING} && \
#Encrypt a message using the generated secret key \
	echo "Secret message" > message.txt && \
	$(TEST_OPENSSL) enc -e -in message.txt -out enc_message.bin -kfile secret.bin ${PROVIDER_STRING} && \
#reciver extracts the secret key from the encapsulated key using the private key \
	$(TEST_OPENSSL) pkeyutl -decap -inkey mlkem1024_srv.key -in mlkem1024_encap.bin -out recover_secret.bin ${PROVIDER_STRING} && \
#Decrypt the message using the recovered secret key \
	$(TEST_OPENSSL) enc -d -in enc_message.bin -out dec_message.txt -kfile recover_secret.bin ${PROVIDER_STRING} && \
#Check if the decrypted message is the same as the original message. error exit code if not \
	if [ "$$(cat message.txt)" != "$$(cat dec_message.txt)" ]; then exit 1; else echo "echo MLKEM1024 key exchange test passed"; fi

test: test_provider test_python test_openssl_cert_mldsa65 test_openssl_sign_mldsa65 test_openssl_mlkem1024

clean:
	@echo "Cleaning up..."
	rm -rf liboqs liboqs-provider liboqs-provider-src liboqs-python-src liboqs-src openssl openssl-src ${VENV_DIR} ${OPENSSL_TEST_DIR}
