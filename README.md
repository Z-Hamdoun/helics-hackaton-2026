# Hackaton HéliCS 2026

## Guides:
- Utilisation d'une RPI 4 (SSH, Mettre une addr IP par défaut, bash)
- Branchements RPI - FC
- Mavlink et pymavlink
- RPI Camera (Calibration, detection AruCo)
- Git et GitLab
- Installation des dépendences


## Simulation

```sh
gz sim -v4 -r ~/gz_ws/src/ardupilot_gazebo/worlds/hackathon.sdf
```

```sh
~/ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console -I0 --sysid=1 --use-dir=$HOME/gz_ws/ardupilot_output/iris_with_gimbal -A '--serial1=udpclient:127.0.0.1:14554'
```
