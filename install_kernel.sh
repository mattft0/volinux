#!/bin/bash

# Vérifier que le fichier System.map existe
if [ ! -f "$1" ]; then
    echo "Le fichier $1 n'existe pas !"
    exit 1
fi

# Extraire la version du noyau à partir du fichier System.map
KERNEL_VERSION=$(strings "$1" | grep -i 'Linux version' | grep -v 'of' | sed -E 's/.*Linux version ([^ ]+).*/\1/' | head -n 1)

if [ -z "$KERNEL_VERSION" ]; then
    echo "Impossible d'extraire la version du noyau depuis $1."
    exit 1
fi

echo "Version du noyau extraite : $KERNEL_VERSION"

# Installer les headers et l'image du noyau correspondant
echo "Installation des headers et de l'image du noyau $KERNEL_VERSION..."
apt update && apt install -y linux-headers-${KERNEL_VERSION} linux-image-${KERNEL_VERSION}

# Vérification de l'installation des fichiers du noyau
ls -la /lib/modules/${KERNEL_VERSION}/ && ls -la /boot/

# Cloner et compiler Volatility
cd /volatility/tools/linux || exit 1
make -C /lib/modules/$(uname -r)/build M=$(pwd) modules

# Vérification des fichiers générés
ls -la /volatility/tools/linux/ && ls -la /boot/
