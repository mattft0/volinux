FROM debian:12

# Mise à jour et installation des outils nécessaires
RUN apt update && apt upgrade -y
RUN apt install -y build-essential dwarfdump git zip

# Installation des headers et du package de débogage du noyau
RUN apt install -y linux-headers-$(uname -r) linux-image-$(uname -r)

# Vérification de la présence de vmlinux
RUN find /usr/lib/debug/boot -name "vmlinux*" && find /boot -name "vmlinux*"

# Clonage de Volatility et ajout de la licence au module.c
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && \
    echo 'MODULE_LICENSE("GPL");' >> volatility/tools/linux/module.c && \
    cd volatility/tools/linux && \
    make -C /lib/modules/$(uname -r)/build M=$(pwd) CONFIG_DEBUG_INFO=y modules

# Vérification de la génération des fichiers
RUN ls -la /volatility/tools/linux/

# Création du profil Volatility
RUN zip VolatilityProfile.zip /volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)

# Déplacement du profil généré
RUN mkdir -p /usr/lib/python2.7/dist-packages/volatility/plugins/linux/ && \
    mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/