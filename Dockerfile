FROM debian:12

# Définition des arguments
ARG FILE_NAME
ARG KERNEL_VERSION

# Mise à jour et installation des outils nécessaires
RUN apt update && apt install -y \
    build-essential dwarfdump git zip wget \
    unzip

# Affichage de la version du noyau pour debug
RUN echo "Kernel version: ${KERNEL_VERSION}"

# Téléchargement des paquets du noyau
RUN apt-get update && \
    apt-cache search linux-image | grep "${KERNEL_VERSION}" && \
    apt install -y linux-image-${KERNEL_VERSION}-generic linux-headers-${KERNEL_VERSION}-generic || \
    (echo "Kernel not found in repositories, attempting to download and install manually..." && \
    wget -q "https://snapshot.debian.org/archive/debian-security/20220307T130529Z/pool/updates/main/l/linux/linux-image-${KERNEL_VERSION}-dbg_5.10.92-2_amd64.deb" -O /tmp/linux-image.deb && \
    wget -q "https://snapshot.debian.org/archive/debian-security/20220307T130529Z/pool/updates/main/l/linux/linux-headers-${KERNEL_VERSION}_5.10.92-2_amd64.deb" -O /tmp/linux-headers.deb && \
    dpkg -i /tmp/linux-image.deb /tmp/linux-headers.deb || apt install -f -y) || \
    (echo "Kernel ${KERNEL_VERSION} not found, attempting to compile from source..." && \
    wget https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-${KERNEL_VERSION}.tar.xz && \
    tar -xf linux-${KERNEL_VERSION}.tar.xz && cd linux-${KERNEL_VERSION} && \
    make defconfig && make -j$(nproc) && make modules_install && make install)

# Vérification des fichiers du noyau
RUN ls -la /lib/modules/${KERNEL_VERSION}/ && ls -la /boot/

# Clonage de Volatility et modification du fichier module.c
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility.git && \
    echo 'MODULE_LICENSE("GPL");' >> volatility/tools/linux/module.c && \
    cd volatility/tools/linux && \
    make -C /lib/modules/${KERNEL_VERSION}/build M=$(pwd) modules

# Vérification de la génération des fichiers
RUN ls -la /volatility/tools/linux/ && ls -la /boot/

# Création du profil Volatility
RUN zip VolatilityProfile.zip /volatility/tools/linux/module.dwarf /boot/System.map-${KERNEL_VERSION}

# Déplacement du profil généré vers Volatility
RUN mkdir -p /usr/lib/python2.7/dist-packages/volatility/plugins/linux/ && \
    mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/

# Vérification finale
RUN unzip -l /usr/lib/python2.7/dist-packages/volatility/plugins/linux/VolatilityProfile.zip