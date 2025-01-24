export FILE_NAME=$1
export KERNEL_VERSION=$(strings ${FILE_NAME} | grep -i 'Linux version' | grep -v 'of' | sed -E 's/.*Linux version ([^ ]+).*/\1/' | head -n 1)

export LINUX_IMAGE="linux-image-"${KERNEL_VERSION}
export LINUX_HEADERS="linux-headers-"${KERNEL_VERSION}

docker-compose build --no-cache
