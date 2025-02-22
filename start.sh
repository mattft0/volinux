#!/bin/bash

# Vérification des arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <memory_dump>"
    exit 1
fi

export FILE_NAME=$1
export KERNEL_VERSION=$(strings "${FILE_NAME}" | grep -i 'Linux version' | grep -v 'of' | sed -E 's/.*Linux version ([^ ]+).*/\1/' | head -n 1)

# Vérification si la version du noyau a été trouvée
if [ -z "$KERNEL_VERSION" ]; then
    echo "Erreur : Impossible de détecter la version du noyau."
    exit 1
fi

export LINUX_IMAGE="linux-image-${KERNEL_VERSION}"
export LINUX_HEADERS="linux-headers-${KERNEL_VERSION}"

echo "Détection du noyau : ${KERNEL_VERSION}"
docker-compose build --no-cache
