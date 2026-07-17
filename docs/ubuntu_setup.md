# Ubuntu 22.04 Setup — Docker and VS Code

Goal: run the whole lab on Ubuntu 22.04. ROS2 runs inside Docker; Gazebo and RViz
display through your X server. **No native ROS2 installation is required for the
main path.**

## 1. Install Docker Engine + Compose Plugin

```bash
# Remove old versions if any
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Install from Docker's official repository
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

## 2. Run Docker Without sudo

```bash
sudo usermod -aG docker $USER
# Log out and back in (or run: newgrp docker), then verify:
docker run --rm hello-world
docker compose version
```

## 3. Install VS Code

Install VS Code (deb package or snap), then the **Dev Containers** extension.

## 4. Clone and Verify

```bash
cd ~
git clone https://github.com/LearnRoboticsWROS-Lab/industrial_ros2_manipulation_lab.git
cd industrial_ros2_manipulation_lab
./scripts/lab doctor
```

## 5. GUI Notes (X11)

The compose file mounts `/tmp/.X11-unix` and passes `DISPLAY`. If Gazebo/RViz
windows do not open, allow local containers to use your X server:

```bash
xhost +local:
```

(Re-run after reboot, or add it to your shell profile. See
[docker_troubleshooting.md](docker_troubleshooting.md) for Wayland notes.)

## 6. Optional: NVIDIA GPU Acceleration

Only needed if Gazebo feels slow. Install `nvidia-container-toolkit`, then enable
the commented GPU section in `docker/compose.yaml`. The lab is designed to work
with CPU rendering too.

## Known Ubuntu-Specific Limits

- On Wayland sessions, X11 forwarding works through XWayland; if you hit blank windows, try a `Ubuntu on Xorg` session from the login screen.
- First `lab build` downloads a multi-GB base image.
