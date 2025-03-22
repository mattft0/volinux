#!/bin/bash

# Vérification des arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <memory_dump>"
    exit 1
fi

FILE_NAME="$1"
KERNEL_VERSION=$(strings "${FILE_NAME}" | grep -i 'Linux version' | grep -v 'of' | sed -E 's/.*Linux version ([^ ]+).*/\1/' | head -n 1)

# Vérification si la version du noyau a été trouvée
if [ -z "$KERNEL_VERSION" ]; then
    echo "Erreur : Impossible de détecter la version du noyau."
    exit 1
fi

echo "Détection du noyau : ${KERNEL_VERSION}"

# Nettoyage du système Docker
echo "Nettoyage du système Docker..."
docker system prune -f

# Lancement de Docker Compose avec les arguments
docker-compose build --no-cache --build-arg FILE_NAME="${FILE_NAME}" --build-arg KERNEL_VERSION="${KERNEL_VERSION}"
