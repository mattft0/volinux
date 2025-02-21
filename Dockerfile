FROM debian:12

RUN apt install ${KERNEL_VERSION}
RUN uname -a
RUN ls /home/
RUN apt update && apt upgrade -y
RUN apt install build-essential dwarfdump git -y
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility
RUN cd volatility/tools/linux
RUN make
RUN zip VolatilityProfile.zip volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)
RUN mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/