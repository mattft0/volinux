FROM debian:12

RUN apt install ${KERNEL_VERSION}
RUN uname -a
RUN ls /home/
RUN apt install build-essential dwarfdump
RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility
RUN cd volatility/tools/linux
RUN make
RUN zip Ubuntu1604.zip volatility/tools/linux/module.dwarf /boot/System.map-4.4.0-72-lowlatency
RUN mv Ubuntu1604.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/