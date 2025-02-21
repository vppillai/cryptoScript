# Introduction

This directory includes scripts and tools to generate the liboqs library, providers and python wrappers from source. Used to create a local test environment with specific version combinations.

## Current versions

|Tool|Version|
|----|-------|
|[liboqs](https://github.com/open-quantum-safe/liboqs.git)             | `0.12.0`|
|[oqs provider](https://github.com/open-quantum-safe/oqs-provider.git) | `0.8.0` |
|[oqs python](https://github.com/open-quantum-safe/liboqs-python.git)  | `0.12.0`|
|[openssl](https://github.com/openssl/openssl.git)                     | `3.4.1` |


## Usage

- `make build` - download and generate all the liboqs components
- `make clean` - remove all the generated files
- `make test` - run the tests
    - This includes the tests that are released as part of the liboqs component source packages as well as additional tests to ensure the build components are working correctly.

## Installing the python wrapper

Once the build is complete, the python wrapper can be installed into any venv using the following command:

```
cd liboqs-python-src
${VENV_DIR}/bin/pip install --ignore-installed . 
```

Where `${VENV_DIR}` is the path to the virtual environment where the python wrapper should be installed.
