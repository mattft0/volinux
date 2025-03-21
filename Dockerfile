FROM ubuntu:20.04

# Arguments passés par le script Bash
ARG FILE_NAME
ARG KERNEL_VERSION
ARG DEBIAN_FRONTEND=noninteractive

# Mise à jour et installation des outils nécessaires
RUN apt-get update && apt-get install -y \
    build-essential dwarfdump git zip wget unzip \
    flex bison libssl-dev libelf-dev bc python3 python3-pip binutils

# Affichage pour debug
RUN echo "Kernel version: ${KERNEL_VERSION}"

# Installation des headers et de l'image du noyau (pour System.map)
RUN apt-get update && \
    apt-get install -y linux-headers-${KERNEL_VERSION} linux-image-${KERNEL_VERSION} || \
    (echo "Headers or image not found in repositories, attempting manual download..." && \
    wget -q "http://archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-headers-${KERNEL_VERSION}_all.deb" -O /tmp/headers_all.deb && \
    wget -q "http://archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-headers-${KERNEL_VERSION}-generic_${KERNEL_VERSION}-generic_amd64.deb" && \
    wget -q "http://archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-image-${KERNEL_VERSION}-generic_${KERNEL_VERSION}-generic_amd64.deb" && \
    dpkg -i /tmp/headers_all.deb /tmp/headers.deb /tmp/image.deb || apt-get install -f -y) || \
    echo "Headers or image ${KERNEL_VERSION} unavailable, profile creation may fail."

# Mise à jour de pip
RUN python3 -m pip install --upgrade pip

# Installation de Volatility 3
RUN pip3 install volatility2 --break-system-packages

# Clonage du dépôt et compilation avec symboles de débogage
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility.git && \
    cd volatility/tools/linux && \
    echo 'MODULE_LICENSE("GPL");' >> module.c && \
    make -C /lib/modules/${KERNEL_VERSION}/build CFLAGS_MODULE="-g" M=$(pwd) modules && \
    objcopy --only-keep-debug module.ko module.dwarf || echo "Failed to extract DWARF data"

# Création du profil Volatility
RUN zip /VolatilityProfile.zip volatility/tools/linux/module.dwarf /boot/System.map-${KERNEL_VERSION} || echo "Profile creation failed."

# Vérification
RUN unzip -l /VolatilityProfile.zip || echo "Profile zip not created."

RUN mv /VolatilityProfile.zip /volatility/volatility/plugins/olverlays/linux/

# Création du répertoire de travail
WORKDIR /analysis

# Copie du dump mémoire dans le conteneur
COPY ${FILE_NAME} /analysis/memory.dmp

# Commande par défaut pour lancer Volatility
CMD ["python3", "/volatility/vol.py", "-f", "/analysis/memory.dmp", "--plugins=/volatility/volatility/plugins/olverlays/linux/VolatilityProfile.zip", "linux_pslist"]

