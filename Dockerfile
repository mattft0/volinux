FROM debian:12

RUN apt install ${KERNEL_VERSION}
RUN apt update && apt upgrade -y
RUN apt install build-essential dwarfdump git -y
RUN ls /home/ \
    git clone --depth=1 https://github.com/volatilityfoundation/volatility \
    cd volatility/tools/linux \
    make
RUN zip VolatilityProfile.zip /home/volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)
RUN mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/