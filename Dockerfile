FROM debian:12

# Mise à jour du système et installation des outils nécessaires
RUN apt update && apt upgrade -y
RUN apt install -y build-essential dwarfdump git zip

# Installation des headers du noyau et du fichier System.map
RUN apt install -y linux-headers-$(uname -r) linux-image-$(uname -r)

# Vérification des fichiers du noyau
RUN ls -la /lib/modules/$(uname -r)/ && ls -la /boot/

# Clonage de Volatility et modification du fichier module.c
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && \
    echo 'MODULE_LICENSE("GPL");' >> volatility/tools/linux/module.c && \
    cd volatility/tools/linux && \
    make -C /lib/modules/$(uname -r)/build M=$(pwd) modules

# Vérification de la génération des fichiers
RUN ls -la /volatility/tools/linux/ && ls -la /boot/

# Création du profil Volatility
RUN zip VolatilityProfile.zip /volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)

# Déplacement du profil généré vers le répertoire Volatility
RUN mkdir -p /usr/lib/python2.7/dist-packages/volatility/plugins/linux/ && \
    mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/
