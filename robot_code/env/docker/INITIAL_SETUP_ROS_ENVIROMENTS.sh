#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo pip install --upgrade pip

# Installing pip packages
pip3 install -r src/powder_grinding/requirements.txt

# Updating ROSDEP and installing dependencies
rosdep update
rm -rf src/third_party
rm -rf src/powder_grinding/third_party
vcs import src < src/powder_grinding/.rosinstall
rosdep install --from-paths src --ignore-src --rosdistro=$ROS_DISTRO -y

# Build
rm -rf build devel
catkin build

# Update enviromental veriables
source /opt/ros/$ROS_DISTRO/setup.bash
source devel/setup.bash


# Copy description files to DENSO ROS package
echo "It is fine if cobotta's setup_files does not exist even if you run this script more than once."
echo "If you can't use roslauch, please run the 'source devel/setup.bash' on the terminal."