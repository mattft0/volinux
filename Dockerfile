FROM debian:12

# Mise à jour du système et installation des outils nécessaires
RUN apt update && apt upgrade -y
RUN apt install -y build-essential dwarfdump git zip wget

# Installation des dépendances pour Volatility
RUN apt install -y python2.7 python2.7-dev

# Clonage de Volatility
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && \
    echo 'MODULE_LICENSE("GPL");' >> volatility/tools/linux/module.c

# Copier le script shell d'installation dans le conteneur
COPY install_kernel.sh /usr/local/bin/install_kernel.sh
RUN chmod +x /usr/local/bin/install_kernel.sh

# Utiliser le script d'installation du noyau avec le fichier System.map
RUN /usr/local/bin/install_kernel.sh /path/to/dump/System.map

# Vérification des fichiers générés
RUN ls -la /lib/modules/ && ls -la /boot/

# Créer le profil Volatility
RUN zip VolatilityProfile.zip /volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)

# Déplacer le profil Volatility vers le répertoire approprié
RUN mkdir -p /usr/lib/python2.7/dist-packages/volatility/plugins/linux/ && \
    mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/

# Vérification du profil généré
RUN unzip -l /usr/lib/python2.7/dist-packages/volatility/plugins/linux/VolatilityProfile.zip
