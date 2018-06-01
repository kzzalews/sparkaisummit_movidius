FROM  ubuntu:bionic

RUN apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install lightdm -y
RUN apt-get install -y  libprotobuf-dev libleveldb-dev libsnappy-dev libopencv-dev libhdf5-serial-dev protobuf-compiler
RUN apt-get install -y --no-install-recommends libboost-all-dev
RUN apt-get install -y bash git make wget sudo python3-pip libopencv-dev python-opencv cmake caffe-cuda
RUN pip3 install -U pip
RUN python3 -m pip install --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-0.12.0-py3-none-any.whl
RUN python3 -m pip install grpcio
RUN python3 -m pip install grpcio-tools
RUN python3 -m pip install opencv-python
RUN python3 -m pip install opencv-contrib-python

RUN mkdir -p /workspace
WORKDIR /workspace
RUN git clone https://github.com/movidius/ncsdk.git && cd ncsdk && git checkout v1.12.00.01
WORKDIR /workspace/ncsdk
RUN chmod +x *.sh
RUN sync
RUN sed -i "39i sed -i '630s/^/#/' /opt/movidius/NCSDK/install-ncsdk.sh && sed -i '631s/^/#/' /opt/movidius/NCSDK/install-ncsdk.sh" ./install.sh
RUN USER=root PATH=$PATH:/bin:/usr/bin ./install.sh

COPY ncs_service /opt/ncs_service
WORKDIR /opt/ncs_service
ENTRYPOINT [ "/opt/ncs_service/ncs_service.py" ]
