## Lancer Gazebo

```sh
gz sim -v4 -r ~/gz_ws/src/ardupilot_gazebo/worlds/hackathon.sdf
```

## Lancer ardupilot SITL

```sh
~/ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console -I1 --sysid=2 --use-dir=$HOME/gz_ws/ardupilot_output/drone1 -A '--serial1=udpclient:127.0.0.1:14564'
```
