FROM debian:12

# Définition des arguments pour les variables
ARG FILE_NAME
ARG KERNEL_VERSION

# Mise à jour du système et installation des outils nécessaires
RUN apt update && apt upgrade -y
RUN apt install -y build-essential dwarfdump git zip wget

# Utilisation de la variable KERNEL_VERSION
RUN echo ${KERNEL_VERSION}

# Téléchargement et installation des paquets du noyau
RUN wget https://kernel.ubuntu.com/~kernel-ppa/mainline/v${KERNEL_VERSION}/linux-headers-${KERNEL_VERSION}-generic_${KERNEL_VERSION}_amd64.deb && \
    wget https://kernel.ubuntu.com/~kernel-ppa/mainline/v${KERNEL_VERSION}/linux-image-${KERNEL_VERSION}-generic_${KERNEL_VERSION}_amd64.deb && \
    dpkg -i linux-headers-${KERNEL_VERSION}-generic_${KERNEL_VERSION}_amd64.deb && \
    dpkg -i linux-image-${KERNEL_VERSION}-generic_${KERNEL_VERSION}_amd64.deb

RUN apt install -y linux-headers-${KERNEL_VERSION}-generic linux-image-${KERNEL_VERSION}-generic

# Vérification des fichiers du noyau
RUN ls -la /lib/modules/${KERNEL_VERSION}/ && ls -la /boot/

# Clonage de Volatility et modification du fichier module.c
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && \
    echo 'MODULE_LICENSE("GPL");' >> volatility/tools/linux/module.c && \
    cd volatility/tools/linux && \
    make -C /lib/modules/${KERNEL_VERSION}/build M=$(pwd) modules

# Vérification de la génération des fichiers
RUN ls -la /volatility/tools/linux/ && ls -la /boot/

# Création du profil Volatility
RUN zip VolatilityProfile.zip /volatility/tools/linux/module.dwarf /boot/System.map-${KERNEL_VERSION}

# Déplacement du profil généré vers le répertoire Volatility
RUN mkdir -p /usr/lib/python2.7/dist-packages/volatility/plugins/linux/ && \
    mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/

# Vérification des fichiers du profil créé
RUN unzip -l /usr/lib/python2.7/dist-packages/volatility/plugins/linux/VolatilityProfile.zip