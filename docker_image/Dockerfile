FROM ubuntu:noble-20260410

# setup timezone
RUN echo 'Etc/UTC' > /etc/timezone && \
    ln -s /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    apt-get update && \
    apt-get install -q -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*

# install packages
RUN apt-get update && apt-get install -q -y --no-install-recommends \
    bash-completion \
    dirmngr \
    gnupg2 \
    curl \
    gedit \
    wget \
    python3-argcomplete \
    python3-flake8 \
    python3-flake8-blind-except \
    python3-flake8-builtins \
    python3-flake8-class-newline \
    python3-flake8-comprehensions \
    python3-flake8-deprecated \
    python3-flake8-docstrings \
    python3-flake8-import-order \
    python3-flake8-quotes \
    python3-pip \
    python3.12-venv \
    python3-pytest-cov \
    python3-pytest-mock \
    python3-pytest-repeat \
    python3-pytest-rerunfailures \
    python3-pytest-runner \
    python3-pytest-timeout \
    build-essential g++ libc6-dev \
    libcap-dev \
    && rm -rf /var/lib/apt/lists/*

# setup keys
RUN set -eux; \
       key='C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654'; \
       export GNUPGHOME="$(mktemp -d)"; \
       gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key"; \
       mkdir -p /usr/share/keyrings; \
       gpg --batch --export "$key" > /usr/share/keyrings/ros2-latest-archive-keyring.gpg; \
       gpgconf --kill all; \
       rm -rf "$GNUPGHOME"

# setup sources.list
RUN echo "deb [ signed-by=/usr/share/keyrings/ros2-latest-archive-keyring.gpg ] http://packages.ros.org/ros2/ubuntu noble main" > /etc/apt/sources.list.d/ros2-latest.list

# setup environment
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# install bootstrap tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git \
    python3-colcon-common-extensions \
    python3-colcon-mixin \
    python3-rosdep \
    python3-setuptools \
    python3-vcstool \
    && rm -rf /var/lib/apt/lists/*

# This is a workaround for pytest not found causing builds to fail
# Following RUN statements tests for regression of https://github.com/ros2/ros2/issues/722
RUN pip3 freeze | grep pytest \
    && python3 -m pytest --version

# bootstrap rosdep
RUN rosdep init \
    && rosdep update

# setup colcon mixin and metadata
RUN colcon mixin add default \
      https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml && \
    colcon mixin update && \
    colcon metadata add default \
      https://raw.githubusercontent.com/colcon/colcon-metadata-repository/master/index.yaml && \
    colcon metadata update

# Install universal repo ubuntu
RUN echo "deb http://archive.ubuntu.com/ubuntu noble universe" >> /etc/apt/sources.list && \
    echo "deb http://archive.ubuntu.com/ubuntu noble-updates universe" >> /etc/apt/sources.list && \
    apt-get update

# Install ROS2
#COPY ./ros2.sources /etc/apt/sources.list.d/
ENV ROS_DISTRO=jazzy

RUN apt install -y ros-dev-tools && apt update
RUN apt upgrade -y 
RUN apt install -y ros-${ROS_DISTRO}-desktop
RUN sudo apt-get install -y ros-${ROS_DISTRO}-ros-gz

RUN git config --global user.name "Docker Image User" 
ENV USER=DOCKER

#RUN rosdep install --from-paths -y ${BNL_WS}/src/ros2_packages/ldlidar_ros2_ws/src && \ 
#    rosdep install --from-paths -y ${BNL_WS}/src/ros2_packages/slam_toolbox

# build source
#RUN colcon \
#    build \
#    --cmake-args \
#      -DSECURITY=ON --no-warn-unused-cli \
#    --symlink-install

ENV BNL_VENV_PATH=/home/${USER}/.BNL_venv/

RUN echo "woop woop"

RUN wget https://raw.githubusercontent.com/Havlia/BNL/refs/heads/main/docker_image/docker_python_venv.bash
RUN bash docker_python_venv.bash
RUN rm docker_python_venv.bash
#RUN chmod u+w /root/.config/Ultralytics

# setup bashrc
RUN cp /etc/skel/.bashrc ~/

# setup entrypoint
COPY ./ros_entrypoint.sh /

RUN apt-get update && apt-get upgrade -y

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]


