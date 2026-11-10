# EKD Jupiter Setup

This repository contains the EKD Catkin workspace and its bundled SafeZone YOLOv5 tree. The supported baseline is Ubuntu 20.04 with ROS Noetic.

## Fresh machine

Install ROS Noetic and Git LFS first. Git LFS is required for the GUI video asset:

```bash
sudo apt-get install git-lfs
git lfs install
git clone https://github.com/hetawk/ekd_jupiter.git ~/ekd_catkin_ws
cd ~/ekd_catkin_ws
git lfs pull
```

Install ROS package dependencies, then build:

```bash
sudo rosdep init  # only if rosdep has not been initialized on this machine
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro noetic -r -y
source /opt/ros/noetic/setup.bash
catkin_make
```

Create a machine-local environment file. Do not copy credentials into tracked files or share `.env`:

```bash
cp .env.example .env
chmod 600 .env
nano .env
source setup_ekd.bash
```

Enter commands from `COMMANDS.md` after sourcing `setup_ekd.bash` in each ROS terminal. Robot cameras, speech hardware/SDKs, OpenVINO, GPU/CUDA, and API credentials are optional per-experiment requirements and must be installed/configured for the workflows that use them.

## Repository layout

- `src/`: ROS packages; embedded repository histories were removed from the published tree, while their source files remain.
- `ekd_yolov5/`: SafeZone model source, dataset, analysis artifacts, and selected checkpoint.
- `.env.example`: variable names only; each machine keeps its own ignored `.env`.
- `.gitattributes`: sends the required 104 MB GUI video through Git LFS.