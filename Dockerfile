# FROM debian:12

# RUN apt update && apt upgrade -y
# RUN apt install ${LINUX_IMAGE} && apt install ${LINUX_HEADERS} -y
# RUN apt install build-essential dwarfdump git -y
# RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && cd volatility/tools/linux && make
# RUN zip VolatilityProfile.zip /home/volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)
# RUN mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/


FROM debian:12

# Mise à jour du système et installation des outils nécessaires
RUN apt update && apt upgrade -y
RUN apt install -y build-essential dwarfdump git zip

# Installation des headers du noyau
RUN apt install -y linux-headers-$(uname -r)

# Vérification des headers
RUN ls -la /lib/modules/$(uname -r)/

# Clonage de Volatility et modification du fichier module.c
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && \
    echo 'MODULE_LICENSE("GPL");' >> volatility/tools/linux/module.c && \
    cd volatility/tools/linux && \
    make -C /lib/modules/$(uname -r)/build M=$(pwd) modules

# Création du profil Volatility
RUN zip VolatilityProfile.zip /volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)

# Déplacement du profil généré vers le répertoire Volatility
RUN mkdir -p /usr/lib/python2.7/dist-packages/volatility/plugins/linux/ && \
    mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/

