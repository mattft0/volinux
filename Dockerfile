FROM ubuntu:20.04

# Arguments passés par le script Bash
ARG FILE_NAME
ARG KERNEL_VERSION
ARG DEBIAN_FRONTEND=noninteractive

# Mise à jour et installation des outils nécessaires
RUN apt-get update && apt-get install -y \
    build-essential dwarfdump git zip wget unzip \
    flex bison libssl-dev libelf-dev bc python2.7 python2.7-dev python3 python3-pip binutils

# Installation des headers et de l'image du noyau (pour System.map)
RUN apt-get update && \
    apt-get install -y linux-headers-${KERNEL_VERSION} linux-image-${KERNEL_VERSION} || \
    (echo "Headers or image not found in repositories, attempting manual download..." && \
    wget -q "http://archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-headers-${KERNEL_VERSION}_all.deb" -O /tmp/headers_all.deb && \
    wget -q "http://archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-headers-${KERNEL_VERSION}-generic_${KERNEL_VERSION}-generic_amd64.deb" && \
    wget -q "http://archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-image-${KERNEL_VERSION}-generic_${KERNEL_VERSION}-generic_amd64.deb" && \
    dpkg -i /tmp/headers_all.deb /tmp/headers.deb /tmp/image.deb || apt-get install -f -y) || \
    echo "Headers or image ${KERNEL_VERSION} unavailable, profile creation may fail."

# Installation de Volatility 2 et création du profil
RUN git clone https://github.com/volatilityfoundation/volatility.git && \
    cd volatility && \
    python2.7 setup.py install && \
    cd tools/linux && \
    echo 'MODULE_LICENSE("GPL");' >> module.c && \
    make -C /lib/modules/${KERNEL_VERSION}/build CFLAGS_MODULE="-g" M=$(pwd) modules && \
    objcopy --only-keep-debug module.ko module.dwarf && \
    zip /VolatilityProfile.zip module.dwarf /boot/System.map-${KERNEL_VERSION} && \
    mkdir -p /volatility/volatility/plugins/overlays/linux/ && \
    mv /VolatilityProfile.zip /volatility/volatility/plugins/overlays/linux/

# Création du répertoire de travail et copie du dump
WORKDIR /analysis
COPY ${FILE_NAME} /analysis/memory.dmp

# Commande par défaut pour lancer Volatility
RUN python2.7 /volatility/vol.py -f /analysis/memory.dmp --profile=/volatility/volatility/plugins/overlays/linux/VolatilityProfile.zip linux_pslist