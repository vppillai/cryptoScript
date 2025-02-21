#!/bin/bash
set -e

# Script to pull a specified version of the OQS library and generate teh library, python wrapper and OpenSSL provider connections for it



#ROOT_DIR=$PWD
CMAKE_BUILD_PARALLEL_LEVEL=16
CROSS_COMPILE=""

# This is a dirty workaround to get the correct version of GCC on the build server 02. 
if [ $(hostname -s) == "bby-cbu-swbuild02" ]; then
    export PATH=/opt/rh/devtoolset-10/root/usr/bin:$PATH
fi



#------------------------------------------build Openssl-----------------------------------------
# Pull the OpenSSL library
cd $ROOT_DIR
if [ ! -d "openssl-src" ]; then
    echo "Cloning openssl"
    git clone --depth 1 --branch openssl-$OPENSSL_VERSION https://github.com/openssl/openssl.git $ROOT_DIR/openssl-src
    cd $ROOT_DIR/openssl-src
    ./Configure --prefix=$ROOT_DIR/openssl --openssldir=$ROOT_DIR/openssl  no-tests no-docs no-demos 
else
    echo "Openssl exists. "
    cd $ROOT_DIR/openssl-src
fi

# build openssl
make build_sw -j$CMAKE_BUILD_PARALLEL_LEVEL
make install

#------------------------------------------build liboqs------------------------------------------
# based on https://github.com/open-quantum-safe/liboqs/blob/main/README.md#linux-and-mac
# Pull the OQS library
cd $ROOT_DIR
if [ ! -d "${LIBOQS_DIR}-src" ]; then
    echo "Cloning liboqs"
    git clone --depth 1 --branch $LIBOQS_VERSION https://github.com/open-quantum-safe/liboqs.git ${LIBOQS_DIR}-src 
    cd ${LIBOQS_DIR}-src
    git checkout $LIBOQS_VERSION
else
    echo "Liboqs exists. "
    cd ${LIBOQS_DIR}-src
fi

# build liboqs
if [ ! -d "build" ]; then
    mkdir -p build && cd build
    cmake -GNinja .. -DOPENSSL_ROOT_DIR=$ROOT_DIR/openssl -DCMAKE_INSTALL_PREFIX=$ROOT_DIR/$LIBOQS_DIR -DBUILD_SHARED_LIBS=ON -DOQS_DIST_BUILD=ON \
                  -DOQS_ENABLE_KEM_BIKE=ON -DOQS_ENABLE_KEM_FRODOKEM=ON -DOQS_ENABLE_KEM_HQC=ON -DOQS_ENABLE_KEM_KYBER=ON -DOQS_ENABLE_KEM_NTRUPRIME=ON \
                  -DOQS_ENABLE_ML_KEM=ON -DOQS_ENABLE_KEM_CLASSIC_MCELIECE=ON -DOQS_ENABLE_SIG_DILITHIUM=ON -DOQS_ENABLE_ML_DSA=ON \
                  -DOQS_ENABLE_SIG_FALCON=ON -DOQS_ENABLE_SIG_SPHINCS=ON -DOQS_ENABLE_SIG_MAYO=ON -DOQS_ENABLE_SIG_CROSS=ON -DOQS_ENABLE_SIG_STFL_XMSS=ON \
                  -DOQS_ENABLE_SIG_STFL_LMS=ON
                  #-DOQS_BUILD_ONLY_LIB=ON 
else
    cd build
fi
ninja
ninja install


#------------------------------------------build oqs-provider------------------------------------------
#based on https://github.com/open-quantum-safe/oqs-provider/blob/main/CONFIGURE.md
cd $ROOT_DIR
if [ ! -d "${LIBOQS_DIR}-provider-src" ]; then
    echo "Cloning oqs-provider"
    git clone --depth 1 --branch $OQS_PROVIDER_VERSION https://github.com/open-quantum-safe/oqs-provider.git ${LIBOQS_DIR}-provider-src
    cd ${LIBOQS_DIR}-provider-src
    git checkout $OQS_PROVIDER_VERSION
else
    echo "oqs-provider exists. "
    cd ${LIBOQS_DIR}-provider-src
    #git fetch
fi


liboqs_DIR=$ROOT_DIR/$LIBOQS_DIR cmake -S . -B _build -DOQS_KEM_ENCODERS=ON -DCMAKE_INSTALL_PREFIX=$ROOT_DIR/${LIBOQS_DIR}-provider && \
cmake --build _build && \
#cmake --install _build --prefix $ROOT_DIR/${LIBOQS_DIR}-provider && \
mkdir -p $ROOT_DIR/${LIBOQS_DIR}-provider && \
cp -f _build/lib/oqsprovider.so $ROOT_DIR/${LIBOQS_DIR}-provider

#------------------------------------------build oqs-python------------------------------------------
cd $ROOT_DIR
if [ ! -d "${LIBOQS_DIR}-python-src" ]; then
    git clone --depth 1 --branch $OQS_PYTHON_VERSION https://github.com/open-quantum-safe/liboqs-python.git ${LIBOQS_DIR}-python-src
    cd ${LIBOQS_DIR}-python-src
else
    cd ${LIBOQS_DIR}-python-src
    git clean -xfd
    git reset --hard
    git fetch
fi

git checkout $OQS_PYTHON_VERSION
