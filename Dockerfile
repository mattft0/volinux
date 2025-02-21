# FROM debian:12

# RUN apt update && apt upgrade -y
# RUN apt install ${LINUX_IMAGE} && apt install ${LINUX_HEADERS} -y
# RUN apt install build-essential dwarfdump git -y
# RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && cd volatility/tools/linux && make
# RUN zip VolatilityProfile.zip /home/volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)
# RUN mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/


FROM debian:12

RUN apt update && apt install -y linux-headers-$(uname -r)

RUN apt update && apt upgrade -y
RUN apt install -y build-essential dwarfdump git zip

RUN git clone --depth=1 https://github.com/volatilityfoundation/volatility && \
    cd volatility/tools/linux && \
    ls -la && \
    ls -la /lib/modules/$(uname -r)/ && \
    make

RUN test -f /volatility/tools/linux/module.dwarf && \
    test -f /boot/System.map-$(uname -r) && \
    zip VolatilityProfile.zip /volatility/tools/linux/module.dwarf /boot/System.map-$(uname -r)

RUN mkdir -p /usr/lib/python2.7/dist-packages/volatility/plugins/linux/ && \
    mv VolatilityProfile.zip /usr/lib/python2.7/dist-packages/volatility/plugins/linux/
