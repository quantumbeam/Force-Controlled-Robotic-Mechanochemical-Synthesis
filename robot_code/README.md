### Robotic Powder Grinding Demo
<img src="https://github.com/quantumbeam/Force-Controlled-Robotic-Mechanochemical-Synthesis/blob/main/wiki/grinding_demo.gif?raw=true" alt="UR powder grinding" width="500">

Demo ROS packages for robotic mechanochemistry.
This package can operate both in simulation (fake_joint) and on the actual robot.


#### **Table of Contents**
- [Supported Robots](#supported-robots)
  - [Quick Start Guide](#quick-start-guide)
    - [Setting up Environments of Host PC, Robot, and Docker](#setting-up-environments-of-host-pc-robot-and-docker)
    - [Running Docker Container](#running-docker-container)
    - [Building ROS Packages in Docker Container](#building-ros-packages-in-docker-container)
    - [Demonstration](#demonstration)


## Supported Robots
- UR5e (Universal Robot)


### Quick Start Guide
You can also view the Japanese version of the [README_jp](./README_jp.md).

#### Setting up Environments of Host PC, Robot, and Docker
- [Setup Instructions](./env/docker/README.md)
- [Setup Instructions (Japanese version)](./env/docker/README_jp.md)

#### Running Docker Container
- Runing docker container on terminal: `cd ./env && ./RUN-DOCKER-CONTAINER.sh`
- Launch Terminator and running docker container: `cd ./env && ./LAUNCH-TERMINATOR-TERMINAL.sh`

#### Building ROS Packages in Docker Container
- Execute only once on first `./INITIAL_SETUP_ROS_ENVIROMENTS.sh` in `catkin_ws` in docker conatner.  
- Execute to build `./BUILD_ROS_WORKSPACE.sh` in `catkin_ws` in docker conatner.


#### Demonstration
- We have prepared demo files for launching and performing grinding motions.
- Robot Launch:
   ```
   roslaunch grinding_robot_bringup ur5e_bringup.launch
   ```
  - If you want to use simulation, please launch with sim:=true.
- Launching Grinding Motion:
   ```
   roslaunch grinding_motion_routines ur5e_grinding_demo.launch
   ```
   - Use the command g to prepare for grinding (g=grinding), and then use y to execute the grinding.
   - Use the command G to prepare for powder collection with a spatula (G=gathering), and then use y to execute the powder collection.
- Grinding Parameters Configuration:
   - The configuration settings are located in the config directory within the grinding_motion_routines package.
