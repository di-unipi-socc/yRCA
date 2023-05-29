FROM ubuntu:18.04

# Refresh apt-get
RUN apt update -qq

# Install SWI Prolog  
RUN apt update -qq
RUN apt install swi-prolog -y

# Install Python and PIP (v3.8)
RUN apt update --fix-missing && apt install python3.8 -y && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
RUN apt install python3-pip -y && python -m pip install --upgrade pip
# Install Python libraries
RUN pip3 install -q pyyaml
RUN pip3 install -q pyswip

# Clone yRCA
RUN apt install git -y  
RUN git clone https://github.com/di-unipi-socc/yRCA.git

# Run example
WORKDIR yRCA
CMD python3.8 yrca.py data/examples/sock-echo/shipping-fail/event-edgeRouter.log data/examples/sock-echo/shipping-fail/all.log data/templates/chaos-echo.yml
# TODO: Add script running all examples!
